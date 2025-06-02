import pandas as pd
import MeCab
import re
from typing import Dict, List
from difflib import SequenceMatcher

class AddressMatcher:
    def __init__(self):
        self.address_levels = {
            '都道府県': 1,
            '市区町村': 2,
            '町名': 3,
            '番地': 4,
            '建物名': 5
        }
        self.tagger = MeCab.Tagger()
        
    def parse_address(self, address: str) -> Dict[str, str]:
        """住所を階層的に分解"""
        components = {
            '都道府県': '',
            '市区町村': '',
            '町名': '',
            '番地': '',
            '建物名': ''
        }
        
        # 都道府県の抽出
        prefecture_pattern = r'(東京都|北海道|(?:京都|大阪)府|(?:神奈川|埼玉|千葉|.+)県)'
        prefecture_match = re.search(prefecture_pattern, address)
        if prefecture_match:
            components['都道府県'] = prefecture_match.group(1)
            
        # 市区町村の抽出
        city_pattern = r'(?:市|区|町|村)(?=[\u3400-\u9FFF]|$)'
        city_matches = list(re.finditer(city_pattern, address))
        if city_matches:
            last_city_match = city_matches[-1]
            start_pos = 0
            if prefecture_match:
                start_pos = prefecture_match.end()
            components['市区町村'] = address[start_pos:last_city_match.end()]
            
        return components
    
    def calculate_similarity(self, addr1: str, addr2: str) -> float:
        """階層的な類似度計算"""
        comp1 = self.parse_address(addr1)
        comp2 = self.parse_address(addr2)
        
        total_weight = 0
        weighted_similarity = 0
        
        for level, weight in self.address_levels.items():
            if comp1[level] and comp2[level]:
                # 各階層での類似度を計算
                level_similarity = self.calculate_level_similarity(
                    comp1[level], comp2[level], level
                )
                weighted_similarity += level_similarity * weight
                total_weight += weight
                
        return weighted_similarity / total_weight if total_weight > 0 else 0.0
    
    def calculate_level_similarity(self, text1: str, text2: str, level: str) -> float:
        """各階層でのテキスト類似度計算"""
        if level in ['都道府県', '市区町村']:
            # 完全一致で判定
            return 1.0 if text1 == text2 else 0.0
        else:
            # その他の部分はSequenceMatcherで比較
            return SequenceMatcher(None, text1, text2).ratio()

def test_address_matcher():
    # テストデータ
    test_addresses = [
        "東京都渋谷区神南1-1-1",
        "東京都 渋谷区 神南１－１－１",
        "東京都渋谷区神南一丁目1番1号",
        "神奈川県横浜市中区本町1-1",
        "神奈川県横浜市中区本町１丁目１番",
        "大阪府大阪市中央区心斎橋筋2-1-1",
        "大阪市中央区心斎橋筋2丁目1-1"
    ]
    
    # AddressMatcherのインスタンス化
    matcher = AddressMatcher()
    
    print("=== 住所パース結果 ===")
    for addr in test_addresses[:3]:  # 最初の3つの住所のみパース結果を表示
        components = matcher.parse_address(addr)
        print(f"\n住所: {addr}")
        for level, value in components.items():
            print(f"{level}: {value}")
    
    print("\n=== 類似度計算結果 ===")
    # 類似度の計算と表示
    for i in range(len(test_addresses)):
        for j in range(i + 1, len(test_addresses)):
            similarity = matcher.calculate_similarity(
                test_addresses[i], test_addresses[j]
            )
            print(f"\n住所1: {test_addresses[i]}")
            print(f"住所2: {test_addresses[j]}")
            print(f"類似度: {similarity:.3f}")

if __name__ == "__main__":
    test_address_matcher() 