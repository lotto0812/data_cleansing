import pandas as pd
import requests
import time
from typing import Dict, List, Optional
import json

class GSIGeocoder:
    """国土地理院のジオコーディングAPIを使用するクラス"""
    
    def __init__(self):
        self.base_url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    
    def geocode(self, address: str) -> Optional[Dict[str, float]]:
        """
        住所を緯度経度に変換
        
        Args:
            address: 変換したい住所
            
        Returns:
            成功時: {'lat': 緯度, 'lng': 経度}
            失敗時: None
        """
        try:
            # 建物名や階数を除去（より正確な検索のため）
            address = address.split(' ')[0]
            
            # APIリクエスト
            response = requests.get(
                self.base_url,
                params={'q': address}
            )
            response.raise_for_status()
            
            results = response.json()
            if results and len(results) > 0:
                coordinates = results[0]['geometry']['coordinates']
                return {
                    'lng': coordinates[0],  # 経度
                    'lat': coordinates[1]   # 緯度
                }
        except Exception as e:
            print(f"Error geocoding address: {str(e)}")
        
        return None
    
    def batch_geocode(self, addresses: List[Dict[str, str]], 
                     address_key: str = 'address',
                     name_key: Optional[str] = None,
                     interval: float = 0.5) -> pd.DataFrame:
        """
        複数の住所を一括で緯度経度に変換
        
        Args:
            addresses: 住所情報を含む辞書のリスト
            address_key: 住所が格納されているキー名
            name_key: 名称が格納されているキー名（オプション）
            interval: リクエスト間隔（秒）
            
        Returns:
            変換結果のDataFrame
        """
        results = []
        
        for i, addr_dict in enumerate(addresses):
            address = addr_dict[address_key]
            name = addr_dict.get(name_key) if name_key else None
            
            print(f"\n処理中 ({i+1}/{len(addresses)}): {name if name else address}")
            
            result = self.geocode(address)
            if result:
                row = {
                    'address': address,
                    'lat': result['lat'],
                    'lng': result['lng']
                }
                if name_key:
                    row['name'] = addr_dict[name_key]
                    
                results.append(row)
                print(f"変換成功: 緯度 {result['lat']}, 経度 {result['lng']}")
            else:
                print(f"変換失敗: {address}")
            
            # APIの負荷を考慮して待機
            if i < len(addresses) - 1:  # 最後の要素以外で待機
                time.sleep(interval)
        
        return pd.DataFrame(results)

def generate_map_html(df: pd.DataFrame, output_file: str = 'locations_map.html'):
    """
    緯度経度データから地図を生成
    
    Args:
        df: 緯度経度データを含むDataFrame（必須カラム: lat, lng）
        output_file: 出力するHTMLファイル名
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Locations Map</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            #map { height: 600px; }
            .attribution { font-size: 12px; margin: 5px; }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <div class="attribution">住所データ：国土地理院</div>
        <script>
            var map = L.map('map').setView([35.6762, 139.6503], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
    """
    
    # マーカーを追加
    for _, row in df.iterrows():
        popup_content = row['name'] if 'name' in row else row['address']
        html_content += f"""
            L.marker([{row['lat']}, {row['lng']}])
                .bindPopup('{popup_content}<br>{row['address']}')
                .addTo(map);
        """
    
    html_content += """
        </script>
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n地図を{output_file}に保存しました。")

# 使用例
if __name__ == "__main__":
    # サンプルデータ
    sample_locations = [
        {
            'name': '渋谷スクランブルスクエア',
            'address': '東京都渋谷区渋谷2-24-12'
        },
        {
            'name': '東京スカイツリー',
            'address': '東京都墨田区押上1-1-2'
        }
    ]
    
    # ジオコーディング実行
    geocoder = GSIGeocoder()
    results_df = geocoder.batch_geocode(
        sample_locations,
        address_key='address',
        name_key='name'
    )
    
    # 結果を保存
    if not results_df.empty:
        results_df.to_csv('geocoding_results.csv', index=False, encoding='utf-8')
        print("\n結果をgeocoding_results.csvに保存しました。")
        
        # 地図生成
        generate_map_html(results_df) 