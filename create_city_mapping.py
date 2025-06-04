import csv
from collections import defaultdict
import json

def create_mapping(input_file: str, output_file: str) -> None:
    """
    旧市区町村名から新市町村名へのマッピングを作成
    """
    # マッピング用の辞書を初期化
    mapping = defaultdict(list)
    total_rows = 0
    skipped_rows = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        
        for row in reader:
            total_rows += 1
            if len(row) < 4:
                skipped_rows += 1
                print(f"スキップされた行: {row}")
                continue
                
            merge_date = row[0].strip()
            prefecture = row[1].strip()
            new_city = row[2].strip()
            old_city = row[3].strip()
            
            if not all([merge_date, prefecture, new_city, old_city]):
                skipped_rows += 1
                print(f"空の値を含む行: {row}")
                continue
            
            # 都道府県名を含めた市区町村名を作成
            old_city_full = f"{prefecture}{old_city}"
            new_city_full = f"{prefecture}{new_city}"
            
            # マッピング情報を作成
            mapping[old_city_full].append({
                "new_city": new_city_full,
                "merge_date": merge_date
            })
    
    # 結果を整形
    result = {
        "description": "旧市区町村名から新市町村名へのマッピング",
        "total_rows": total_rows,
        "skipped_rows": skipped_rows,
        "total_old_cities": len(mapping),
        "mapping": dict(mapping)  # defaultdictをdictに変換
    }
    
    # JSON形式で保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n処理結果:")
    print(f"- 合計行数: {total_rows}")
    print(f"- スキップされた行: {skipped_rows}")
    print(f"- 処理された旧市区町村数: {len(mapping)}")
    print(f"\nマッピングが完了しました。出力ファイル: {output_file}")

def main():
    input_file = '平成11年以降合併市区町村_正規化.csv'
    output_file = '市区町村マッピング.json'
    create_mapping(input_file, output_file)

if __name__ == '__main__':
    main() 