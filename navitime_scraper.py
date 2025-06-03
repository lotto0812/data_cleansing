"""
NAVITIMEからレストランデータを取得し、住所を緯度経度に変換するスクリプト
"""

import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from urllib.parse import urljoin

def get_restaurant_list(base_url: str, max_count: int = 100) -> List[Dict]:
    """
    NAVITIMEの検索結果ページからレストラン情報を取得
    
    Parameters:
    -----------
    base_url : str
        検索ページのURL
    max_count : int
        取得する最大件数
        
    Returns:
    --------
    List[Dict]
        レストラン情報のリスト
    """
    restaurants = []
    page = 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    while len(restaurants) < max_count:
        try:
            # ページの取得
            response = requests.get(base_url, headers=headers, params={'page': page})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # レストラン要素の取得
            restaurant_elements = soup.select('div.spot_list article')
            
            if not restaurant_elements:
                break
                
            for element in restaurant_elements:
                if len(restaurants) >= max_count:
                    break
                    
                try:
                    # 店舗名の取得
                    name_element = element.select_one('div.spot_head h3')
                    name = name_element.text.strip() if name_element else "不明"
                    
                    # 住所の取得
                    address_element = element.select_one('div.spot_body p.address')
                    address = address_element.text.strip() if address_element else "不明"
                    
                    # 電話番号の取得（あれば）
                    tel_element = element.select_one('div.spot_body p.tel')
                    tel = tel_element.text.strip() if tel_element else ""
                    
                    restaurants.append({
                        'name': name,
                        'address': address,
                        'tel': tel
                    })
                    
                except Exception as e:
                    print(f"店舗データの解析中にエラー: {e}")
                    continue
            
            # インターバルを設定
            time.sleep(random.uniform(2, 4))
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"ページ取得中にエラー: {e}")
            break
            
    return restaurants[:max_count]

def main():
    # レストラン一覧を取得
    base_url = "https://www.navitime.co.jp/category/0302002/"
    
    print("レストラン情報を取得中...")
    restaurants = get_restaurant_list(base_url)
    
    # DataFrameに変換
    df = pd.DataFrame(restaurants)
    
    # CSVに保存
    df.to_csv('restaurants_raw.csv', index=False, encoding='utf-8')
    print(f"取得完了: {len(restaurants)}件")
    print("データを restaurants_raw.csv に保存しました")
    
    # 住所の確認
    print("\n=== 住所サンプル ===")
    print(df[['name', 'address']].head())

if __name__ == '__main__':
    main() 