"""
サンプルレストランの住所を変換するスクリプト
"""

import pandas as pd
from gsi_geocoder import process_dataframe

def main():
    # サンプルデータの読み込み
    print("レストランデータを読み込み中...")
    df = pd.read_csv('sample_restaurants.csv', encoding='utf-8')
    
    print(f"読み込み完了: {len(df)}件")
    print("\n=== 変換前の住所サンプル ===")
    print(df[['name', 'address']].head())
    
    # 緯度経度の取得
    print("\n住所の緯度経度を取得中...")
    result_df = process_dataframe(
        df,
        address_column='address',
        store_name_column='name',
        output_file='geocoding_results.csv'
    )
    
    print("\n=== 変換結果 ===")
    print("以下の情報を含む結果を geocoding_results.csv に保存しました：")
    print("- 店舗情報（店舗名、住所）")
    print("- 正規化された住所")
    print("- マッチした住所")
    print("- 緯度・経度")
    print("- 類似度スコア")
    print("- 住所マッチングレベル（丁目・番地・号）")
    
    # 結果の表示
    print("\n=== 変換結果サンプル ===")
    print(result_df[['name', 'address', 'normalized_address', 'latitude', 'longitude']].head())

if __name__ == '__main__':
    main() 