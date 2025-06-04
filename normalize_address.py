import json
import re

class AddressNormalizer:
    def __init__(self, mapping_file: str):
        """
        住所正規化クラスの初期化
        Args:
            mapping_file: 市区町村マッピングのJSONファイルパス
        """
        # マッピングデータの読み込み
        with open(mapping_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.city_mapping = data['mapping']
        
        # 都道府県名のパターン
        self.prefecture_pattern = r'(...??[都道府県])'
        
        # マッピングされている旧市区町村名のパターンを作成
        # 最長一致を優先するため、長い名前から順にマッチングする
        old_cities = sorted(self.city_mapping.keys(), key=len, reverse=True)
        self.old_cities_pattern = '|'.join(map(re.escape, old_cities))
    
    def normalize(self, address: str) -> tuple[str, list[dict]]:
        """
        住所を正規化する
        Args:
            address: 正規化する住所
        Returns:
            tuple[str, list[dict]]: (正規化後の住所, 適用された変更のリスト)
        """
        if not address:
            return address, []
            
        # スペースを削除
        normalized = ''.join(address.split())
        changes = []
        
        # 都道府県名を抽出
        prefecture_match = re.search(self.prefecture_pattern, normalized)
        if not prefecture_match:
            return normalized, changes
        
        prefecture = prefecture_match.group(1)
        
        # 政令指定都市のチェック（市区を含む場合）
        if re.search(r'市[^市]*区', normalized):
            return normalized, changes
        
        # 旧市区町村名を検索し、新市区町村名に置換
        for old_city_full in re.finditer(self.old_cities_pattern, normalized):
            old_city_name = old_city_full.group(0)
            if old_city_name in self.city_mapping:
                # 最新の合併情報を使用（リストの最後の要素）
                latest_merge = self.city_mapping[old_city_name][-1]
                new_city_name = latest_merge['new_city']
                
                # 都道府県名を除いた新市区町村名を使用
                new_city_name = new_city_name.replace(prefecture, '')
                
                # 変更を記録
                changes.append({
                    'old': old_city_name,
                    'new': new_city_name,
                    'merge_date': latest_merge['merge_date']
                })
                
                # 住所を更新
                normalized = normalized.replace(old_city_name, new_city_name)
        
        return normalized, changes

def main():
    # 使用例
    normalizer = AddressNormalizer('市区町村マッピング.json')
    
    # テスト用の住所リスト
    test_addresses = [
        "長崎県西彼杵郡多良見町下郡1234",  # 諫早市に編入
        "山梨県西八代郡上九一色村1234",    # 富士河口湖町と甲府市に分割
        "広島県福山市1234",                # 変更なし（最新の市名）
        "東京都新宿区1234",                # マッピングなし
        "長崎県 西彼杵郡 多良見町 1234",   # スペースを含む
        "長崎県西彼杵郡多良見町１２３４",   # 全角数字
        "静岡県静岡市葵区1234"             # 政令指定都市
    ]
    
    print("住所正規化テスト:")
    print("-" * 80)
    for address in test_addresses:
        normalized, changes = normalizer.normalize(address)
        print(f"\n入力: {address}")
        print(f"出力: {normalized}")
        if changes:
            print("適用された変更:")
            for change in changes:
                print(f"  - {change['old']} → {change['new']} ({change['merge_date']})")
        else:
            print("変更なし")

if __name__ == '__main__':
    main() 