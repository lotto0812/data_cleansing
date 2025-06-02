<<<<<<< HEAD
# 日本の住所ジオコーディングツール

国土地理院の住所検索APIを使用して、日本の住所を緯度経度に変換するPythonツールです。

## 特徴

- 国土地理院APIを使用した高精度な住所検索
- 複数住所の一括変換機能
- 結果の地図表示機能（OpenStreetMap使用）
- APIリクエスト間隔の自動制御

## インストール

```bash
# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows

# 必要なパッケージのインストール
pip install -r requirements.txt
```

## 使用方法

```python
from gsi_geocoder import GSIGeocoder, generate_map_html

# ジオコーダーのインスタンス化
geocoder = GSIGeocoder()

# 単一の住所を変換
result = geocoder.geocode("東京都渋谷区渋谷2-24-12")
if result:
    print(f"緯度: {result['lat']}, 経度: {result['lng']}")

# 複数の住所を一括変換
addresses = [
    {
        'name': '渋谷スクランブルスクエア',
        'address': '東京都渋谷区渋谷2-24-12'
    },
    {
        'name': '東京スカイツリー',
        'address': '東京都墨田区押上1-1-2'
    }
]

# 一括変換を実行
results_df = geocoder.batch_geocode(
    addresses,
    address_key='address',  # 住所が格納されているキー
    name_key='name',        # 名称が格納されているキー（オプション）
    interval=0.5           # リクエスト間隔（秒）
)

# 結果をCSVに保存
results_df.to_csv('results.csv', index=False)

# 地図を生成
generate_map_html(results_df, 'map.html')
```

## 注意事項

1. **利用規約**
   - 国土地理院の利用規約に従って使用してください
   - 出典の明記が必要です（地図生成時は自動で追加されます）

2. **リクエスト制限**
   - デフォルトで0.5秒間隔でリクエストを送信
   - 大量のリクエストは避けてください

3. **商用利用**
   - 商用利用可能ですが、大量リクエストは避けてください
   - 大規模な利用の場合は国土地理院に相談することを推奨

## ライセンス

MIT License

## 謝辞

このツールは[国土地理院](https://www.gsi.go.jp/)の住所検索APIを使用しています。 
=======
# data_cleansing
cleansing for adress, number, ....
>>>>>>> 2d24cbc1b96d4ecc4204612487e55575553093ec
