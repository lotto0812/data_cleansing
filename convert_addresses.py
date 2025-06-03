"""
サンプルレストランの住所を変換するスクリプト
"""

import pandas as pd
from gsi_geocoder import process_dataframe
import sys
import time

class ProgressTracker:
    def __init__(self, total):
        self.total = total
        self.current = 0
        self.start_time = time.time()
    
    def update(self, message):
        self.current += 1
        # 進捗情報は最終行のみ更新
        progress = self.current / self.total * 100
        sys.stdout.write(f'\r処理進捗: {self.current}/{self.total} ({progress:.1f}%)')
        sys.stdout.flush()
        
        if self.current == self.total:
            sys.stdout.write('\n')
            sys.stdout.flush()

def main():
    # サンプルデータの読み込み
    print("レストランデータを読み込み中...")
    df = pd.read_csv('sample_restaurants.csv', encoding='utf-8')
    
    total_count = len(df)
    print(f"読み込み完了: {total_count}件")
    
    # 進捗トラッカーの初期化
    progress = ProgressTracker(total_count)
    
    def progress_callback(store_name: str, address: str, result: dict) -> None:
        """住所処理の進捗を表示するコールバック関数"""
        # 類似度が0.2未満の場合のみ詳細を表示
        similarity = result.get('similarity', 0.0)
        store_code = result.get('store_code', '不明')
        
        if similarity < 0.2:
            print(f"\n低類似度アラート（{similarity:.2f}）:")
            print(f"店舗コード: {store_code}")
            print(f"店舗名: {store_name}")
            print(f"入力住所: {address}")
            print(f"マッチした住所: {result.get('matched_address', '不明')}")
            print(f"緯度経度: {result.get('latitude', '不明')}, {result.get('longitude', '不明')}")
        
        # 進捗バーの更新（表示なし）
        progress.update("")
    
    # 緯度経度の取得
    print("\n住所の緯度経度を取得中...")
    result_df = process_dataframe(
        df,
        address_column='address',
        store_code_column='store_code',
        store_name_column='name',
        output_file='geocoding_results.csv',
        progress_callback=progress_callback
    )
    
    # 類似度が0.2未満の結果の集計
    low_similarity = result_df[result_df['similarity'] < 0.2]
    
    print("\n=== 処理完了 ===")
    print(f"総処理件数: {total_count}件")
    print(f"低類似度件数: {len(low_similarity)}件")
    print(f"結果を geocoding_results.csv に保存しました")

if __name__ == '__main__':
    main() 