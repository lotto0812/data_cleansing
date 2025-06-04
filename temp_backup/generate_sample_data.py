"""
サンプルデータを生成するスクリプト
"""

import pandas as pd
import random

# 店舗名の構成要素
AREAS = ['渋谷', '新宿', '銀座', '上野', '浅草', '池袋', '秋葉原', '品川', '六本木', '恵比寿']
TYPES = ['和食', 'イタリアン', '中華', 'フレンチ', '焼肉', '寿司', 'カフェ', 'ラーメン', '居酒屋', 'バー']
SUFFIXES = ['店', '亭', '庵', '堂', '軒', 'ダイニング', 'キッチン', 'バル']

# 住所のサンプル（問題のある住所を含む）
VALID_ADDRESSES = [
    {"address": "浦和市美園区美園5丁目50地1", "prefecture": "埼玉県"},  # 問題の住所
    {"address": "渋谷区道玄坂2-1-{}", "prefecture": "東京都"},
    {"address": "新宿区新宿3-{}-{}", "prefecture": "東京都"},
    {"address": "中央区銀座4-{}-{}", "prefecture": "東京都"},
    {"address": "台東区上野5-{}-{}", "prefecture": "東京都"},
    {"address": "台東区浅草1-{}-{}", "prefecture": "東京都"},
    {"address": "豊島区東池袋1-{}-{}", "prefecture": "東京都"},
    {"address": "千代田区外神田{}-{}-{}", "prefecture": "東京都"},
    {"address": "港区港南2-{}-{}", "prefecture": "東京都"},
    {"address": "港区六本木6-{}-{}", "prefecture": "東京都"},
    {"address": "渋谷区恵比寿西1-{}-{}", "prefecture": "東京都"}
]

# 不正な住所のサンプル（10%）
INVALID_ADDRESSES = [
    {"address": "場所不明", "prefecture": ""},
    {"address": "どこかのビル", "prefecture": ""},
    {"address": "駅前のビル", "prefecture": ""},
    {"address": "改装中", "prefecture": ""},
    {"address": "未定", "prefecture": ""}
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
    if template["address"] == "浦和市美園区美園5丁目50地1":  # 問題の住所はそのまま返す
        return template
    
    address_template = template["address"]
    if address_template.count('{}') == 2:
        address = address_template.format(
            random.randint(1, 20),
            random.randint(1, 10)
        )
    else:
        address = address_template.format(
            random.randint(1, 20),
            random.randint(1, 10),
            random.randint(1, 5)
        )
    return {"address": address, "prefecture": template["prefecture"]}

def main():
    """サンプルデータを生成してCSVに保存"""
    # 最初のレコードは必ず問題の住所を含める
    data = [{
        'SAKAYA_DEALER_CODE': 'TEST001',
        'SAKAYA_DEALER_NAME': '浦和美園店',
        'ADDRESS': '浦和市美園区美園5丁目50地1',
        'PREFECTURE': '埼玉県'
    }]
    
    # 残りのデータを生成
    for i in range(1, 30):
        store_code = f"S{str(i+1).zfill(4)}"
        name = generate_store_name()
        
        # 90%は正常な住所、10%は不正な住所
        if random.random() < 0.9:
            address_data = generate_valid_address()
            address = address_data["address"]
            prefecture = address_data["prefecture"]
        else:
            address_data = random.choice(INVALID_ADDRESSES)
            address = address_data["address"]
            prefecture = address_data["prefecture"]
        
        data.append({
            'SAKAYA_DEALER_CODE': store_code,
            'SAKAYA_DEALER_NAME': name,
            'ADDRESS': address,
            'PREFECTURE': prefecture
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