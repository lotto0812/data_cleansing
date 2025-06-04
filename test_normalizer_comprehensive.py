from normalize_address import AddressNormalizer
from datetime import datetime
import json

def test_comprehensive(output_file: str = 'test_results.txt', json_output_file: str = 'test_results.json'):
    """
    包括的なテストを実行し、結果をファイルに出力
    Args:
        output_file: テスト結果を出力するテキストファイル
        json_output_file: テスト結果を出力するJSONファイル
    """
    normalizer = AddressNormalizer('市区町村マッピング.json')
    
    test_cases = [
        # 1. 基本的な変換ケース
        {
            'input': '長崎県西彼杵郡多良見町下郡1234',
            'description': '基本的な市町村合併'
        },
        # 2. 政令指定都市
        {
            'input': '静岡県静岡市葵区追手町1234',
            'description': '政令指定都市（変更なし）'
        },
        {
            'input': '新潟県新潟市中央区西堀通1234',
            'description': '政令指定都市（変更なし）'
        },
        # 3. 複数回合併した市
        {
            'input': '広島県福山市1234',
            'description': '複数回合併した市'
        },
        {
            'input': '新潟県長岡市1234',
            'description': '複数回合併した市'
        },
        # 4. 特殊なケース
        {
            'input': '山梨県西八代郡上九一色村1234',
            'description': '分割された村'
        },
        {
            'input': '広島県福山市新市町1234',
            'description': '新市名に旧市町村名を含む'
        },
        # 5. 様々な形式の住所
        {
            'input': '長崎県 西彼杵郡 多良見町 1234',
            'description': 'スペースを含む'
        },
        {
            'input': '長崎県西彼杵郡多良見町１２３４',
            'description': '全角数字'
        },
        {
            'input': '東京都新宿区西新宿1234',
            'description': '変更のない住所'
        },
        # 6. エッジケース
        {
            'input': '',
            'description': '空の文字列'
        },
        {
            'input': '新宿区1234',
            'description': '都道府県名なし'
        },
        {
            'input': '東京都新宿区　歌舞伎町　1234',
            'description': '全角スペース'
        },
        # 7. 複雑な住所
        {
            'input': '静岡県静岡市葵区追手町9番地の50 静岡県庁舎別館',
            'description': '建物名を含む政令指定都市'
        },
        {
            'input': '長崎県西彼杵郡多良見町下郡1234-5678 ABCビル9F',
            'description': '建物名とフロア情報を含む'
        }
    ]
    
    # テスト結果を格納するリスト
    results = []
    
    # テスト実行時刻
    test_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # テキストファイルとJSONファイルに結果を書き込む
    with open(output_file, 'w', encoding='utf-8') as f, \
         open(json_output_file, 'w', encoding='utf-8') as jf:
        
        # ヘッダー情報を書き込み
        header = f"住所正規化システム テスト結果\n実行日時: {test_time}\n{'=' * 80}\n"
        f.write(header)
        
        # 各テストケースを実行
        for case in test_cases:
            # テスト実行
            normalized, changes = normalizer.normalize(case['input'])
            
            # テキスト形式の結果を作成
            result_text = f"\nテストケース: {case['description']}\n"
            result_text += f"入力: {case['input']}\n"
            result_text += f"出力: {normalized}\n"
            
            if changes:
                result_text += "適用された変更:\n"
                for change in changes:
                    result_text += f"  - {change['old']} → {change['new']} ({change['merge_date']})\n"
            else:
                result_text += "変更なし\n"
            
            # テキストファイルに書き込み
            f.write(result_text)
            
            # JSON用の結果を作成
            result_dict = {
                'description': case['description'],
                'input': case['input'],
                'output': normalized,
                'changes': changes,
                'has_changes': bool(changes)
            }
            results.append(result_dict)
            
            # コンソールにも出力
            print(result_text)
        
        # フッター情報を書き込み
        footer = f"\n{'=' * 80}\nテスト完了\n"
        f.write(footer)
        print(footer)
        
        # JSON形式で結果を保存
        json_output = {
            'test_time': test_time,
            'total_cases': len(test_cases),
            'cases_with_changes': sum(1 for r in results if r['has_changes']),
            'results': results
        }
        json.dump(json_output, jf, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    test_comprehensive() 