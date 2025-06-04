import unittest
from normalize_address import AddressNormalizer

class TestAddressNormalizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.normalizer = AddressNormalizer('市区町村マッピング.json')

    def test_basic_normalization(self):
        """基本的な正規化のテスト"""
        test_cases = [
            # 基本的な変換
            {
                'input': '長崎県西彼杵郡多良見町下郡1234',
                'expected': '諫早市下郡1234',
                'should_change': True
            },
            # 複数回合併した市の最新の状態
            {
                'input': '広島県福山市1234',
                'expected': '福山市1234',
                'should_change': True
            },
            # 分割された村
            {
                'input': '山梨県西八代郡上九一色村1234',
                'expected': '甲府市1234',  # 最新の合併先
                'should_change': True
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                normalized, changes = self.normalizer.normalize(case['input'])
                self.assertEqual(normalized, case['expected'])
                self.assertEqual(bool(changes), case['should_change'])

    def test_no_changes_needed(self):
        """変更が不要なケースのテスト"""
        test_cases = [
            # マッピングに存在しない住所
            {
                'input': '東京都新宿区1234',
                'expected': '東京都新宿区1234'
            },
            # 空文字列
            {
                'input': '',
                'expected': ''
            },
            # 都道府県名のない住所
            {
                'input': '新宿区1234',
                'expected': '新宿区1234'
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                normalized, changes = self.normalizer.normalize(case['input'])
                self.assertEqual(normalized, case['expected'])
                self.assertEqual(len(changes), 0)

    def test_complex_cases(self):
        """複雑なケースのテスト"""
        test_cases = [
            # 複数の地名を含む住所
            {
                'input': '広島県福山市新市町1234',  # "新市町"は地名の一部
                'expected': '福山市新市町1234',
                'should_change': True
            },
            # 政令指定都市
            {
                'input': '静岡県静岡市葵区1234',
                'expected': '静岡県静岡市葵区1234',
                'should_change': False
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                normalized, changes = self.normalizer.normalize(case['input'])
                self.assertEqual(normalized, case['expected'])
                self.assertEqual(bool(changes), case['should_change'])

    def test_merge_dates(self):
        """合併日付の正確性テスト"""
        test_cases = [
            # 諫早市の合併
            {
                'input': '長崎県西彼杵郡多良見町1234',
                'merge_date': '平成17年3月1日'
            },
            # 福山市の最新の合併
            {
                'input': '広島県福山市1234',
                'merge_date': '平成18年3月1日'
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                _, changes = self.normalizer.normalize(case['input'])
                if changes:
                    self.assertEqual(changes[-1]['merge_date'], case['merge_date'])

    def test_edge_cases(self):
        """エッジケースのテスト"""
        test_cases = [
            # 特殊文字を含む住所
            {
                'input': '長崎県西彼杵郡多良見町１２３４',  # 全角数字
                'expected': '諫早市１２３４'
            },
            # スペースを含む住所
            {
                'input': '長崎県 西彼杵郡 多良見町 1234',
                'expected': '諫早市1234'
            }
        ]
        
        for case in test_cases:
            with self.subTest(input=case['input']):
                normalized, _ = self.normalizer.normalize(case['input'])
                self.assertEqual(normalized, case['expected'])

if __name__ == '__main__':
    unittest.main(verbosity=2) 