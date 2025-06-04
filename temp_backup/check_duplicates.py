import csv
from collections import defaultdict

def check_duplicates(input_file: str) -> None:
    """
    重複している市区町村を確認
    """
    # 市区町村ごとの出現回数を記録
    city_count = defaultdict(list)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # ヘッダーをスキップ
        
        for row in reader:
            if len(row) < 4:
                continue
                
            merge_date = row[0].strip()
            prefecture = row[1].strip()
            new_city = row[2].strip()
            old_city = row[3].strip()
            
            # 都道府県名を含めた市区町村名を作成
            old_city_full = f"{prefecture}{old_city}"
            
            # 情報を記録
            city_count[old_city_full].append({
                "new_city": f"{prefecture}{new_city}",
                "merge_date": merge_date
            })
    
    # 重複している市区町村を表示
    print("\n重複している市区町村:")
    print("-" * 80)
    for city, records in city_count.items():
        if len(records) > 1:
            print(f"\n{city}:")
            for record in records:
                print(f"  → {record['new_city']} ({record['merge_date']})")
    
    # 統計情報を表示
    duplicates = sum(1 for records in city_count.values() if len(records) > 1)
    print(f"\n統計:")
    print(f"- 合計市区町村数: {len(city_count)}")
    print(f"- 重複している市区町村数: {duplicates}")
    print(f"- 重複を含む総行数: {sum(len(records) for records in city_count.values())}")

def main():
    input_file = '平成11年以降合併市区町村_正規化.csv'
    check_duplicates(input_file)

if __name__ == '__main__':
    main() 