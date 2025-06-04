import csv
import json
import time
import requests
import os
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from address_utils import (
    normalize_address_numbers,
    calculate_address_similarity,
    analyze_address_match_level,
    normalize_city_name_with_history,
    improve_address_matching
)

class GsiGeocoder:
    """国土地理院APIを使用して住所から緯度経度を取得するクラス"""
    
    def __init__(self):
        self.base_url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
        self.cache_file = "geocoding_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """キャッシュファイルを読み込む"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """キャッシュをファイルに保存"""
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def _make_cache_key(self, address: str, store_code: str = None, store_name: str = None) -> str:
        """キャッシュのキーを生成"""
        key_parts = [normalize_address_numbers(address)]
        if store_code:
            key_parts.append(str(store_code))
        if store_name:
            key_parts.append(str(store_name))
        return "||".join(key_parts)
    
    def geocode(self, address: str, store_code: str = None, store_name: str = None) -> Tuple[Optional[Dict], bool]:
        """住所から緯度経度を取得"""
        # キャッシュのキーを生成
        cache_key = self._make_cache_key(address, store_code, store_name)
        
        # キャッシュをチェック
        if cache_key in self.cache:
            return self.cache[cache_key], True
        
        try:
            # 住所を正規化（市町村合併履歴を考慮）
            normalized_address = normalize_city_name_with_history(
                normalize_address_numbers(address)
            )
            
            # APIリクエストパラメータ
            params = {'q': normalized_address}
            
            # APIリクエスト
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # レスポンスを解析
            results = response.json()
            
            if not results:
                return None, False
            
            # 候補住所のリストを作成
            candidate_addresses = [
                result.get('properties', {}).get('title', '')
                for result in results
            ]
            
            # 改善された住所マッチングを使用
            best_match_address, highest_similarity = improve_address_matching(
                normalized_address,
                candidate_addresses
            )
            
            # 最適な結果を選択
            best_match = None
            for result in results:
                if result.get('properties', {}).get('title', '') == best_match_address:
                    best_match = result
                    break
            
            if best_match:
                # 緯度経度を取得
                coordinates = best_match.get('geometry', {}).get('coordinates', [])
                matched_address = best_match.get('properties', {}).get('title', '')
                
                if len(coordinates) >= 2:
                    # 住所のマッチングレベルを分析
                    match_level = analyze_address_match_level(normalized_address, matched_address)
                    
                    result = {
                        'latitude': coordinates[1],
                        'longitude': coordinates[0],
                        'normalized_address': normalized_address,
                        'matched_address': matched_address,
                        'similarity': highest_similarity,
                        'chome_match': match_level['chome_match'],
                        'banchi_match': match_level['banchi_match'],
                        'go_match': match_level['go_match'],
                        'store_code': store_code,
                        'store_name': store_name
                    }
                    
                    # 結果をキャッシュに保存
                    self.cache[cache_key] = result
                    self._save_cache()
                    
                    return result, False
            
            return None, False
            
        except Exception as e:
            print(f"Error geocoding address {address}: {e}")
            return None, False

def process_dataframe(
    df: pd.DataFrame,
    address_column: str = 'address',
    store_code_column: str = 'store_code',
    store_name_column: str = 'store_name',
    output_file: str = None,
    progress_callback = None
) -> pd.DataFrame:
    """
    データフレームから住所を読み込み、緯度経度を取得して結果を返す
    
    Parameters:
    -----------
    df : pd.DataFrame
        入力データフレーム
    address_column : str
        住所が格納されている列名
    store_code_column : str
        店舗コードが格納されている列名
    store_name_column : str
        店舗名が格納されている列名
    output_file : str, optional
        結果を保存するCSVファイルのパス
    progress_callback : callable, optional
        進捗を報告するコールバック関数。
        store_name, address, resultを引数として受け取る
    
    Returns:
    --------
    pd.DataFrame
        緯度経度情報が追加されたデータフレーム。
        マッチしなかったデータも含む（緯度経度情報はNaN）
    """
    geocoder = GsiGeocoder()
    results = []
    
    # 各行の住所を処理
    for idx, row in df.iterrows():
        address = row.get(address_column)
        store_code = row.get(store_code_column) if store_code_column in df.columns else None
        store_name = row.get(store_name_column) if store_name_column in df.columns else None
        
        if pd.isna(address):
            print(f"Warning: Missing address at index {idx}")
            result_row = row.to_dict()
            result_row.update({
                'normalized_address': None,
                'matched_address': None,
                'latitude': None,
                'longitude': None,
                'similarity': 0.0,
                'chome_match': False,
                'banchi_match': False,
                'go_match': False,
                'match_status': 'missing_address'
            })
            results.append(result_row)
            continue
            
        result, is_cached = geocoder.geocode(str(address), store_code, store_name)
        
        # 元のデータを保持しつつ、緯度経度情報を追加
        result_row = row.to_dict()
        
        if result:
            # マッチした場合
            result_row.update({
                'normalized_address': result['normalized_address'],
                'matched_address': result['matched_address'],
                'latitude': result['latitude'],
                'longitude': result['longitude'],
                'similarity': result['similarity'],
                'chome_match': result['chome_match'],
                'banchi_match': result['banchi_match'],
                'go_match': result['go_match'],
                'match_status': 'matched'
            })
        else:
            # マッチしなかった場合
            result_row.update({
                'normalized_address': normalize_address_numbers(str(address)),
                'matched_address': None,
                'latitude': None,
                'longitude': None,
                'similarity': 0.0,
                'chome_match': False,
                'banchi_match': False,
                'go_match': False,
                'match_status': 'unmatched'
            })
        
        results.append(result_row)
        
        # 進捗コールバックを呼び出し
        if progress_callback:
            progress_callback(store_name or 'Unknown store', address, result or {})
        
        # API制限を考慮して待機（キャッシュヒットの場合は待機しない）
        if not is_cached:
            time.sleep(0.5)
    
    # 結果をデータフレームに変換
    result_df = pd.DataFrame(results)
    
    # 結果をファイルに保存
    if output_file:
        result_df.to_csv(output_file, index=False, encoding='utf-8')
    
    return result_df 