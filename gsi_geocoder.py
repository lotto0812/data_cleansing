import requests
import pandas as pd
import folium
import time
from typing import Dict, List, Optional, Union
from address_normalizer import JapaneseAddressNormalizer
import re
from datetime import datetime
import csv

class GSIGeocoder:
    """国土地理院APIを使用した住所ジオコーディングクラス"""
    
    def __init__(self):
        self.normalizer = JapaneseAddressNormalizer()
        self.base_url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
        self.results = []
        self.batch_size = 10000
        self.batch_num = 1
    
    def geocode(self, address: str) -> Optional[Dict]:
        """住所をジオコーディング"""
        # 住所の正規化
        normalized_address = self.normalizer.normalize_address(address)
        
        params = {
            "q": normalized_address
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                return {
                    "latitude": float(result.get("geometry", {}).get("coordinates", [])[1]),
                    "longitude": float(result.get("geometry", {}).get("coordinates", [])[0]),
                    "normalized_address": normalized_address,
                    "matched_address": result.get("properties", {}).get("title", ""),
                    "raw_response": result  # 生データを追加
                }
        except Exception as e:
            print(f"Error geocoding {address}: {str(e)}")
        return None
    
    def process_addresses(self, input_file: str):
        """住所を一括処理"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    address = row['address']
                    name = row.get('name', '')
                    
                    result = self.geocode(address)
                    if result:
                        self.results.append({
                            'name': name,
                            'original_address': address,
                            'normalized_address': result['normalized_address'],
                            'matched_address': result['matched_address'],
                            'raw_response': str(result['raw_response']),
                            'latitude': result['latitude'],
                            'longitude': result['longitude']
                        })
                    
                    # バッチサイズに達したら保存
                    if len(self.results) >= self.batch_size:
                        self._save_batch()
                    
                    time.sleep(1)  # API制限を考慮
                
                # 残りの結果を保存
                if self.results:
                    self._save_batch()
                
        except Exception as e:
            print(f"Error processing addresses: {str(e)}")
            if self.results:
                self._save_batch(error=True)

    def _save_batch(self, error: bool = False):
        """バッチ結果を保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'geocoding_results_batch_{self.batch_num}_{timestamp}.csv'
        if error:
            filename = f'error_batch_{self.batch_num}_{timestamp}.csv'

        with open(filename, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['name', 'original_address', 'normalized_address',
                         'matched_address', 'raw_response', 'latitude', 'longitude']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\nバッチ {self.batch_num} の結果を {filename} に保存しました")
        self.results = []  # 結果をクリア
        self.batch_num += 1

def generate_map_html(df: pd.DataFrame, output_file: str = 'map.html'):
    """ジオコーディング結果を地図に表示"""
    if df.empty:
        print("No data to display on map")
        return
    
    # 中心座標を計算
    center_lat = df['lat'].mean()
    center_lng = df['lng'].mean()
    
    # 地図を作成
    m = folium.Map(location=[center_lat, center_lng], zoom_start=12)
    
    # マーカーを追加
    for _, row in df.iterrows():
        popup_text = f"{row.get('name', '')}<br>{row['matched_address']}"
        folium.Marker(
            [row['lat'], row['lng']],
            popup=popup_text,
            tooltip=row.get('name', row['matched_address'])
        ).add_to(m)
    
    # 国土地理院の利用規約に基づく出典表示
    attribution = ('地理院地図の住所検索API (https://msearch.gsi.go.jp/address-search/AddressSearch) を使用'
                  '<br>出典：国土地理院')
    
    # 出典情報を地図に追加
    m.get_root().html.add_child(folium.Element(
        f'<div style="position: fixed; bottom: 10px; left: 10px; '
        f'background-color: white; padding: 5px; border-radius: 5px; '
        f'z-index: 1000;">{attribution}</div>'
    ))
    
    # 地図を保存
    m.save(output_file)

if __name__ == "__main__":
    # 使用例
    geocoder = GSIGeocoder()
    
    # 単一の住所のジオコーディング
    result = geocoder.geocode("東京都渋谷区渋谷2-24-12")
    if result:
        print(f"単一住所の結果:")
        print(f"緯度: {result['lat']}, 経度: {result['lng']}")
        print(f"正規化された住所: {result['normalized_address']}")
        print(f"マッチした住所: {result['matched_address']}\n")
    
    # 複数の住所の一括ジオコーディング
    test_addresses = [
        {
            'name': '渋谷スクランブルスクエア',
            'address': '東京都渋谷区渋谷2-24-12'
        },
        {
            'name': '東京スカイツリー',
            'address': '東京都墨田区押上1-1-2'
        }
    ]
    
    results_df = geocoder.batch_geocode(
        test_addresses,
        address_key='address',
        name_key='name',
        interval=0.5
    )
    
    if not results_df.empty:
        print("複数住所の結果:")
        print(results_df)
        
        # 地図を生成
        generate_map_html(results_df, 'example_map.html') 