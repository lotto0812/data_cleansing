import pandas as pd
import numpy as np
import jaconv
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple
from unicodedata import normalize

class DataNormalizer:
    def __init__(self):
        # 都道府県の正規表現パターン
        self.prefecture_patterns = {
            r'東京都?': '東京都',
            r'大阪[府県]?': '大阪府',
            r'京都府?': '京都府',
            # 必要に応じて他の都道府県も追加
        }
        
        # 店舗名の正規表現パターン
        self.company_patterns = {
            r'株式会社|（株）|\(株\)|\(株式会社\)|㈱': '株式会社',
            r'有限会社|（有）|\(有\)': '有限会社',
        }
        
        # 商品名の表記ゆれ辞書
        self.product_mapping = {}
    
    def normalize_text(self, text: str) -> str:
        """基本的なテキスト正規化を行う"""
        if not isinstance(text, str):
            return text
        
        # 全角を半角に変換（英数字）
        text = jaconv.z2h(text, ascii=True, digit=True)
        # カタカナを全角に統一
        text = jaconv.h2z(text, kana=True)
        # 空白文字の正規化
        text = normalize('NFKC', text)
        # 複数の空白を1つに
        text = re.sub(r'\s+', ' ', text)
        # 前後の空白を削除
        return text.strip()
    
    def normalize_address(self, address: str) -> str:
        """住所の正規化"""
        if not isinstance(address, str):
            return address
        
        # 基本的な正規化
        address = self.normalize_text(address)
        
        # 都道府県の表記統一
        for pattern, replacement in self.prefecture_patterns.items():
            address = re.sub(pattern, replacement, address)
        
        # 「〒」「郵便番号」の削除
        address = re.sub(r'〒\d{3}-?\d{4}|郵便番号\d{3}-?\d{4}', '', address)
        
        return address
    
    def normalize_store_name(self, store_name: str) -> str:
        """店舗名の正規化"""
        if not isinstance(store_name, str):
            return store_name
        
        # 基本的な正規化
        store_name = self.normalize_text(store_name)
        
        # 会社形態の表記統一
        for pattern, replacement in self.company_patterns.items():
            store_name = re.sub(pattern, replacement, store_name)
        
        return store_name
    
    def update_product_mapping(self, product_names: List[str], similarity_threshold: float = 0.8):
        """類似商品名をグループ化し、マッピング辞書を更新"""
        normalized_products = [self.normalize_text(p) for p in product_names if isinstance(p, str)]
        
        # 類似度に基づいてグループ化
        groups: Dict[str, List[str]] = {}
        processed = set()
        
        for i, prod1 in enumerate(normalized_products):
            if prod1 in processed:
                continue
                
            group = [prod1]
            for prod2 in normalized_products[i+1:]:
                if prod2 in processed:
                    continue
                    
                similarity = SequenceMatcher(None, prod1, prod2).ratio()
                if similarity >= similarity_threshold:
                    group.append(prod2)
                    processed.add(prod2)
            
            # グループの代表値（最も短い名前）を選択
            representative = min(group, key=len)
            for prod in group:
                self.product_mapping[prod] = representative
            
            processed.add(prod1)
    
    def normalize_product_name(self, product_name: str) -> str:
        """商品名の正規化"""
        if not isinstance(product_name, str):
            return product_name
        
        # 基本的な正規化
        product_name = self.normalize_text(product_name)
        
        # マッピング辞書に基づく正規化
        return self.product_mapping.get(product_name, product_name)
    
    def normalize_dataframe(self, df: pd.DataFrame, 
                          address_col: str = '住所',
                          store_col: str = '店舗名',
                          product_col: str = '商品名') -> pd.DataFrame:
        """データフレーム全体の正規化"""
        df = df.copy()
        
        # 住所の正規化
        if address_col in df.columns:
            df[address_col] = df[address_col].apply(self.normalize_address)
        
        # 店舗名の正規化
        if store_col in df.columns:
            df[store_col] = df[store_col].apply(self.normalize_store_name)
        
        # 商品名の正規化
        if product_col in df.columns:
            # 商品名のマッピング辞書を更新
            self.update_product_mapping(df[product_col].unique())
            # 商品名の正規化を適用
            df[product_col] = df[product_col].apply(self.normalize_product_name)
        
        return df

# 使用例
if __name__ == "__main__":
    # サンプルデータの作成
    data = {
        '住所': ['東京都渋谷区神南1-1-1', '東京都 渋谷区 神南１－１－１', '東京渋谷区神南1丁目1番1号'],
        '店舗名': ['（株）テストストア', '株式会社テストストア', 'テストストア(株)'],
        '商品名': ['りんご', 'リンゴ', 'アップル'],
        '売上': [1000, 2000, 3000]
    }
    df = pd.DataFrame(data)
    
    # 正規化の実行
    normalizer = DataNormalizer()
    normalized_df = normalizer.normalize_dataframe(df)
    
    print("正規化前のデータ:")
    print(df)
    print("\n正規化後のデータ:")
    print(normalized_df) 