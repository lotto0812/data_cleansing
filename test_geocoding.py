import pandas as pd
import time
from gsi_geocoder import GSIGeocoder
from address_normalizer import JapaneseAddressNormalizer

# テストデータ（Tabelog 20店舗）
test_data = [
    {"name": "鮨 さいとう", "address": "東京都港区六本木1-4-5 アークヒルズ サウスタワー 1F"},
    {"name": "くろぎ", "address": "東京都港区西麻布2-26-21"},
    {"name": "日本料理 山崎", "address": "東京都港区赤坂1-11-6 赤坂テラスハウス 1F"},
    {"name": "天ぷら 巌流島", "address": "東京都渋谷区神宮前4-9-2"},
    {"name": "鮨 おぎ乃", "address": "東京都中央区銀座7-2-8 GINZA GREEN 5F"},
    {"name": "焼鳥 おがわ", "address": "東京都港区六本木7-14-7"},
    {"name": "虎白", "address": "東京都港区南麻布5-2-35"},
    {"name": "にい留", "address": "東京都港区西麻布2-25-13"},
    {"name": "銀座 小十", "address": "東京都中央区銀座7-5-4 毛利ビル 7F"},
    {"name": "鮨 さかい", "address": "東京都港区六本木1-4-5 アークヒルズ サウスタワー 1F"},
    {"name": "すし処 みや古分店", "address": "東京都渋谷区恵比寿1-22-20"},
    {"name": "鮨 なんば", "address": "東京都港区六本木6-8-7 トライセブン六本木ビル 2F"},
    {"name": "天ぷら 島家", "address": "東京都渋谷区代官山町8-6"},
    {"name": "焼鳥 市松", "address": "東京都渋谷区神宮前3-42-2"},
    {"name": "鮨 まつもと", "address": "東京都港区六本木7-18-12 港ビル 1F"},
    {"name": "日本料理 龍吟", "address": "東京都港区赤坂9-7-4 D0-Box 8F"},
    {"name": "すし匠", "address": "東京都中央区銀座8-3-1 GINZA888 5F"},
    {"name": "焼鳥 とりそば なかお", "address": "東京都渋谷区神宮前6-25-14"},
    {"name": "鮨 はしもと", "address": "東京都港区六本木6-3-7"},
    {"name": "天ぷら 近藤", "address": "東京都渋谷区神宮前5-10-1"}
]

def main():
    # 入力データをCSVに保存
    input_df = pd.DataFrame(test_data)
    input_df.to_csv('test_restaurants.csv', index=False, encoding='utf-8')
    print(f"テストデータを保存しました: test_restaurants.csv ({len(test_data)}件)")

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