import pandas as pd
import requests
import time
from typing import Dict, List, Optional
import json

# サンプルの店舗データ
sample_restaurants = [
    {
        'name': '鮨 さいとう',
        'address': '東京都港区六本木1-4-5 アークヒルズ サウスタワー 1F'
    },
    {
        'name': 'すきやばし次郎',
        'address': '東京都中央区銀座4-2-15 塚本ビル1F'
    },
    {
        'name': '天ぷら はせ川',
        'address': '東京都港区西麻布3-13-3'
    },
    {
        'name': '虎白',
        'address': '東京都千代田区丸の内2-7-2 JPタワー 35F'
    },
    {
        'name': 'にくの匠 三芳',
        'address': '東京都中央区銀座7-8-7 GINZA GREEN 9F'
    },
    {
        'name': '鮨 おぎ乃',
        'address': '東京都渋谷区神南1-20-15'
    },
    {
        'name': '龍吟',
        'address': '東京都港区赤坂9-7-4 D0ビル'
    },
    {
        'name': 'カンテサンス',
        'address': '東京都渋谷区猿楽町29-9'
    },
    {
        'name': '傳',
        'address': '東京都渋谷区神宮前5-10-1 GYRE B1F'
    },
    {
        'name': 'レフェルヴェソンス',
        'address': '東京都中央区日本橋3-2-14'
    }
]

def geocode_address(address: str) -> Optional[Dict[str, float]]:
    """国土地理院APIを使用して住所を緯度経度に変換"""
    try:
        # 建物名や階数を除去（より正確な検索のため）
        address = address.split(' ')[0]  # 最初のスペースまでを使用
        
        # 国土地理院の住所検索APIを使用
        url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={address}"
        response = requests.get(url)
        response.raise_for_status()
        
        results = response.json()
        if results and len(results) > 0:
            # 最初の結果を使用
            coordinates = results[0]['geometry']['coordinates']
            return {
                'lng': coordinates[0],  # 経度
                'lat': coordinates[1]   # 緯度
            }
    except Exception as e:
        print(f"Error geocoding address: {str(e)}")
    
    return None

def process_restaurants():
    """レストランの住所を緯度経度に変換して結果を表示"""
    results = []
    
    for restaurant in sample_restaurants:
        print(f"\n処理中: {restaurant['name']}")
        
        # APIの負荷を考慮して少し待機
        time.sleep(0.5)
        
        result = geocode_address(restaurant['address'])
        if result:
            results.append({
                'name': restaurant['name'],
                'address': restaurant['address'],
                'lat': result['lat'],
                'lng': result['lng']
            })
            print(f"変換成功: 緯度 {result['lat']}, 経度 {result['lng']}")
        else:
            print(f"変換失敗: {restaurant['address']}")
    
    # 結果をDataFrameに変換
    if results:
        df = pd.DataFrame(results)
        print("\n=== 変換結果 ===")
        print(df)
        
        # CSVファイルに保存
        df.to_csv('restaurant_coordinates_gsi.csv', index=False, encoding='utf-8')
        print("\n結果をrestaurant_coordinates_gsi.csvに保存しました。")
        
        # 地図表示用のHTMLファイルを生成
        generate_map_html(df)
    else:
        print("\n変換に成功した結果がありません。")

def generate_map_html(df: pd.DataFrame):
    """結果を地図上にプロットするHTMLファイルを生成"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Restaurant Locations</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            #map { height: 600px; }
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([35.6762, 139.6503], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
    """
    
    # マーカーを追加
    for _, row in df.iterrows():
        html_content += f"""
            L.marker([{row['lat']}, {row['lng']}])
                .bindPopup('{row['name']}<br>{row['address']}')
                .addTo(map);
        """
    
    html_content += """
        </script>
    </body>
    </html>
    """
    
    with open('restaurant_map.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("\n地図をrestaurant_map.htmlに保存しました。")

if __name__ == "__main__":
    process_restaurants() 