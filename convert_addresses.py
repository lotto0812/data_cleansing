"""
サンプルレストランの住所を変換するスクリプト
"""

import pandas as pd
from gsi_geocoder import process_dataframe
import sys
import time
import os
from math import ceil
from datetime import datetime

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

def process_batch(df_batch, batch_num, timestamp, progress):
    """バッチ単位でデータを処理する"""
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

    output_file = f'geocoding_results_{timestamp}_batch_{str(batch_num).zfill(2)}.csv'
    
    # 都道府県情報を住所に追加
    df_batch = df_batch.copy()
    df_batch['normalized_address'] = df_batch.apply(
        lambda row: (
            f"{str(row['PREFECTURE'])}{row['ADDRESS']}" 
            if pd.notna(row['PREFECTURE']) and pd.notna(row['ADDRESS']) and not str(row['ADDRESS']).startswith(str(row['PREFECTURE']))
            else str(row['ADDRESS'])
        ),
        axis=1
    )
    
    # 緯度経度の取得
    result_df = process_dataframe(
        df_batch,
        address_column='normalized_address',  # 都道府県を含む正規化された住所を使用
        store_code_column='SAKAYA_DEALER_CODE',
        store_name_column='SAKAYA_DEALER_NAME',
        output_file=output_file,
        progress_callback=progress_callback
    )
    
    return result_df, output_file

def main():
    BATCH_SIZE = 10000  # バッチサイズを10000に変更
    
    # 実行時のタイムスタンプを取得（YYYYMMDDHHmm形式）
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    
    # サンプルデータの読み込み
    print("酒屋データを読み込み中...")
    df = pd.read_csv('sample_restaurants.csv', encoding='utf-8')
    
    total_count = len(df)
    print(f"読み込み完了: {total_count}件")
    
    # バッチ数の計算
    num_batches = ceil(total_count / BATCH_SIZE)
    all_low_similarity = []
    output_files = []
    
    print(f"\n{num_batches}バッチに分けて処理を実行します（1バッチ={BATCH_SIZE}件）")
    
    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min((batch_num + 1) * BATCH_SIZE, total_count)
        df_batch = df.iloc[start_idx:end_idx].copy()
        
        print(f"\nバッチ {batch_num + 1}/{num_batches} の処理を開始（{start_idx + 1}～{end_idx}件目）")
        
        # バッチごとの進捗トラッカーの初期化
        progress = ProgressTracker(len(df_batch))
        
        # バッチ処理の実行
        result_df, output_file = process_batch(df_batch, batch_num + 1, timestamp, progress)
        output_files.append(output_file)
        
        # 低類似度データの収集
        low_similarity_batch = result_df[result_df['similarity'] < 0.2]
        all_low_similarity.append(low_similarity_batch)
        
        print(f"\nバッチ {batch_num + 1} の処理完了:")
        print(f"処理件数: {len(df_batch)}件")
        print(f"低類似度件数: {len(low_similarity_batch)}件")
        print(f"結果を {output_file} に保存しました")
    
    # 全バッチの結果を統合
    total_low_similarity = pd.concat(all_low_similarity) if all_low_similarity else pd.DataFrame()
    
    print("\n=== 全体の処理完了 ===")
    print(f"総処理件数: {total_count}件")
    print(f"総低類似度件数: {len(total_low_similarity)}件")
    print("\n出力ファイル:")
    for file in output_files:
        print(f"- {file}")

if __name__ == '__main__':
    main() 