"""
100件のサンプルレストランデータを生成するスクリプト（不正な住所を含む）
"""

import pandas as pd
import random

# 完全に不正な住所のパターン
invalid_addresses = [
    'あああああああ',
    'どこどこ県どこどこ市',
    '場所不明wwww',
    'ここらへん',
    '電車から見えるとこ',
    'となりのビル',
    '駅前のやつ',
    'そこそこ',
    'あのへん',
    'どっか',
    '東京都あたり',
    '大阪のどっか',
    'ええとねえ',
    'わかりません',
    'そこの角'
]

def generate_store_name():
    store_type = ['和食', '寿司', 'うどん', 'そば', 'ラーメン', '焼肉', '居酒屋', 'カフェ', 'イタリアン', '中華']
    adjectives = ['美味', '本格', '創作', '旬', '匠', '粋', '彩', '和', '新', '老舗']
    names = ['亭', '庵', '屋', '軒', '館', '堂', '店', '房', 'ダイニング', 'キッチン']
    
    if random.random() < 0.3:  # 30%の確率で地名を含む店名
        areas = ['銀座', '渋谷', '新宿', '浅草', '上野', '博多', '天神', '心斎橋', '三宮', '八重洲']
        return f"{random.choice(areas)} {random.choice(adjectives)}{random.choice(store_type)}"
    else:
        return f"{random.choice(adjectives)}{random.choice(store_type)} {random.choice(names)}"

# 100件のデータを生成
data = []
for i in range(100):
    store_code = f"S{str(i+1).zfill(4)}"
    data.append({
        'store_code': store_code,
        'name': generate_store_name(),
        'address': random.choice(invalid_addresses)
    })

# DataFrameを作成
df = pd.DataFrame(data)

# CSVファイルに保存
df.to_csv('sample_restaurants.csv', index=False, encoding='utf-8')
print("100件のサンプルデータを生成しました（完全に不正な住所を含む）。")
print("\n=== サンプルデータ（先頭10件） ===")
print(df.head(10)) 