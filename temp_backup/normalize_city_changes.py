import csv
import re
from typing import List, Tuple

def remove_readings(text: str) -> str:
    """
    文字列から（）で囲まれた読み仮名を削除
    """
    return re.sub(r'[（(][^）)]*[）)]', '', text)

def extract_county_name(text: str) -> str:
    """
    文字列から郡名を抽出
    例: '西彼杵郡多良見町' -> '西彼杵'
    """
    match = re.search(r'(.+?)郡', text)
    return match.group(1) if match else None

def replace_same_county(rows: List[List[str]]) -> List[List[str]]:
    """
    「同郡」を前の行の郡名で置き換える
    """
    result = []
    current_county = None
    current_merge_date = None
    current_city = None
    
    for row in rows:
        if len(row) < 4:
            continue
            
        merge_date = row[0]
        new_city = row[2]
        old_city = row[3]
        
        # 合併日と新市町村名が変わったら郡名をリセット
        if merge_date != current_merge_date or new_city != current_city:
            current_county = None
            current_merge_date = merge_date
            current_city = new_city
        
        # 現在の郡名を取得（「同郡」以外の「〜郡」を含む場合）
        if '郡' in old_city and '同郡' not in old_city:
            current_county = extract_county_name(old_city)
            
        # 「同郡」を置き換える
        if current_county and '同郡' in old_city:
            old_city = old_city.replace('同郡', current_county + '郡')
            row[3] = old_city
            
        result.append(row)
    
    return result

def process_csv(input_file: str, output_file: str) -> None:
    """
    CSVファイルを処理して正規化
    """
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        
        # ヘッダーをスキップして新しいヘッダーを書き込み
        next(reader)
        writer.writerow(['合併年月日', '都道府県', '新市町村名', '旧市区町村名'])
        
        rows = []
        for row in reader:
            if len(row) < 4:  # データが不十分な行はスキップ
                continue
                
            merge_date = row[0].strip()
            prefecture = row[1].strip()
            new_city = remove_readings(row[2].strip())
            
            # 3列目以降のすべての列を結合して、「、」で分割
            old_cities_text = '、'.join([city.strip() for city in row[3:] if city.strip()])
            old_cities = [remove_readings(city.strip()) for city in old_cities_text.split('、') if city.strip()]
            
            # 各旧市区町村について個別の行を作成
            for old_city in old_cities:
                if merge_date and prefecture and new_city and old_city:
                    rows.append([
                        merge_date,
                        prefecture,
                        new_city,
                        old_city
                    ])
        
        # 「同郡」を置き換える
        rows = replace_same_county(rows)
        
        # 結果を書き込み
        writer.writerows(rows)

def main():
    input_file = '平成11年以降合併市区町村.csv'
    output_file = '平成11年以降合併市区町村_正規化.csv'
    process_csv(input_file, output_file)
    print(f"正規化が完了しました。出力ファイル: {output_file}")

if __name__ == '__main__':
    main() 