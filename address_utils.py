"""
住所処理のユーティリティ関数
"""

import re
import difflib
from typing import Dict

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
    住所の数字を正規化する（全角→半角、漢数字→アラビア数字）
    
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
    
    # 漢数字をアラビア数字に変換（一～九のみ対応）
    kanji_numbers = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                    '六': '6', '七': '7', '八': '8', '九': '9'}
    for k, v in kanji_numbers.items():
        normalized = normalized.replace(k, v)
    
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
    # 数字を正規化
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
    # 数字を正規化
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