import csv
import requests
from gsi_geocoder import GSIGeocoder
import time
from typing import Dict, List, Tuple
import os
from math import radians, sin, cos, sqrt, atan2
from dotenv import load_dotenv
import difflib
import re
from datetime import datetime
import unicodedata

# .envファイルから環境変数を読み込む
print("環境変数を読み込み中...")
load_dotenv(verbose=True)  # verboseモードで詳細な情報を表示

def normalize_number(number: str) -> str:
    """数字を正規化（半角数字に統一）"""
    # 漢数字を数字に変換するための辞書
    kanji_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
    }
    
    # 全角数字を半角に変換
    number = unicodedata.normalize('NFKC', str(number))
    
    # 漢数字を変換
    for kanji, digit in kanji_numbers.items():
        number = number.replace(kanji, digit)
    
    return number

def normalize_address_numbers(address: str) -> str:
    """住所内の全ての数字を正規化"""
    # 数字（漢数字含む）を検出して正規化
    numbers = re.findall(r'[一二三四五六七八九十\d]+', address)
    normalized_address = address
    
    for number in numbers:
        normalized_address = normalized_address.replace(number, normalize_number(number))
    
    return normalized_address

def get_google_coordinates(address: str, api_key: str) -> Tuple[float, float]:
    """Google Maps APIを使用して緯度経度を取得"""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key,
        "language": "ja",
        "region": "jp"
    }
    
    try:
        print(f"\nGoogle Maps APIリクエストURL: {url}")
        print(f"パラメータ: address={address}, key={api_key[:6]}...")
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "OK" and data["results"]:
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            print(f"Google Maps API Error for {address}: {data['status']} - {data.get('error_message', 'No error message')}")
            print(f"完全なレスポンス: {data}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Request Error for {address}: {str(e)}")
        return None, None

def get_gsi_coordinates(address: str, geocoder: GSIGeocoder) -> Tuple[float, float, str, str]:
    """国土地理院APIを使用して緯度経度を取得"""
    result = geocoder.geocode(address)
    if result and "latitude" in result and "longitude" in result:
        return (
            result["latitude"],
            result["longitude"],
            result.get("normalized_address", ""),
            result.get("matched_address", "")
        )
    return None, None, "", ""

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """2点間の距離をメートルで計算（Haversine formula）"""
    R = 6371000  # 地球の半径（メートル）

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

def calculate_address_similarity(addr1: str, addr2: str) -> float:
    """2つの住所の類似度を計算（改善版）"""
    # 数字を正規化
    norm_addr1 = normalize_address_numbers(addr1)
    norm_addr2 = normalize_address_numbers(addr2)
    
    # ビル名や階数情報を除去
    norm_addr1 = re.sub(r'\s+.*$', '', norm_addr1)
    norm_addr2 = re.sub(r'\s+.*$', '', norm_addr2)
    
    return difflib.SequenceMatcher(None, norm_addr1, norm_addr2).ratio()

def analyze_address_match_level(normalized: str, matched: str) -> Dict[str, bool]:
    """住所のマッチングレベルを分析（改善版）"""
    # 両方の住所を数字正規化
    norm_normalized = normalize_address_numbers(normalized)
    norm_matched = normalize_address_numbers(matched)
    
    # 数字を抽出
    norm_numbers = re.findall(r'\d+', norm_normalized)
    matched_numbers = re.findall(r'\d+', norm_matched)
    
    # マッチングレベルの判定
    chome_match = False
    banchi_match = False
    go_match = False
    
    # 丁目の判定
    if '丁目' in matched and norm_numbers and norm_numbers[0] in matched_numbers:
        chome_match = True
    
    # 番地の判定
    if '番' in matched and len(norm_numbers) > 1:
        banchi_number = norm_numbers[1]
        if banchi_number in matched_numbers:
            banchi_match = True
    
    # 号の判定
    if '号' in matched and len(norm_numbers) > 2:
        go_number = norm_numbers[2]
        if go_number in matched_numbers:
            go_match = True
    
    return {
        'chome_match': chome_match,
        'banchi_match': banchi_match,
        'go_match': go_match
    }

def save_batch_results(results: List[Dict], batch_num: int):
    """バッチ結果をCSVファイルに保存"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'gsi_geocoding_results_batch_{batch_num}_{timestamp}.csv'
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['name', 'original_address', 'normalized_address', 
                     'matched_address', 'address_similarity', 
                     'chome_match', 'banchi_match', 'go_match',
                     'latitude', 'longitude']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nバッチ {batch_num} の結果を {filename} に保存しました")

def analyze_gsi_results():
    """国土地理院のジオコーディング結果を分析"""
    # GSIジオコーダーの初期化
    gsi_geocoder = GSIGeocoder()
    results = []
    batch_size = 10000
    batch_num = 1
    total_processed = 0
    
    print("=== 国土地理院ジオコーディング結果 ===\n")
    
    try:
        # CSVから店舗データを読み込み
        with open('restaurants.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                name = row['name']
                address = row['address']
                
                print(f"\n▼ {name}")
                print(f"入力住所: {address}")
                
                # 国土地理院の座標を取得
                result = gsi_geocoder.geocode(address)
                if result:
                    normalized_addr = result.get("normalized_address", "")
                    matched_addr = result.get("matched_address", "")
                    lat = result.get("lat")
                    lng = result.get("lng")
                    
                    # 住所の類似度を計算
                    similarity = calculate_address_similarity(normalized_addr, matched_addr)
                    
                    # マッチングレベルを分析
                    match_levels = analyze_address_match_level(normalized_addr, matched_addr)
                    
                    print(f"正規化後: {normalized_addr}")
                    print(f"国土地理院の住所: {matched_addr}")
                    print(f"住所類似度: {similarity:.2f}")
                    print(f"マッチングレベル: 丁目={match_levels['chome_match']}, "
                          f"番地={match_levels['banchi_match']}, "
                          f"号={match_levels['go_match']}")
                    
                    if lat and lng:
                        print(f"緯度経度: {lat}, {lng}")
                    
                    results.append({
                        'name': name,
                        'original_address': address,
                        'normalized_address': normalized_addr,
                        'matched_address': matched_addr,
                        'address_similarity': f"{similarity:.2f}",
                        'chome_match': match_levels['chome_match'],
                        'banchi_match': match_levels['banchi_match'],
                        'go_match': match_levels['go_match'],
                        'latitude': lat,
                        'longitude': lng
                    })
                else:
                    print("ジオコーディング結果なし")
                
                total_processed += 1
                
                # バッチサイズに達したら結果を保存
                if len(results) >= batch_size:
                    save_batch_results(results, batch_num)
                    results = []  # 結果をクリア
                    batch_num += 1
                
                # API制限を考慮して待機
                time.sleep(1)
        
        # 残りの結果があれば保存
        if results:
            save_batch_results(results, batch_num)
        
        print(f"\n=== 処理完了 ===")
        print(f"総処理件数: {total_processed}")
        print(f"出力バッチ数: {batch_num}")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")
        # エラーが発生した時点での結果を保存
        if results:
            save_batch_results(results, f"error_{batch_num}")

if __name__ == "__main__":
    analyze_gsi_results() 