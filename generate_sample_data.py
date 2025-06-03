"""
サンプルデータを生成するスクリプト
"""

import pandas as pd
import random

# 店舗名の構成要素
AREAS = ['渋谷', '新宿', '銀座', '上野', '浅草', '池袋', '秋葉原', '品川', '六本木', '恵比寿']
TYPES = ['和食', 'イタリアン', '中華', 'フレンチ', '焼肉', '寿司', 'カフェ', 'ラーメン', '居酒屋', 'バー']
SUFFIXES = ['店', '亭', '庵', '堂', '軒', 'ダイニング', 'キッチン', 'バル']

# 住所のサンプル（90%は正常な住所）
VALID_ADDRESSES = [
    "東京都渋谷区道玄坂2-1-{}",
    "東京都新宿区新宿3-{}-{}",
    "東京都中央区銀座4-{}-{}",
    "東京都台東区上野5-{}-{}",
    "東京都台東区浅草1-{}-{}",
    "東京都豊島区東池袋1-{}-{}",
    "東京都千代田区外神田{}-{}-{}",
    "東京都港区港南2-{}-{}",
    "東京都港区六本木6-{}-{}",
    "東京都渋谷区恵比寿西1-{}-{}"
]

# 不正な住所のサンプル（10%）
INVALID_ADDRESSES = [
    "場所不明",
    "どこかのビル",
    "駅前のビル",
    "改装中",
    "未定"
]

def generate_store_name():
    """ランダムな店舗名を生成"""
    area = random.choice(AREAS)
    type_ = random.choice(TYPES)
    suffix = random.choice(SUFFIXES)
    return f"{area} {type_} {suffix}"

def generate_valid_address():
    """正常な住所を生成"""
    template = random.choice(VALID_ADDRESSES)
    if template.count('{}') == 2:
        return template.format(
            random.randint(1, 20),
            random.randint(1, 10)
        )
    else:
        return template.format(
            random.randint(1, 20),
            random.randint(1, 10),
            random.randint(1, 5)
        )

def main():
    """サンプルデータを生成してCSVに保存"""
    # 100件のデータを生成
    data = []
    for i in range(100):
        store_code = f"S{str(i+1).zfill(4)}"
        name = generate_store_name()
        
        # 90%は正常な住所、10%は不正な住所
        if random.random() < 0.9:
            address = generate_valid_address()
        else:
            address = random.choice(INVALID_ADDRESSES)
        
        data.append({
            'store_code': store_code,
            'name': name,
            'address': address
        })
    
    # DataFrameに変換
    df = pd.DataFrame(data)
    
    # CSVに保存
    df.to_csv('sample_restaurants.csv', index=False, encoding='utf-8')
    print(f"サンプルデータを生成しました（{len(df)}件）")
    print("\n=== サンプル ===")
    print(df.head())

if __name__ == '__main__':
    main() 