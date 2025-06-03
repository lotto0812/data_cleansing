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
        elapsed_time = time.time() - self.start_time
        avg_time = elapsed_time / self.current if self.current > 0 else 0
        remaining = avg_time * (self.total - self.current)
        
        # 進捗バーの作成（幅20文字）
        progress = self.current / self.total
        bar_width = 20
        filled = int(bar_width * progress)
        bar = '=' * filled + '-' * (bar_width - filled)
        
        # 進捗情報の表示（同じ行を上書き）
        sys.stdout.write(f'\r[{bar}] {self.current}/{self.total} ({progress*100:.1f}%) '
                        f'残り約{remaining:.0f}秒 | {message}')
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
    print("\n=== 変換前の住所サンプル ===")
    print(df[['name', 'address']].head())
    
    # 進捗トラッカーの初期化
    progress = ProgressTracker(total_count)
    
    def progress_callback(store_name: str, address: str, result: dict) -> None:
        """住所処理の進捗を表示するコールバック関数"""
        # 類似度が0.2未満の場合は詳細を表示
        similarity = result.get('similarity', 0.0)
        message = f"処理中: {store_name}"
        
        if similarity < 0.2:
            print(f"\n\n低類似度アラート（{similarity:.2f}）:")
            print(f"店舗名: {store_name}")
            print(f"入力住所: {address}")
            print(f"マッチした住所: {result.get('matched_address', '不明')}")
            print(f"緯度経度: {result.get('latitude', '不明')}, {result.get('longitude', '不明')}\n")
        
        progress.update(message)
    
    # 緯度経度の取得
    print("\n住所の緯度経度を取得中...")
    result_df = process_dataframe(
        df,
        address_column='address',
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