# %% [markdown]
# # 住所の緯度経度変換例
# 
# このノートブックでは、データフレームに含まれる住所を緯度経度に変換する例を示します。

# %%
import pandas as pd
from gsi_geocoder import process_dataframe

# %% [markdown]
# ## データの準備
# 
# 以下の列を含むデータフレームを用意します：
# - 住所
# - 店舗コード
# - 店舗名

# %%
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

df = pd.DataFrame(data)
df

# %% [markdown]
# ## 緯度経度の取得
# 
# データフレームの住所から緯度経度を取得します。

# %%
# 緯度経度の取得
result_df = process_dataframe(
    df,
    address_column='住所',
    store_code_column='店舗コード',
    store_name_column='店舗名',
    output_file='geocoding_results.csv'
)

# 結果の表示
result_df

# %% [markdown]
# ## 結果の確認
# 
# 変換結果には以下の情報が含まれます：
# - 元の店舗情報（店舗コード、店舗名、住所）
# - 正規化された住所
# - マッチした住所
# - 緯度・経度
# - 類似度スコア
# - 住所マッチングレベル（丁目・番地・号）

# %%
# 緯度経度のみを表示
result_df[['店舗名', '住所', 'latitude', 'longitude']] 