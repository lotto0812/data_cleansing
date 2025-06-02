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
            r'大阪[府県]?': '大阪府',
            r'京都府?': '京都府',
            r'神奈川県?': '神奈川県',
            r'埼玉県?': '埼玉県',
            r'千葉県?': '千葉県',
            r'愛知県?': '愛知県',
            # 他の道府県も同様に追加可能
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

    def normalize_address(self, address: str) -> str:
        """住所文字列を正規化する"""
        if not isinstance(address, str):
            return address

        # 基本的な正規化
        address = self._basic_normalization(address)
        
        # 都道府県の正規化
        address = self._normalize_prefecture(address)
        
        # 町丁目番地の正規化
        address = self._normalize_chome_banchi(address)
        
        # 建物名の正規化
        address = self._normalize_building(address)
        
        return address.strip()

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
        # 複数の空白を1つに
        text = re.sub(r'\s+', ' ', text)
        return text

    def _normalize_prefecture(self, address: str) -> str:
        """都道府県名を正規化"""
        for pattern, replacement in self.prefecture_patterns.items():
            address = re.sub(f"^{pattern}", replacement, address)
        return address

    def _normalize_chome_banchi(self, address: str) -> str:
        """町丁目・番地・号を正規化"""
        for pattern, replacement in self.chome_patterns.items():
            address = re.sub(pattern, replacement, address)
        return address

    def _normalize_building(self, address: str) -> str:
        """建物名を正規化"""
        for pattern, replacement in self.building_patterns.items():
            address = re.sub(pattern, replacement, address)
        return address

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