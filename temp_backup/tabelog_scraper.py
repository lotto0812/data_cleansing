"""
食べログからレストランデータを取得し、住所を緯度経度に変換するスクリプト
"""

import time
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re
from urllib.parse import urljoin

def get_restaurant_list(area_url: str, max_count: int = 100) -> List[Dict]:
    """
    食べログの検索結果ページからレストラン情報を取得
    
    Parameters:
    -----------
    area_url : str
        エリアのURL
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
        # ページURLの生成
        if page == 1:
            url = area_url
        else:
            url = f"{area_url}{page}/"
            
        try:
            # ページの取得
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # レストラン要素の取得
            restaurant_elements = soup.select('div.list-rst__wrap')
            
            if not restaurant_elements:
                break
                
            for element in restaurant_elements:
                if len(restaurants) >= max_count:
                    break
                    
                try:
                    # 店舗名の取得
                    name_element = element.select_one('h4.list-rst__rst-name a')
                    name = name_element.text.strip() if name_element else "不明"
                    
                    # 店舗URLの取得
                    url = name_element['href'] if name_element else None
                    
                    # 住所の取得
                    address_element = element.select_one('p.list-rst__address span')
                    address = address_element.text.strip() if address_element else "不明"
                    
                    # 評価の取得
                    rating_element = element.select_one('span.c-rating__val')
                    rating = rating_element.text.strip() if rating_element else "0.0"
                    
                    restaurants.append({
                        'name': name,
                        'address': address,
                        'rating': rating,
                        'url': url
                    })
                    
                except Exception as e:
                    print(f"店舗データの解析中にエラー: {e}")
                    continue
            
            # インターバルを設定
            time.sleep(random.uniform(3, 5))
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"ページ取得中にエラー: {e}")
            break
            
    return restaurants[:max_count]

def main():
    # 東京都内の人気レストランを取得
    area_url = "https://tabelog.com/tokyo/rstLst/lunch/rank/"
    
    print("レストラン情報を取得中...")
    restaurants = get_restaurant_list(area_url)
    
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