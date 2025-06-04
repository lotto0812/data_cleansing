"""
住所処理のユーティリティ関数
"""

import re
import difflib
import csv
import json
from typing import Dict, Tuple, List
from datetime import datetime

def load_city_mapping() -> Dict:
    """市区町村マッピングを読み込む"""
    try:
        with open('市区町村マッピング.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load 市区町村マッピング.json: {e}")
        return {}

# 市区町村の変更履歴を読み込む
CITY_CHANGES = load_city_mapping()

# 有効な都道府県名のリスト
VALID_PREFECTURES = {
    '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
    '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
    '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県',
    '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県',
    '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県',
    '徳島県', '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県',
    '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
}

def is_valid_prefecture(prefecture: str) -> bool:
    """
    都道府県名が有効かどうかを判定する
    
    Parameters:
    -----------
    prefecture : str
        判定する都道府県名
    
    Returns:
    --------
    bool
        有効な都道府県名の場合はTrue、そうでない場合はFalse
    """
    if not prefecture:
        return False
    return prefecture.strip() in VALID_PREFECTURES

def extract_prefecture(address: str) -> Tuple[str, str]:
    """
    住所から都道府県名を抽出し、残りの住所と共に返す
    
    Args:
        address (str): 入力住所
    
    Returns:
        Tuple[str, str]: (都道府県名, 残りの住所)
    """
    for pref in VALID_PREFECTURES:
        if address.startswith(pref):
            return pref, address[len(pref):]
    return "", address

def normalize_city_name(address: str, date: str = None) -> str:
    """
    廃止された市区町村名を現在の名称に変換
    
    Args:
        address (str): 入力住所
        date (str, optional): 基準日（YYYY-MM-DD形式）。指定がない場合は最新の状態に変換
    
    Returns:
        str: 正規化された住所
    """
    # 都道府県名を抽出
    prefecture, remaining_address = extract_prefecture(address)
    if not prefecture:
        return address
    
    # 基準日の処理
    target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    
    # 旧市町村名を探索
    normalized = remaining_address
    for (pref, old_city), info in CITY_CHANGES.items():
        if prefecture == pref and old_city in remaining_address:
            # 基準日チェック
            change_date = datetime.strptime(info["date"], "%Y-%m-%d")
            if not date or target_date >= change_date:
                # 新しい市町村名に置換
                normalized = remaining_address.replace(old_city, info["new"])
                break
    
    # 都道府県名と正規化された住所を結合
    return prefecture + normalized

def normalize_number(number: str) -> str:
    """漢数字と全角数字を半角算用数字に変換"""
    kanji_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
        '１': '1', '２': '2', '３': '3', '４': '4', '５': '5',
        '６': '6', '７': '7', '８': '8', '９': '9', '０': '0'
    }
    
    # 漢数字と全角数字を半角算用数字に変換
    result = number
    for kanji, digit in kanji_numbers.items():
        result = result.replace(kanji, digit)
    
    return result

def normalize_address_numbers(address: str) -> str:
    """
    住所の数字を正規化する
    - 丁目・番地・号の前の漢数字のみをアラビア数字に変換
    - その他の漢数字（地名等）はそのまま保持
    - 全角数字は半角数字に変換
    
    Parameters:
    -----------
    address : str
        正規化する住所
        
    Returns:
    --------
    str
        正規化された住所
    """
    # 全角数字を半角に変換
    normalized = address.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    
    # 丁目・番地・号の前の漢数字のみをアラビア数字に変換
    kanji_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9'
    }
    
    # 丁目・番地・号の前の漢数字のみを変換
    for kanji, arabic in kanji_numbers.items():
        normalized = re.sub(f'{kanji}(?=(丁目|番地?|号))', arabic, normalized)
    
    return normalized

def extract_address_parts(address: str) -> tuple:
    """住所から丁目、番地、号の数字を抽出"""
    # 数字を正規化
    normalized = normalize_address_numbers(address)
    
    # パターン1: ハイフン区切り (例: 1-4-5)
    pattern1 = r'(\d+)[-−ー](\d+)[-−ー](\d+)'
    match = re.search(pattern1, normalized)
    if match:
        return match.group(1), match.group(2), match.group(3)
    
    # パターン2: ハイフン区切り (例: 1-4)
    pattern2 = r'(\d+)[-−ー](\d+)'
    match = re.search(pattern2, normalized)
    if match:
        return match.group(1), match.group(2), None
    
    # パターン3: 丁目、番、号
    chome = None
    banchi = None
    go = None
    
    if '丁目' in normalized:
        parts = normalized.split('丁目')
        nums = re.findall(r'\d+', parts[0])
        if nums:
            chome = nums[-1]
            rest = parts[1]
        else:
            rest = normalized
    else:
        rest = normalized
    
    if '番' in rest:
        parts = rest.split('番')
        nums = re.findall(r'\d+', parts[0])
        if nums:
            banchi = nums[-1]
            rest = parts[1]
    
    if '号' in rest:
        nums = re.findall(r'\d+', rest.split('号')[0])
        if nums:
            go = nums[-1]
    
    return chome, banchi, go

def calculate_address_similarity(address1: str, address2: str) -> float:
    """
    2つの住所の類似度を計算する
    
    Parameters:
    -----------
    address1 : str
        比較する住所1
    address2 : str
        比較する住所2
        
    Returns:
    --------
    float
        類似度（0.0～1.0）
    """
    # 数字を正規化（地名の漢数字は保持）
    norm1 = normalize_address_numbers(address1)
    norm2 = normalize_address_numbers(address2)
    
    # 文字列を正規化（空白除去）
    norm1 = ''.join(norm1.split())
    norm2 = ''.join(norm2.split())
    
    # 完全一致の場合
    if norm1 == norm2:
        return 1.0
    
    # 部分文字列の場合
    if norm1 in norm2 or norm2 in norm1:
        return 0.8
    
    # 文字の一致率を計算
    matches = sum(1 for a, b in zip(norm1, norm2) if a == b)
    max_length = max(len(norm1), len(norm2))
    
    return matches / max_length if max_length > 0 else 0.0

def analyze_address_match_level(input_address: str, matched_address: str) -> Dict[str, bool]:
    """
    住所のマッチングレベルを分析する
    
    Parameters:
    -----------
    input_address : str
        入力された住所
    matched_address : str
        マッチした住所
        
    Returns:
    --------
    Dict[str, bool]
        各レベル（丁目、番地、号）のマッチング結果
    """
    # 数字を正規化（地名の漢数字は保持）
    input_norm = normalize_address_numbers(input_address)
    matched_norm = normalize_address_numbers(matched_address)
    
    # 丁目、番地、号を抽出
    def extract_numbers(address: str) -> Dict[str, str]:
        numbers = {
            'chome': '',
            'banchi': '',
            'go': ''
        }
        
        # 丁目を抽出
        chome_match = re.search(r'(\d+)丁目', address)
        if chome_match:
            numbers['chome'] = chome_match.group(1)
            
        # 番地を抽出
        banchi_match = re.search(r'(\d+)番地?', address)
        if banchi_match:
            numbers['banchi'] = banchi_match.group(1)
            
        # 号を抽出
        go_match = re.search(r'(\d+)号', address)
        if go_match:
            numbers['go'] = go_match.group(1)
            
        return numbers
    
    input_numbers = extract_numbers(input_norm)
    matched_numbers = extract_numbers(matched_norm)
    
    return {
        'chome_match': input_numbers['chome'] == matched_numbers['chome'] and input_numbers['chome'] != '',
        'banchi_match': input_numbers['banchi'] == matched_numbers['banchi'] and input_numbers['banchi'] != '',
        'go_match': input_numbers['go'] == matched_numbers['go'] and input_numbers['go'] != ''
    }

def normalize_city_name_with_history(address: str, date: str = None) -> str:
    """
    市区町村名を正規化する（合併履歴を考慮）
    
    Parameters:
    -----------
    address : str
        正規化する住所
    date : str, optional
        基準日（この日付時点での市区町村名に変換）
        形式：YYYY-MM-DD
    
    Returns:
    --------
    str
        正規化された住所
    """
    # 都道府県名と市区町村名を分離
    prefecture, remaining = extract_prefecture(address)
    if not prefecture:
        return address
        
    # 完全な市区町村名を作成（都道府県名 + 市区町村名）
    full_city_name = prefecture + remaining.split()[0]
    
    # マッピングから新しい市区町村名を取得
    if full_city_name in CITY_CHANGES.get('mapping', {}):
        changes = CITY_CHANGES['mapping'][full_city_name]
        if changes:
            # 日付指定がある場合は、その日付以前の最新の変更を使用
            if date:
                valid_changes = [
                    change for change in changes 
                    if convert_japanese_date(change['merge_date']) <= date
                ]
                if valid_changes:
                    new_city = valid_changes[-1]['new_city']
                    # 元の住所の市区町村名部分を新しい名前で置換
                    return address.replace(full_city_name, new_city)
            
            # 日付指定がない場合は最新の変更を使用
            new_city = changes[-1]['new_city']
            return address.replace(full_city_name, new_city)
    
    return address

def convert_japanese_date(japanese_date: str) -> str:
    """
    和暦の日付を西暦に変換
    例：平成17年3月1日 → 2005-03-01
    """
    # 元号の変換テーブル
    era_table = {
        '平成': 1989,
        '令和': 2019
    }
    
    # 数字を抽出
    match = re.match(r'(平成|令和)(\d+)年(\d+)月(\d+)日', japanese_date)
    if not match:
        return '9999-12-31'  # 変換できない場合は遠い未来の日付を返す
        
    era, year, month, day = match.groups()
    year = int(year)
    month = int(month)
    day = int(day)
    
    # 西暦に変換
    western_year = era_table[era] + year - 1
    
    # YYYY-MM-DD形式に変換
    return f'{western_year:04d}-{month:02d}-{day:02d}'

def get_city_reading(prefecture: str, city_name: str) -> str:
    """
    市町村名の読み仮名を取得する
    
    Parameters:
    -----------
    prefecture : str
        都道府県名
    city_name : str
        市町村名
    
    Returns:
    --------
    str
        読み仮名（見つからない場合は空文字列）
    """
    # 新市町村名で検索
    for (pref, _), change in CITY_CHANGES.items():
        if pref == prefecture and change['new'] == city_name:
            return change.get('reading', '')
            
    # 旧市町村名で検索
    for (pref, old_city), change in CITY_CHANGES.items():
        if pref == prefecture and old_city == city_name:
            return change.get('reading', '')
            
    return ''

def get_city_history(prefecture: str, city_name: str) -> List[Dict]:
    """
    市町村の変遷履歴を取得する
    
    Parameters:
    -----------
    prefecture : str
        都道府県名
    city_name : str
        市町村名
    
    Returns:
    --------
    List[Dict]
        変遷履歴のリスト。各要素は以下のキーを持つ辞書：
        - old_name: 旧市町村名
        - new_name: 新市町村名
        - date: 変更日
        - type: 変更種別（新設/編入）
        - reading: 読み仮名
    """
    history = []
    
    # 新市町村名として検索
    for (pref, old_city), change in CITY_CHANGES.items():
        if pref == prefecture and change['new'] == city_name:
            history.append({
                'old_name': old_city,
                'new_name': change['new'],
                'date': change['date'],
                'type': change['type'],
                'reading': change.get('reading', '')
            })
            
    # 旧市町村名として検索
    for (pref, old_city), change in CITY_CHANGES.items():
        if pref == prefecture and old_city == city_name:
            history.append({
                'old_name': old_city,
                'new_name': change['new'],
                'date': change['date'],
                'type': change['type'],
                'reading': change.get('reading', '')
            })
            
    # 日付でソート
    history.sort(key=lambda x: x['date'])
    return history

def improve_address_matching(input_address: str, candidates: List[str]) -> Tuple[str, float]:
    """
    住所マッチングの精度を改善する
    
    Parameters:
    -----------
    input_address : str
        入力住所
    candidates : List[str]
        マッチング候補の住所リスト
    
    Returns:
    --------
    Tuple[str, float]
        最もマッチする住所と類似度のタプル
    """
    best_match = None
    highest_similarity = -1
    
    # 入力住所から都道府県を抽出
    input_prefecture, input_remaining = extract_prefecture(input_address)
    
    for candidate in candidates:
        # 候補住所から都道府県を抽出
        candidate_prefecture, candidate_remaining = extract_prefecture(candidate)
        
        # 都道府県が一致しない場合はスキップ
        if input_prefecture and candidate_prefecture and input_prefecture != candidate_prefecture:
            continue
        
        # 住所の類似度を計算
        similarity = calculate_address_similarity(input_remaining, candidate_remaining)
        
        # 都道府県が一致する場合は類似度にボーナスを加算
        if input_prefecture and candidate_prefecture and input_prefecture == candidate_prefecture:
            similarity += 0.1
        
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = candidate
    
    return best_match or input_address, highest_similarity 