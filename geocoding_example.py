"""
住所の緯度経度変換例

このスクリプトでは、データフレームに含まれる住所を緯度経度に変換する例を示します。
"""

import pandas as pd
from gsi_geocoder import process_dataframe

def main():
    # サンプルデータの作成
    data = {
        '店舗コード': ['S001', 'S002', 'S003'],
        '店舗名': ['六本木店', '銀座店', '新宿店'],
        '住所': [
            '東京都港区六本木1-4-5',
            '東京都中央区銀座4-5-6',
            '東京都新宿区新宿3-1-2'
        ]
    }

    print("=== サンプルデータ ===")
    df = pd.DataFrame(data)
    print(df)
    print("\n")

    print("=== 緯度経度の取得 ===")
    # 緯度経度の取得
    result_df = process_dataframe(
        df,
        address_column='住所',
        store_code_column='店舗コード',
        store_name_column='店舗名',
        output_file='geocoding_results.csv'
    )

    print("\n=== 変換結果 ===")
    print("結果は以下の情報を含みます：")
    print("- 元の店舗情報（店舗コード、店舗名、住所）")
    print("- 正規化された住所")
    print("- マッチした住所")
    print("- 緯度・経度")
    print("- 類似度スコア")
    print("- 住所マッチングレベル（丁目・番地・号）")
    print("\n")

    # 結果の表示
    print(result_df)
    print("\n")

    # 緯度経度のみを表示
    print("=== 緯度経度のみの表示 ===")
    print(result_df[['店舗名', '住所', 'latitude', 'longitude']])

if __name__ == '__main__':
    main() 