import pandas as pd
import time
from gsi_geocoder import GSIGeocoder
from address_normalizer import JapaneseAddressNormalizer

def main():
    # CSVからテストデータを読み込み
    try:
        input_df = pd.read_csv('test_data.csv', encoding='utf-8')
        print(f"テストデータを読み込みました: {len(input_df)}件")
    except Exception as e:
        print(f"テストデータの読み込みに失敗しました: {str(e)}")
        return

    # データフレームを辞書のリストに変換
    test_data = input_df.to_dict('records')
    
    # ジオコーダーの初期化
    geocoder = GSIGeocoder()
    
    # ジオコーディングの実行
    print("\nジオコーディングを開始します...")
    results_df = geocoder.batch_geocode(
        test_data,
        address_key='address',
        name_key='name',
        interval=1.0  # APIの負荷を考慮して1秒間隔に変更
    )
    
    # 結果の保存
    if not results_df.empty:
        results_df.to_csv('geocoding_results.csv', index=False, encoding='utf-8')
        print(f"\n結果を保存しました: geocoding_results.csv ({len(results_df)}件)")
        
        # 成功率の計算
        success_rate = (len(results_df) / len(test_data)) * 100
        print(f"\n処理結果:")
        print(f"- 入力データ数: {len(test_data)}")
        print(f"- 成功件数: {len(results_df)}")
        print(f"- 成功率: {success_rate:.1f}%")
        
        # 地図の生成
        from gsi_geocoder import generate_map_html
        generate_map_html(results_df, 'test_results_map.html')
        print("\n地図を生成しました: test_results_map.html")

if __name__ == "__main__":
    main() 