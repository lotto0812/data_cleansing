import requests
import pandas as pd
import folium
import time
from typing import Dict, List, Optional, Union
from address_normalizer import JapaneseAddressNormalizer
import re

class GSIGeocoder:
    """国土地理院APIを使用した住所ジオコーディングクラス"""
    
    def __init__(self):
        self.base_url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
        self.normalizer = JapaneseAddressNormalizer()
    
    def geocode(self, address: str) -> Optional[Dict[str, Union[float, str]]]:
        """単一の住所を緯度経度に変換"""
        # 住所の正規化
        normalized_address = self.normalizer.normalize_address(address)
        
        # 元の住所から番地号を抽出
        base_address, house_number = self.normalizer._extract_house_number(address)
        
        params = {
            "q": normalized_address
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            results = response.json()
            
            if results and len(results) > 0:
                # 最も関連性の高い結果を使用
                result = results[0]
                coordinates = result['geometry']['coordinates']
                matched_address = result.get('properties', {}).get('title', '')
                
                # マッチした住所に番地号を追加
                if house_number and not re.search(rf'{house_number}(?:番地?|号)', matched_address):
                    if '番地' in matched_address:
                        matched_address = f"{matched_address}-{house_number}"
                    else:
                        matched_address = f"{matched_address}{house_number}号"
                
                return {
                    'lat': float(coordinates[1]),  # 緯度
                    'lng': float(coordinates[0]),  # 経度
                    'original_address': address,
                    'normalized_address': normalized_address,
                    'matched_address': matched_address
                }
            
        except requests.exceptions.RequestException as e:
            print(f"Error geocoding address '{address}': {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error parsing response for address '{address}': {str(e)}")
        
        return None
    
    def batch_geocode(self, 
                     addresses: List[Dict[str, str]], 
                     address_key: str = 'address',
                     name_key: Optional[str] = None,
                     interval: float = 0.5) -> pd.DataFrame:
        """複数の住所を一括で緯度経度に変換"""
        results = []
        total = len(addresses)
        
        for i, item in enumerate(addresses, 1):
            address = item[address_key]
            name = item.get(name_key, '') if name_key else ''
            
            print(f"\r処理中... {i}/{total} ({(i/total)*100:.1f}%)", end='')
            
            result = self.geocode(address)
            if result:
                result['name'] = name
                results.append(result)
            else:
                print(f"\n変換失敗: {address}")
            
            # APIリクエスト間隔を制御
            if i < total:  # 最後の要素以外で待機
                time.sleep(interval)
        
        print("\n処理完了")
        return pd.DataFrame(results)

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