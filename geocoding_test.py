import requests
import pandas as pd
from typing import Dict, Optional, Tuple
import time
import json
from urllib.parse import quote

class AddressGeocoder:
    def __init__(self):
        self.base_url = "https://www.geocoding.jp/api/"
        self.cache = {}  # APIコール削減のためのキャッシュ
        
    def geocode(self, address: str) -> Optional[Dict[str, float]]:
        """
        住所から緯度経度を取得
        
        Args:
            address: 住所文字列
            
        Returns:
            Dict with 'lat' and 'lng' if successful, None otherwise
        """
        # キャッシュチェック
        if address in self.cache:
            return self.cache[address]
            
        # URLエンコード
        encoded_address = quote(address)
        
        try:
            # APIリクエスト
            response = requests.get(
                f"{self.base_url}?q={encoded_address}",
                headers={'accept': 'application/json'}
            )
            
            # APIの利用制限を考慮して1秒待機
            time.sleep(1)
            
            # レスポンスの解析
            if response.status_code == 200:
                # XMLレスポンスをパース
                from xml.etree import ElementTree
                root = ElementTree.fromstring(response.content)
                
                # 緯度経度の取得
                lat = float(root.find('.//lat').text)
                lng = float(root.find('.//lng').text)
                
                result = {'lat': lat, 'lng': lng}
                
                # キャッシュに保存
                self.cache[address] = result
                return result
                
        except Exception as e:
            print(f"Error geocoding address '{address}': {str(e)}")
            
        return None

def test_geocoder():
    # テストデータ
    test_addresses = [
        "東京都渋谷区神南1-1-1",
        "東京都千代田区丸の内1-1-1",
        "大阪府大阪市中央区心斎橋筋2-1-1"
    ]
    
    # ジオコーダーのインスタンス化
    geocoder = AddressGeocoder()
    
    print("=== 緯度経度変換結果 ===")
    for address in test_addresses:
        result = geocoder.geocode(address)
        print(f"\n住所: {address}")
        if result:
            print(f"緯度: {result['lat']}")
            print(f"経度: {result['lng']}")
        else:
            print("変換失敗")
            
    # DataFrameでの使用例
    df = pd.DataFrame({
        '住所': test_addresses
    })
    
    # 緯度経度を追加
    def add_coordinates(row):
        result = geocoder.geocode(row['住所'])
        if result:
            row['緯度'] = result['lat']
            row['経度'] = result['lng']
        return row
        
    df = df.apply(add_coordinates, axis=1)
    
    print("\n=== DataFrame結果 ===")
    print(df)

if __name__ == "__main__":
    test_geocoder() 