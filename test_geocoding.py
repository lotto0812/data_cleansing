import pandas as pd
from normalize_address import AddressNormalizer
from gsi_geocoder import process_dataframe

def main():
    # テスト用の住所データを作成
    test_data = {
        '店舗コード': ['001', '002', '003', '004', '005', '006', '007'],
        '店舗名': ['諫早支店', '新宿本店', '静岡支店', '福山店', '長岡支店', 'さいたま支店1', 'さいたま支店2'],
        'PREFECTURE': ['長崎県', '東京都', '静岡県', '広島県', '新潟県', '埼玉県', ''],
        '住所': [
            '西彼杵郡多良見町下郡1234',  # 市町村合併のテスト（諫早市に統合）
            '新宿区西新宿2-8-1',         # 変更なしのテスト
            '静岡市葵区追手町9-6',       # 政令指定都市のテスト
            '福山市城見町1-1-1',         # 複数回合併した市のテスト
            '長岡市大手通2-6',           # 複数回合併した市のテスト
            'さいたま市浦和区常盤1-1-1', # 政令指定都市（都道府県あり）
            'さいたま市大宮区吉敷町1-1-1' # 政令指定都市（都道府県なし）
        ]
    }

    # DataFrameを作成
    df = pd.DataFrame(test_data)
    print("テストデータ:")
    print(df)
    print("\n" + "="*80 + "\n")

    # まず住所正規化の結果を確認
    print("住所正規化の過程:")
    print("-" * 80)
    normalizer = AddressNormalizer('市区町村マッピング.json')
    
    for index, row in df.iterrows():
        original_address = row['住所']
        prefecture = row['PREFECTURE']
        
        # 都道府県がある場合は住所の前に追加
        if prefecture and not original_address.startswith(prefecture):
            full_address = f"{prefecture}{original_address}"
        else:
            full_address = original_address
            
        normalized_address, changes = normalizer.normalize(full_address)
        
        print(f"\n[{row['店舗名']}]")
        print(f"都道府県: {prefecture if prefecture else '(なし)'}")
        print(f"入力住所: {original_address}")
        print(f"完全住所: {full_address}")
        print(f"正規化後: {normalized_address}")
        if changes:
            for change in changes:
                print(f"変更内容: {change['old']} → {change['new']} ({change['merge_date']})")
        else:
            print("変更なし")
    
    print("\n" + "="*80 + "\n")

    # 住所を処理
    print("緯度経度変換処理を開始します...")
    
    # 都道府県を住所に追加
    df['normalized_address'] = df.apply(
        lambda row: (
            f"{row['PREFECTURE']}{row['住所']}"
            if row['PREFECTURE'] and not row['住所'].startswith(row['PREFECTURE'])
            else row['住所']
        ),
        axis=1
    )
    
    result_df = process_dataframe(
        df,
        address_column='normalized_address',
        store_code_column='店舗コード',
        store_name_column='店舗名',
        output_file='geocoding_test_results.csv'
    )

    # 結果を表示
    print("\n処理結果:")
    print("-" * 80)
    display_columns = ['店舗名', 'PREFECTURE', '住所', 'normalized_address', 'matched_address', 'latitude', 'longitude', 'similarity']
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    print(result_df[display_columns].to_string())

if __name__ == '__main__':
    main() 