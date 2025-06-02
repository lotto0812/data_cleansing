import pandas as pd
import geopandas as gpd
import requests
import zipfile
import io
import sqlite3
import os
from typing import Dict, Optional, List, Tuple
from abc import ABC, abstractmethod
import time
from datetime import datetime
import json

class BaseGeocoder(ABC):
    """ジオコーディングの基底クラス"""
    def __init__(self, db_path: str = 'geocoding.db'):
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """SQLiteデータベースのセットアップ"""
        self.conn = sqlite3.connect(self.db_path)
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY,
                original_address TEXT,
                normalized_address TEXT,
                prefecture TEXT,
                city TEXT,
                town TEXT,
                block TEXT,
                latitude REAL,
                longitude REAL,
                source TEXT,
                last_updated TIMESTAMP
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS addr_idx ON addresses(normalized_address)')
        self.conn.commit()
    
    @abstractmethod
    def download_data(self):
        """データのダウンロード処理"""
        pass
    
    @abstractmethod
    def update_database(self):
        """データベースの更新処理"""
        pass
    
    def normalize_address(self, address: str) -> str:
        """住所の正規化"""
        # 基本的な正規化処理
        address = address.replace('　', ' ')  # 全角スペースを半角に
        address = address.strip()
        return address
    
    def search_address(self, address: str) -> Optional[Dict[str, float]]:
        """住所から緯度経度を検索"""
        normalized = self.normalize_address(address)
        c = self.conn.cursor()
        c.execute('''
            SELECT latitude, longitude 
            FROM addresses 
            WHERE normalized_address = ? 
            OR original_address = ?
            LIMIT 1
        ''', (normalized, address))
        result = c.fetchone()
        
        if result:
            return {'lat': result[0], 'lng': result[1]}
        return None

class GSIGeocoder(BaseGeocoder):
    """国土地理院の位置参照情報を使用したジオコーダー"""
    def __init__(self, db_path: str = 'gsi_geocoding.db'):
        super().__init__(db_path)
        self.base_url = "https://saigai.gsi.go.jp/jusho/download/"
        
    def download_data(self, prefecture: str):
        """指定した都道府県のデータをダウンロード"""
        url = f"{self.base_url}{prefecture}.zip"
        print(f"Downloading data for {prefecture}...")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # CSVファイルを読み込み
                csv_file = [f for f in z.namelist() if f.endswith('.csv')][0]
                with z.open(csv_file) as f:
                    df = pd.read_csv(f, encoding='shift-jis')
                return df
        except Exception as e:
            print(f"Error downloading data: {str(e)}")
            return None
    
    def update_database(self, prefecture_list: List[str] = None):
        """データベースを更新"""
        if prefecture_list is None:
            prefecture_list = ['tokyo', 'osaka', 'kanagawa']  # デフォルトの都道府県リスト
        
        for pref in prefecture_list:
            df = self.download_data(pref)
            if df is not None:
                # データベースに保存
                df['source'] = 'gsi'
                df['last_updated'] = datetime.now()
                df.to_sql('addresses', self.conn, if_exists='append', index=False)
                self.conn.commit()
                print(f"Updated database with {len(df)} records for {pref}")

class OSMGeocoder(BaseGeocoder):
    """OpenStreetMapデータを使用したジオコーダー"""
    def __init__(self, db_path: str = 'osm_geocoding.db'):
        super().__init__(db_path)
        
    def download_data(self, area: str):
        """指定したエリアのOSMデータをダウンロード"""
        try:
            import osmnx as ox
            # エリアの境界を取得
            area_gdf = ox.geocode_to_gdf(area)
            
            # 建物データを取得
            buildings = ox.features_from_place(area, {'building': True})
            
            # 住所データを抽出
            addresses = buildings[buildings['addr:housenumber'].notna()].copy()
            return addresses
        except Exception as e:
            print(f"Error downloading OSM data: {str(e)}")
            return None
    
    def update_database(self, area_list: List[str] = None):
        """データベースを更新"""
        if area_list is None:
            area_list = ['東京都', '大阪府', '神奈川県']  # デフォルトのエリアリスト
        
        for area in area_list:
            gdf = self.download_data(area)
            if gdf is not None:
                # DataFrameに変換
                df = pd.DataFrame({
                    'original_address': gdf['addr:full'],
                    'prefecture': gdf['addr:prefecture'],
                    'city': gdf['addr:city'],
                    'latitude': gdf.geometry.y,
                    'longitude': gdf.geometry.x,
                    'source': 'osm',
                    'last_updated': datetime.now()
                })
                
                # データベースに保存
                df.to_sql('addresses', self.conn, if_exists='append', index=False)
                self.conn.commit()
                print(f"Updated database with {len(df)} records for {area}")

class CommercialGeocoder(BaseGeocoder):
    """商用データベースを使用したジオコーダー"""
    def __init__(self, api_key: str, db_path: str = 'commercial_geocoding.db'):
        super().__init__(db_path)
        self.api_key = api_key
        self.base_url = "https://example.com/api/v1/geocoding"  # 実際のAPIエンドポイントに変更
        
    def download_data(self, area: str = None):
        """APIを使用してデータをダウンロード"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            params = {'area': area} if area else {}
            
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error accessing commercial API: {str(e)}")
            return None
    
    def update_database(self, area_list: List[str] = None):
        """データベースを更新"""
        if area_list is None:
            area_list = ['東京都', '大阪府', '神奈川県']
        
        for area in area_list:
            data = self.download_data(area)
            if data is not None:
                # JSONデータをDataFrameに変換
                df = pd.DataFrame(data)
                df['source'] = 'commercial'
                df['last_updated'] = datetime.now()
                
                # データベースに保存
                df.to_sql('addresses', self.conn, if_exists='append', index=False)
                self.conn.commit()
                print(f"Updated database with {len(df)} records for {area}")

def test_geocoders():
    """ジオコーダーのテスト"""
    # テスト用の住所リスト
    test_addresses = [
        "東京都渋谷区神南1-1-1",
        "大阪府大阪市中央区心斎橋筋2-1-1",
        "神奈川県横浜市中区本町1-1"
    ]
    
    # GSIジオコーダーのテスト
    print("\n=== Testing GSI Geocoder ===")
    gsi_geocoder = GSIGeocoder()
    gsi_geocoder.update_database(['tokyo'])
    
    # OSMジオコーダーのテスト
    print("\n=== Testing OSM Geocoder ===")
    osm_geocoder = OSMGeocoder()
    osm_geocoder.update_database(['東京都'])
    
    # 商用ジオコーダーのテスト
    print("\n=== Testing Commercial Geocoder ===")
    commercial_geocoder = CommercialGeocoder(api_key="your_api_key_here")
    commercial_geocoder.update_database(['東京都'])
    
    # 各ジオコーダーで住所を検索
    geocoders = [
        ('GSI', gsi_geocoder),
        ('OSM', osm_geocoder),
        ('Commercial', commercial_geocoder)
    ]
    
    for name, geocoder in geocoders:
        print(f"\nTesting {name} Geocoder:")
        for addr in test_addresses:
            result = geocoder.search_address(addr)
            if result:
                print(f"Address: {addr}")
                print(f"Result: {result}")
            else:
                print(f"No result found for: {addr}")

if __name__ == "__main__":
    test_geocoders() 