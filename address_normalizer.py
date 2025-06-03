import re
import jaconv
from typing import Dict, List, Optional
from unicodedata import normalize

class JapaneseAddressNormalizer:
    def __init__(self):
        # 都道府県の正規表現パターン
        self.prefecture_patterns = {
            r'北海道': '北海道',
            r'東京都?': '東京都',
            r'大阪府?(?!市)': '大阪府',  # 「大阪市」にマッチしないように修正
            r'京都府?': '京都府',
            r'神奈川県?': '神奈川県',
            r'埼玉県?': '埼玉県',
            r'千葉県?': '千葉県',
            r'愛知県?': '愛知県',
            # 他の道府県も同様に追加可能
        }
        
        # 政令指定都市の正規表現パターン
        self.city_patterns = {
            r'^大阪市': '大阪府大阪市',  # 先頭の「大阪市」を「大阪府大阪市」に変換
            r'京都市': '京都市',
            r'神戸市': '神戸市',
            r'名古屋市': '名古屋市',
            r'横浜市': '横浜市',
            r'札幌市': '札幌市',
            # 他の政令指定都市も同様に追加可能
        }
        
        # 町丁目の正規表現パターン
        self.chome_patterns = {
            r'(\d+)\s*(?:丁目|丁|－|ー|の)': r'\1丁目',
            r'(\d+)\s*(?:番地?|番号?|－|ー|の)(?!\d)': r'\1番',
            r'(\d+)\s*(?:号|－|ー|の)(?!\d)': r'\1号',
        }
        
        # 建物名の正規化パターン
        self.building_patterns = {
            r'ビル(?:ディング)?': 'ビル',
            r'マンション': 'マンション',
            r'アパート': 'アパート',
        }

    def _extract_house_number(self, address: str) -> tuple[str, str]:
        """住所から番地号を抽出し、残りの住所と番地号を返す"""
        number_match = re.search(r'([0-9-]+)(?:番地?|号)?$', address)
        if number_match:
            number = number_match.group(1)
            base_address = address[:number_match.start()].strip()
            return base_address, number
        return address, ""

    def _normalize_house_number(self, number: str) -> str:
        """番地号を正規化"""
        if not number:
            return ""
        
        # ハイフン区切りの番号を処理
        parts = number.split('-')
        
        if len(parts) == 3:  # 1-3-16 形式
            return f"{parts[0]}丁目{parts[1]}番{parts[2]}号"
        elif len(parts) == 2:  # 3-16 形式
            return f"{parts[0]}番{parts[1]}号"
        else:  # 単独の番号
            return f"{number}番"

    def normalize_address(self, address: str) -> str:
        """住所文字列を正規化する"""
        if not isinstance(address, str):
            return address

        # 基本的な正規化
        address = self._basic_normalization(address)
        
        # 番地号を抽出
        base_address, house_number = self._extract_house_number(address)
        
        # 政令指定都市の処理（都道府県の前に実行）
        normalized_address = base_address
        for pattern, replacement in self.city_patterns.items():
            if re.match(pattern, normalized_address):
                normalized_address = re.sub(pattern, replacement, normalized_address)
                break
        
        # 都道府県の正規化
        for pattern, replacement in self.prefecture_patterns.items():
            normalized_address = re.sub(f"^{pattern}", replacement, normalized_address)
        
        # 町丁目番地の正規化
        for pattern, replacement in self.chome_patterns.items():
            normalized_address = re.sub(pattern, replacement, normalized_address)
        
        # 正規化された番地号を追加
        if house_number:
            normalized_house_number = self._normalize_house_number(house_number)
            normalized_address = f"{normalized_address}{normalized_house_number}"
        
        return normalized_address.strip()

    def _basic_normalization(self, text: str) -> str:
        """基本的なテキスト正規化を行う"""
        # 全角英数を半角に変換
        text = jaconv.z2h(text, ascii=True, digit=True)
        # カタカナを全角に統一
        text = jaconv.h2z(text, kana=True)
        # Unicode正規化
        text = normalize('NFKC', text)
        # 郵便番号を削除
        text = re.sub(r'〒\d{3}-?\d{4}|郵便番号\d{3}-?\d{4}', '', text)
        # 文頭の「・」を削除
        text = re.sub(r'^[・]+', '', text)
        # 特殊文字（☆、★、※など）を削除
        text = re.sub(r'[☆★※♪♡♥❤︎❀✿✽✾✤✣❉❋❆❅⭐️]+', '', text)
        # 複数の空白を1つに
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_components(self, address: str) -> Dict[str, Optional[str]]:
        """住所から構成要素を抽出する"""
        normalized = self.normalize_address(address)
        
        # 都道府県を抽出
        prefecture = None
        for pattern in self.prefecture_patterns.values():
            if pattern in normalized:
                prefecture = pattern
                break
        
        # 建物名を抽出
        building = None
        building_match = re.search(r'(.+(?:ビル|マンション|アパート))', normalized)
        if building_match:
            building = building_match.group(1)
        
        return {
            'normalized_address': normalized,
            'prefecture': prefecture,
            'building': building
        }

if __name__ == "__main__":
    # 使用例
    normalizer = JapaneseAddressNormalizer()
    
    test_addresses = [
        "東京都渋谷区神南１－１－１",
        "東京都 渋谷区 神南1丁目1番1号",
        "〒150-0041 東京都渋谷区神南1丁目",
        "東京都渋谷区神南1-1-1 渋谷マンション101",
    ]
    
    for addr in test_addresses:
        normalized = normalizer.normalize_address(addr)
        components = normalizer.extract_components(addr)
        print(f"\n原文: {addr}")
        print(f"正規化: {normalized}")
        print(f"構成要素: {components}") 