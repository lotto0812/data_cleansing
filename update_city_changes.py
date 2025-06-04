import csv
import json
from typing import Dict, Tuple
from datetime import datetime

def convert_japanese_date(date_str: str) -> str:
    """
    和暦の日付を西暦（YYYY-MM-DD形式）に変換
    
    Parameters:
    -----------
    date_str : str
        和暦の日付（例：平成11年4月1日）
    
    Returns:
    --------
    str
        西暦の日付（YYYY-MM-DD形式）
    """
    if not date_str:
        return ""
        
    # 年号変換テーブル
    era_table = {
        "平成": 1989,
        "令和": 2019
    }
    
    try:
        # 年の抽出
        era = "平成" if "平成" in date_str else "令和"
        year_str = date_str[date_str.find(era) + len(era):date_str.find("年")]
        year = int(year_str) + era_table[era] - 1
        
        # 月と日の抽出
        month = int(date_str[date_str.find("年") + 1:date_str.find("月")])
        day = int(date_str[date_str.find("月") + 1:date_str.find("日")])
        
        # YYYY-MM-DD形式に変換
        return f"{year:04d}-{month:02d}-{day:02d}"
    except:
        return ""

def clean_city_name(city_name: str) -> str:
    """
    市区町村名から余分な情報を削除
    
    Parameters:
    -----------
    city_name : str
        市区町村名
    
    Returns:
    --------
    str
        クリーニングされた市区町村名
    """
    if not city_name:
        return ""
        
    # （し）、（ちょう）などの除去
    if "（" in city_name and "）" in city_name:
        pos = city_name.find("（")
        if any(suffix in city_name[pos:] for suffix in ["（し）", "（ちょう）", "（まち）", "（むら）"]):
            city_name = city_name[:pos]
    
    return city_name.strip()

def replace_same_county(old_cities_str: str) -> str:
    """
    '同郡'を適切な郡名に置き換える
    
    Parameters:
    -----------
    old_cities_str : str
        旧市区町村名のリスト（読点区切り文字列）
    
    Returns:
    --------
    str
        '同郡'を置き換えた後の文字列
    """
    if '同郡' not in old_cities_str:
        return old_cities_str
        
    cities = old_cities_str.split('、')
    current_county = None
    
    # 最初に出現する「××郡」を探す
    for city in cities:
        if '郡' in city and '同郡' not in city:
            # 郡名を抽出（括弧の前まで）
            if '（' in city:
                county_part = city[:city.find('（')]
            else:
                county_part = city
            
            if '郡' in county_part:
                current_county = county_part[:county_part.find('郡')]
                break
    
    if current_county is None:
        return old_cities_str
        
    # '同郡'を置き換える
    result = []
    for city in cities:
        if '同郡' in city:
            city = city.replace('同郡', current_county + '郡')
        result.append(city)
    
    return '、'.join(result)

def extract_reading(city_info: str) -> Tuple[str, str]:
    """
    市区町村名から読み仮名を抽出
    
    Parameters:
    -----------
    city_info : str
        市区町村名（読み仮名付き）
    
    Returns:
    --------
    Tuple[str, str]
        (市区町村名, 読み仮名)
    """
    if '（' in city_info and '）' in city_info:
        name = city_info[:city_info.find('（')].strip()
        reading = city_info[city_info.find('（')+1:city_info.find('）')].strip()
        
        # 読み仮名から（し）、（ちょう）などを除去
        reading = clean_city_name(reading)
        
        return name, reading
    else:
        return city_info.strip(), ""

def read_city_changes(csv_file: str) -> Dict[Tuple[str, str], Dict[str, str]]:
    """
    CSVファイルから市区町村合併データを読み込む
    
    Parameters:
    -----------
    csv_file : str
        CSVファイルのパス
    
    Returns:
    --------
    Dict[Tuple[str, str], Dict[str, str]]
        市区町村合併データのマッピング
    """
    city_changes = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        
        for row in reader:
            if len(row) < 4 or not row[1] or not row[2]:  # 都道府県名と新市町村名は必須
                continue
                
            date = convert_japanese_date(row[0])  # 合併年月日
            prefecture = row[1].strip()  # 都道府県
            new_city = clean_city_name(row[2])  # 新市町村名
            
            # '同郡'を適切な郡名に置き換える
            old_cities_str = replace_same_county(row[3])
            old_cities = old_cities_str.split('、')  # 旧市町村名（読み仮名）のリスト
            
            # 旧市町村名から読み仮名を抽出
            for old_city_info in old_cities:
                old_city, reading = extract_reading(old_city_info)
                if not old_city:  # 市区町村名が空の場合はスキップ
                    continue
                
                # 合併形態の判定（新設・編入の判定ロジックを追加）
                merge_type = "新設" if len(old_cities) > 1 else "編入"
                
                # マッピングに追加
                city_changes[(prefecture, old_city)] = {
                    "new": new_city,
                    "date": date,
                    "type": merge_type,
                    "reading": reading
                }
    
    return city_changes

def generate_city_changes_code(city_changes: Dict[Tuple[str, str], Dict[str, str]]) -> str:
    """
    市区町村合併データから Python コードを生成
    
    Parameters:
    -----------
    city_changes : Dict[Tuple[str, str], Dict[str, str]]
        市区町村合併データのマッピング
    
    Returns:
    --------
    str
        生成された Python コード
    """
    code = "# 市区町村の変更履歴（平成11年以降の変更）\nCITY_CHANGES = {\n"
    
    # 日付でソート
    sorted_items = sorted(city_changes.items(), key=lambda x: (x[1]['date'], x[0][0], x[0][1]))
    
    for (prefecture, old_city), change in sorted_items:
        if not prefecture or not old_city or not change['new'] or not change['date']:
            continue
            
        code += f"    (\"{prefecture}\", \"{old_city}\"): {{\"new\": \"{change['new']}\", "
        code += f"\"date\": \"{change['date']}\", \"type\": \"{change['type']}\", "
        code += f"\"reading\": \"{change['reading']}\"}},\n"
    
    code += "}\n"
    return code

def main():
    # CSVファイルから市区町村合併データを読み込む
    city_changes = read_city_changes("平成11年以降合併市区町村.csv")
    
    # Python コードを生成
    code = generate_city_changes_code(city_changes)
    
    # 生成したコードをファイルに出力
    with open("city_changes.py", "w", encoding="utf-8") as f:
        f.write(code)
    
    print(f"Total number of city changes: {len(city_changes)}")

if __name__ == "__main__":
    main() 