# 住所緯度経度変換システム

国土地理院APIを使用して、日本の住所から緯度経度を取得するシステムです。

## 特徴

- Pandas DataFrameに対応
- 店舗情報（店舗コード、店舗名）のサポート
- キャッシュ機能による高速化
- 住所の正規化と類似度計算
- 住所マッチングレベル（丁目・番地・号）の分析

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

```python
import pandas as pd
from gsi_geocoder import process_dataframe

# サンプルデータの作成
data = {
    '店舗コード': ['S001', 'S002'],
    '店舗名': ['六本木店', '銀座店'],
    '住所': [
        '東京都港区六本木1-4-5',
        '東京都中央区銀座4-5-6'
    ]
}

# DataFrameの作成
df = pd.DataFrame(data)

# 緯度経度の取得
result_df = process_dataframe(
    df,
    address_column='住所',
    store_code_column='店舗コード',
    store_name_column='店舗名',
    output_file='geocoding_results.csv'  # オプション：結果をCSVに保存
)

# 結果の表示
print(result_df[['店舗名', '住所', 'latitude', 'longitude']])
```

詳細な使用例は `geocoding_example.py` を参照してください。

## ファイル構成

- `gsi_geocoder.py`: 緯度経度変換の主要機能
- `address_utils.py`: 住所処理のユーティリティ関数
- `geocoding_example.py`: 使用例

## 依存パッケージ

- pandas: データフレーム処理
- requests: API通信

詳細は `requirements.txt` を参照してください。

## ライセンス

MITライセンスの下で公開されています。詳細は `LICENSE` ファイルを参照してください。
