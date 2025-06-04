"""
住所処理のユーティリティ関数
"""

import re
import difflib
import csv
from typing import Dict, Tuple, List
from datetime import datetime

# 市区町村の変更履歴（平成11年以降の変更）
CITY_CHANGES = {
    # 平成11年度
    ("兵庫県", "多紀郡篠山町"): {"new": "篠山市", "date": "1999-04-01", "type": "新設", "reading": "たきぐんささやまちょう"},
    ("兵庫県", "多紀郡西紀町"): {"new": "篠山市", "date": "1999-04-01", "type": "新設", "reading": "にしきちょう"},
    ("兵庫県", "多紀郡丹南町"): {"new": "篠山市", "date": "1999-04-01", "type": "新設", "reading": "たんなんちょう"},
    ("兵庫県", "多紀郡今田町"): {"new": "篠山市", "date": "1999-04-01", "type": "新設", "reading": "こんだちょう"},

    # 平成13年度
    ("新潟県", "西蒲原郡黒埼町"): {"new": "新潟市", "date": "2001-01-01", "type": "編入", "reading": "にしかんばらぐんくろさきまち"},
    ("東京都", "田無市"): {"new": "西東京市", "date": "2001-01-21", "type": "新設", "reading": "たなしし"},
    ("東京都", "保谷市"): {"new": "西東京市", "date": "2001-01-21", "type": "新設", "reading": "ほうやし"},
    ("茨城県", "行方郡潮来町"): {"new": "潮来市", "date": "2001-04-01", "type": "編入", "reading": "なめかたぐんいたこまち"},
    ("茨城県", "行方郡牛堀町"): {"new": "潮来市", "date": "2001-04-01", "type": "編入", "reading": "どうぐんうしぼりまち"},
    ("埼玉県", "浦和市"): {"new": "さいたま市", "date": "2001-05-01", "type": "新設", "reading": "うらわし"},
    ("埼玉県", "大宮市"): {"new": "さいたま市", "date": "2001-05-01", "type": "新設", "reading": "おおみやし"},
    ("埼玉県", "与野市"): {"new": "さいたま市", "date": "2001-05-01", "type": "新設", "reading": "よのし"},
    ("岩手県", "気仙郡三陸町"): {"new": "大船渡市", "date": "2001-11-15", "type": "編入", "reading": "けせんぐんさんりくちょう"},

    # 平成14年度
    ("香川県", "大川郡津田町"): {"new": "さぬき市", "date": "2002-04-01", "type": "新設", "reading": "おおかわぐんつだちょう"},
    ("香川県", "大川郡大川町"): {"new": "さぬき市", "date": "2002-04-01", "type": "新設", "reading": "おおかわちょう"},
    ("香川県", "大川郡志度町"): {"new": "さぬき市", "date": "2002-04-01", "type": "新設", "reading": "しどちょう"},
    ("香川県", "大川郡寒川町"): {"new": "さぬき市", "date": "2002-04-01", "type": "新設", "reading": "さんがわちょう"},
    ("香川県", "大川郡長尾町"): {"new": "さぬき市", "date": "2002-04-01", "type": "新設", "reading": "ながおちょう"},
    ("沖縄県", "島尻郡仲里村"): {"new": "久米島町", "date": "2002-04-01", "type": "新設", "reading": "しまじりぐんなかざとそん"},
    ("沖縄県", "島尻郡具志川村"): {"new": "久米島町", "date": "2002-04-01", "type": "新設", "reading": "ぐしかわそん"},
    ("茨城県", "稲敷郡茎崎町"): {"new": "つくば市", "date": "2002-11-01", "type": "編入", "reading": "いなしきぐんくきざきまち"},

    # 平成15年度
    ("広島県", "沼隅郡内海町"): {"new": "福山市", "date": "2003-02-03", "type": "編入", "reading": "ぬまくまぐんうつみちょう"},
    ("広島県", "芦品郡新市町"): {"new": "福山市", "date": "2003-02-03", "type": "編入", "reading": "あしなぐんしんいちちょう"},
    ("山梨県", "南巨摩郡南部町"): {"new": "南部町", "date": "2003-03-01", "type": "新設", "reading": "みなみこまぐんなぶちょう"},
    ("山梨県", "南巨摩郡富沢町"): {"new": "南部町", "date": "2003-03-01", "type": "新設", "reading": "とみざわちょう"},
    ("広島県", "佐伯郡佐伯町"): {"new": "廿日市市", "date": "2003-03-01", "type": "編入", "reading": "さえきぐんさいきちょう"},
    ("広島県", "佐伯郡吉和村"): {"new": "廿日市市", "date": "2003-03-01", "type": "編入", "reading": "よしわむら"},
    ("宮城県", "加美郡中新田町"): {"new": "加美町", "date": "2003-04-01", "type": "新設", "reading": "かみぐんなかにいだまち"},
    ("宮城県", "加美郡小野田町"): {"new": "加美町", "date": "2003-04-01", "type": "新設", "reading": "おのだまち"},
    ("宮城県", "加美郡宮崎町"): {"new": "加美町", "date": "2003-04-01", "type": "新設", "reading": "みやざきちょう"},
    ("群馬県", "多野郡万場町"): {"new": "神流町", "date": "2003-04-01", "type": "新設", "reading": "たのぐんまんばまち"},
    ("群馬県", "多野郡中里村"): {"new": "神流町", "date": "2003-04-01", "type": "新設", "reading": "なかさとむら"},
    ("山梨県", "中巨摩郡八田村"): {"new": "南アルプス市", "date": "2003-04-01", "type": "新設", "reading": "なかこまぐんはったむら"},
    ("山梨県", "中巨摩郡白根町"): {"new": "南アルプス市", "date": "2003-04-01", "type": "新設", "reading": "しらねまち"},
    ("山梨県", "中巨摩郡芦安村"): {"new": "南アルプス市", "date": "2003-04-01", "type": "新設", "reading": "あしやすむら"},
    ("山梨県", "中巨摩郡若草町"): {"new": "南アルプス市", "date": "2003-04-01", "type": "新設", "reading": "わかくさちょう"},
    ("山梨県", "中巨摩郡櫛形町"): {"new": "南アルプス市", "date": "2003-04-01", "type": "新設", "reading": "くしがたまち"},
    ("山梨県", "中巨摩郡甲西町"): {"new": "南アルプス市", "date": "2003-04-01", "type": "新設", "reading": "こうさいまち"},
    ("岐阜県", "山県郡高富町"): {"new": "山県市", "date": "2003-04-01", "type": "新設", "reading": "やまがたぐんたかとみちょう"},
    ("岐阜県", "山県郡伊自良村"): {"new": "山県市", "date": "2003-04-01", "type": "新設", "reading": "いじらむら"},
    ("岐阜県", "山県郡美山町"): {"new": "山県市", "date": "2003-04-01", "type": "新設", "reading": "みやまちょう"},
    ("静岡県", "清水市"): {"new": "静岡市", "date": "2003-04-01", "type": "新設", "reading": "しみずし"},
    ("広島県", "安芸郡下蒲刈町"): {"new": "呉市", "date": "2003-04-01", "type": "編入", "reading": "あきぐんしもかまがりちょう"},
    ("広島県", "豊田郡大崎町"): {"new": "大崎上島町", "date": "2003-04-01", "type": "新設", "reading": "とよたぐんおおさきちょう"},
    ("広島県", "豊田郡東野町"): {"new": "大崎上島町", "date": "2003-04-01", "type": "新設", "reading": "ひがしのちょう"},
    ("広島県", "豊田郡木江町"): {"new": "大崎上島町", "date": "2003-04-01", "type": "新設", "reading": "きのえちょう"},
    ("香川県", "大川郡引田町"): {"new": "東かがわ市", "date": "2003-04-01", "type": "新設", "reading": "おおかわぐんひけたちょう"},
    ("香川県", "大川郡白鳥町"): {"new": "東かがわ市", "date": "2003-04-01", "type": "新設", "reading": "しろとりちょう"},
    ("香川県", "大川郡大内町"): {"new": "東かがわ市", "date": "2003-04-01", "type": "新設", "reading": "おおちちょう"},
    ("愛媛県", "宇摩郡別子山村"): {"new": "新居浜市", "date": "2003-04-01", "type": "編入", "reading": "うまぐんべっしやまむら"},
    ("福岡県", "宗像郡玄海町"): {"new": "宗像市", "date": "2003-04-01", "type": "新設", "reading": "むなかたぐんげんかいまち"},
    ("熊本県", "球磨郡上村"): {"new": "あさぎり町", "date": "2003-04-01", "type": "新設", "reading": "くまぐんうえむら"},
    ("熊本県", "球磨郡免田町"): {"new": "あさぎり町", "date": "2003-04-01", "type": "新設", "reading": "めんだまち"},
    ("熊本県", "球磨郡岡原村"): {"new": "あさぎり町", "date": "2003-04-01", "type": "新設", "reading": "おかはるむら"},
    ("熊本県", "球磨郡須恵村"): {"new": "あさぎり町", "date": "2003-04-01", "type": "新設", "reading": "すえむら"},
    ("熊本県", "球磨郡深田村"): {"new": "あさぎり町", "date": "2003-04-01", "type": "新設", "reading": "ふかだむら"},

    # 平成16年度以降のデータは追加で実装が必要です

    # 平成17年度
    ("高知県", "土佐郡鏡村"): {"new": "高知市", "date": "2005-01-01", "type": "編入", "reading": "とさぐんかがみむら"},
    ("高知県", "土佐郡土佐山村"): {"new": "高知市", "date": "2005-01-01", "type": "編入", "reading": "とさやまむら"},
    ("佐賀県", "東松浦郡浜玉町"): {"new": "唐津市", "date": "2005-01-01", "type": "新設", "reading": "ひがしまつうらぐんはまたまちょう"},
    ("佐賀県", "東松浦郡厳木町"): {"new": "唐津市", "date": "2005-01-01", "type": "新設", "reading": "きゅうらぎまち"},
    ("佐賀県", "東松浦郡相知町"): {"new": "唐津市", "date": "2005-01-01", "type": "新設", "reading": "おうちちょう"},
    ("佐賀県", "東松浦郡北波多村"): {"new": "唐津市", "date": "2005-01-01", "type": "新設", "reading": "きたはたむら"},
    ("佐賀県", "東松浦郡肥前町"): {"new": "唐津市", "date": "2005-01-01", "type": "新設", "reading": "ひぜんちょう"},
    ("佐賀県", "東松浦郡鎮西町"): {"new": "唐津市", "date": "2005-01-01", "type": "新設", "reading": "ちんぜいちょう"},
    ("佐賀県", "東松浦郡呼子町"): {"new": "唐津市", "date": "2005-01-01", "type": "新設", "reading": "よぶこちょう"},
    ("佐賀県", "杵島郡白石町"): {"new": "白石町", "date": "2005-01-01", "type": "新設", "reading": "きしまぐんしろいしちょう"},
    ("佐賀県", "杵島郡福富町"): {"new": "白石町", "date": "2005-01-01", "type": "新設", "reading": "ふくどみまち"},
    ("佐賀県", "杵島郡有明町"): {"new": "白石町", "date": "2005-01-01", "type": "新設", "reading": "ありあけちょう"},
    ("熊本県", "葦北郡田浦町"): {"new": "芦北町", "date": "2005-01-01", "type": "新設", "reading": "あしきたぐんたのうらまち"},
    ("熊本県", "葦北郡芦北町"): {"new": "芦北町", "date": "2005-01-01", "type": "新設", "reading": "あしきたまち"},
    ("大分県", "大分郡野津原町"): {"new": "大分市", "date": "2005-01-01", "type": "編入", "reading": "おおいたぐんのつはるまち"},
    ("大分県", "北海部郡佐賀関町"): {"new": "大分市", "date": "2005-01-01", "type": "編入", "reading": "きたあまべぐんさがのせきまち"},
    ("大分県", "大野郡野津町"): {"new": "臼杵市", "date": "2005-01-01", "type": "新設", "reading": "おおのぐんのつまち"},
    ("長崎県", "西彼杵郡香焼町"): {"new": "長崎市", "date": "2005-01-04", "type": "編入", "reading": "にしそのぎぐんこうやぎちょう"},
    ("長崎県", "西彼杵郡伊王島町"): {"new": "長崎市", "date": "2005-01-04", "type": "編入", "reading": "いおうじまちょう"},
    ("長崎県", "西彼杵郡高島町"): {"new": "長崎市", "date": "2005-01-04", "type": "編入", "reading": "たかしまちょう"},
    ("長崎県", "西彼杵郡野母崎町"): {"new": "長崎市", "date": "2005-01-04", "type": "編入", "reading": "のもざきちょう"},
    ("長崎県", "西彼杵郡三和町"): {"new": "長崎市", "date": "2005-01-04", "type": "編入", "reading": "さんわちょう"},
    ("長崎県", "西彼杵郡外海町"): {"new": "長崎市", "date": "2005-01-04", "type": "編入", "reading": "そとめちょう"},
    ("秋田県", "河辺郡河辺町"): {"new": "秋田市", "date": "2005-01-11", "type": "編入", "reading": "かわべぐんかわべまち"},
    ("秋田県", "河辺郡雄和町"): {"new": "秋田市", "date": "2005-01-11", "type": "編入", "reading": "ゆうわまち"},
    ("三重県", "鈴鹿郡関町"): {"new": "亀山市", "date": "2005-01-11", "type": "新設", "reading": "すずかぐんせきちょう"},
    ("兵庫県", "三原郡緑町"): {"new": "南あわじ市", "date": "2005-01-11", "type": "新設", "reading": "みはらぐんみどりちょう"},
    ("兵庫県", "三原郡西淡町"): {"new": "南あわじ市", "date": "2005-01-11", "type": "新設", "reading": "せいだんちょう"},
    ("兵庫県", "三原郡三原町"): {"new": "南あわじ市", "date": "2005-01-11", "type": "新設", "reading": "みはらちょう"},
    ("兵庫県", "三原郡南淡町"): {"new": "南あわじ市", "date": "2005-01-11", "type": "新設", "reading": "なんだんちょう"},
    ("愛媛県", "喜多郡長浜町"): {"new": "大洲市", "date": "2005-01-11", "type": "新設", "reading": "きたぐんながはまちょう"},
    ("愛媛県", "喜多郡肱川町"): {"new": "大洲市", "date": "2005-01-11", "type": "新設", "reading": "ひじかわちょう"},
    ("愛媛県", "喜多郡河辺村"): {"new": "大洲市", "date": "2005-01-11", "type": "新設", "reading": "かわべむら"},
    ("熊本県", "宇土郡三角町"): {"new": "宇城市", "date": "2005-01-15", "type": "新設", "reading": "うとぐんみすみまち"},
    ("熊本県", "宇土郡不知火町"): {"new": "宇城市", "date": "2005-01-15", "type": "新設", "reading": "しらぬひまち"},
    ("熊本県", "下益城郡松橋町"): {"new": "宇城市", "date": "2005-01-15", "type": "新設", "reading": "しもましきぐんまつばせまち"},
    ("熊本県", "下益城郡小川町"): {"new": "宇城市", "date": "2005-01-15", "type": "新設", "reading": "おがわまち"},
    ("熊本県", "下益城郡豊野町"): {"new": "宇城市", "date": "2005-01-15", "type": "新設", "reading": "とよのまち"},
    ("熊本県", "鹿本郡鹿北町"): {"new": "山鹿市", "date": "2005-01-15", "type": "新設", "reading": "かもとぐんかほくまち"},
    ("熊本県", "鹿本郡菊鹿町"): {"new": "山鹿市", "date": "2005-01-15", "type": "新設", "reading": "きくかまち"},
    ("熊本県", "鹿本郡鹿本町"): {"new": "山鹿市", "date": "2005-01-15", "type": "新設", "reading": "かもとまち"},
    ("熊本県", "鹿本郡鹿央町"): {"new": "山鹿市", "date": "2005-01-15", "type": "新設", "reading": "かおうまち"},
    ("愛媛県", "越智郡朝倉村"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "おちぐんあさくらむら"},
    ("愛媛県", "越智郡玉川町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "たまがわちょう"},
    ("愛媛県", "越智郡波方町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "なみかたちょう"},
    ("愛媛県", "越智郡大西町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "おおにしちょう"},
    ("愛媛県", "越智郡菊間町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "きくまちょう"},
    ("愛媛県", "越智郡関前村"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "せきぜんむら"},
    ("愛媛県", "越智郡吉海町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "よしうみちょう"},
    ("愛媛県", "越智郡宮窪町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "みやくぼちょう"},
    ("愛媛県", "越智郡伯方町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "はかたちょう"},
    ("愛媛県", "越智郡上浦町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "かみうらちょう"},
    ("愛媛県", "越智郡大三島町"): {"new": "今治市", "date": "2005-01-16", "type": "新設", "reading": "おおみしまちょう"},
    ("静岡県", "小笠郡小笠町"): {"new": "菊川市", "date": "2005-01-17", "type": "新設", "reading": "おがさぐんおがさちょう"},
    ("静岡県", "小笠郡菊川町"): {"new": "菊川市", "date": "2005-01-17", "type": "新設", "reading": "きくがわちょう"},
    ("茨城県", "那珂郡那珂町"): {"new": "那珂市", "date": "2005-01-21", "type": "編入", "reading": "なかぐんなかまち"},
    ("茨城県", "那珂郡瓜連町"): {"new": "那珂市", "date": "2005-01-21", "type": "編入", "reading": "うりづらまち"},
    ("福岡県", "宗像郡福間町"): {"new": "福津市", "date": "2005-01-24", "type": "新設", "reading": "むなかたぐんふくままち"},
    ("福岡県", "宗像郡津屋崎町"): {"new": "福津市", "date": "2005-01-24", "type": "新設", "reading": "つやざきまち"},
    ("岐阜県", "揖斐郡谷汲村"): {"new": "揖斐川町", "date": "2005-01-31", "type": "新設", "reading": "たにぐみむら"},
    ("岐阜県", "揖斐郡春日村"): {"new": "揖斐川町", "date": "2005-01-31", "type": "新設", "reading": "かすがむら"},
    ("岐阜県", "揖斐郡久瀬村"): {"new": "揖斐川町", "date": "2005-01-31", "type": "新設", "reading": "くぜむら"},
    ("岐阜県", "揖斐郡藤橋村"): {"new": "揖斐川町", "date": "2005-01-31", "type": "新設", "reading": "ふじはしむら"},
    ("岐阜県", "揖斐郡坂内村"): {"new": "揖斐川町", "date": "2005-01-31", "type": "新設", "reading": "さかうちむら"},
    # 平成17年度（続き）
    ("茨城県", "東茨城郡内原町"): {"new": "水戸市", "date": "2005-02-01", "type": "編入", "reading": "ひがしいばらきぐんうちはらまち"},
    ("茨城県", "東茨城郡常北町"): {"new": "城里町", "date": "2005-02-01", "type": "新設", "reading": "ひがしいばらきぐんじょうほくまち"},
    ("茨城県", "東茨城郡桂村"): {"new": "城里町", "date": "2005-02-01", "type": "新設", "reading": "かつらむら"},
    ("茨城県", "西茨城郡七会村"): {"new": "城里町", "date": "2005-02-01", "type": "新設", "reading": "にしいばらきぐんななかいむら"},
    ("石川県", "松任市"): {"new": "白山市", "date": "2005-02-01", "type": "新設", "reading": "まつとうし"},
    ("石川県", "石川郡美川町"): {"new": "白山市", "date": "2005-02-01", "type": "新設", "reading": "いしかわぐんみかわまち"},
    ("石川県", "石川郡鶴来町"): {"new": "白山市", "date": "2005-02-01", "type": "新設", "reading": "つるぎまち"},
    ("石川県", "石川郡河内村"): {"new": "白山市", "date": "2005-02-01", "type": "新設", "reading": "かわちむら"},
    ("石川県", "石川郡吉野谷村"): {"new": "白山市", "date": "2005-02-01", "type": "新設", "reading": "よしのだにむら"},
    ("石川県", "石川郡鳥越村"): {"new": "白山市", "date": "2005-02-01", "type": "新設", "reading": "とりごえむら"},
    ("石川県", "石川郡尾口村"): {"new": "白山市", "date": "2005-02-01", "type": "新設", "reading": "おぐちむら"},
    ("石川県", "石川郡白峰村"): {"new": "白山市", "date": "2005-02-01", "type": "新設", "reading": "しらみねむら"},
    ("石川県", "能美郡根上町"): {"new": "能美市", "date": "2005-02-01", "type": "新設", "reading": "のみぐんねあがりまち"},
    ("石川県", "能美郡寺井町"): {"new": "能美市", "date": "2005-02-01", "type": "新設", "reading": "てらいまち"},
    ("石川県", "能美郡辰口町"): {"new": "能美市", "date": "2005-02-01", "type": "新設", "reading": "たつのくちまち"},
    ("福井県", "丹生郡朝日町"): {"new": "越前町", "date": "2005-02-01", "type": "新設", "reading": "にゅうぐんあさひちょう"},
    ("福井県", "丹生郡宮崎村"): {"new": "越前町", "date": "2005-02-01", "type": "新設", "reading": "みやざきむら"},
    ("福井県", "丹生郡越前町"): {"new": "越前町", "date": "2005-02-01", "type": "新設", "reading": "えちぜんちょう"},
    ("福井県", "丹生郡織田町"): {"new": "越前町", "date": "2005-02-01", "type": "新設", "reading": "おたちょう"},
    ("岐阜県", "大野郡丹生川村"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "おおのぐんにゅうかわむら"},
    ("岐阜県", "大野郡清見村"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "きよみむら"},
    ("岐阜県", "大野郡荘川村"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "しょうかわむら"},
    ("岐阜県", "大野郡宮村"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "みやむら"},
    ("岐阜県", "大野郡久々野町"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "くぐのちょう"},
    ("岐阜県", "大野郡朝日村"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "あさひむら"},
    ("岐阜県", "大野郡高根村"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "たかねむら"},
    ("岐阜県", "吉城郡国府町"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "よしきぐんこくふちょう"},
    ("岐阜県", "吉城郡上宝村"): {"new": "高山市", "date": "2005-02-01", "type": "編入", "reading": "かみたからむら"},
    ("大阪府", "南河内郡美原町"): {"new": "堺市", "date": "2005-02-01", "type": "編入", "reading": "みなみかわちぐんみはらちょう"},
    ("広島県", "沼隈郡沼隈町"): {"new": "福山市", "date": "2005-02-01", "type": "編入", "reading": "ぬまくまぐんぬまくまちょう"},
    ("広島県", "山県郡芸北町"): {"new": "北広島町", "date": "2005-02-01", "type": "新設", "reading": "やまがたぐんげいほくちょう"},
    ("広島県", "山県郡大朝町"): {"new": "北広島町", "date": "2005-02-01", "type": "新設", "reading": "おおあさちょう"},
    ("広島県", "山県郡千代田町"): {"new": "北広島町", "date": "2005-02-01", "type": "新設", "reading": "ちよだちょう"},
    ("広島県", "山県郡豊平町"): {"new": "北広島町", "date": "2005-02-01", "type": "新設", "reading": "とよひらちょう"},
    ("高知県", "高岡郡葉山村"): {"new": "津野町", "date": "2005-02-01", "type": "新設", "reading": "たかおかぐんはやまむら"},
    ("高知県", "高岡郡東津野村"): {"new": "津野町", "date": "2005-02-01", "type": "新設", "reading": "たかおかぐんひがしつのむら"},
    ("福岡県", "浮羽郡田主丸町"): {"new": "久留米市", "date": "2005-02-05", "type": "編入", "reading": "うきはぐんたぬしまるまち"},
    ("福岡県", "三井郡北野町"): {"new": "久留米市", "date": "2005-02-05", "type": "編入", "reading": "みいぐんきたのまち"},
    ("福岡県", "三潴郡城島町"): {"new": "久留米市", "date": "2005-02-05", "type": "編入", "reading": "みずまぐんじょうじままち"},
    ("福岡県", "三潴郡三潴町"): {"new": "久留米市", "date": "2005-02-05", "type": "編入", "reading": "みづままち"},
    ("岐阜県", "武儀郡洞戸村"): {"new": "関市", "date": "2005-02-07", "type": "編入", "reading": "むぎぐんほらどむら"},
    ("岐阜県", "武儀郡板取村"): {"new": "関市", "date": "2005-02-07", "type": "編入", "reading": "いたどりむら"},
    ("岐阜県", "武儀郡武芸川町"): {"new": "関市", "date": "2005-02-07", "type": "編入", "reading": "むげがわちょう"},
    ("岐阜県", "武儀郡武儀町"): {"new": "関市", "date": "2005-02-07", "type": "編入", "reading": "むぎちょう"},
    ("岐阜県", "武儀郡上之保村"): {"new": "関市", "date": "2005-02-07", "type": "編入", "reading": "かみのほむら"},
    ("三重県", "三重郡楠町"): {"new": "四日市市", "date": "2005-02-07", "type": "編入", "reading": "みえぐんくすちょう"},
    ("広島県", "賀茂郡黒瀬町"): {"new": "東広島市", "date": "2005-02-07", "type": "編入", "reading": "かもぐんくろせちょう"},
    ("広島県", "賀茂郡福富町"): {"new": "東広島市", "date": "2005-02-07", "type": "編入", "reading": "ふくとみちょう"},
    ("広島県", "賀茂郡豊栄町"): {"new": "東広島市", "date": "2005-02-07", "type": "編入", "reading": "とよさかちょう"},
    ("広島県", "賀茂郡河内町"): {"new": "東広島市", "date": "2005-02-07", "type": "編入", "reading": "こうちちょう"},
    ("広島県", "豊田郡安芸津町"): {"new": "東広島市", "date": "2005-02-07", "type": "編入", "reading": "とよたぐんあきつちょう"},
    ("青森県", "西津軽郡木造町"): {"new": "つがる市", "date": "2005-02-11", "type": "新設", "reading": "にしつがるぐんきづくりまち"},
    ("青森県", "西津軽郡森田村"): {"new": "つがる市", "date": "2005-02-11", "type": "新設", "reading": "もりたむら"},
    ("青森県", "西津軽郡柏村"): {"new": "つがる市", "date": "2005-02-11", "type": "新設", "reading": "かしわむら"},
    ("青森県", "西津軽郡稲垣村"): {"new": "つがる市", "date": "2005-02-11", "type": "新設", "reading": "いながきむら"},
    ("青森県", "西津軽郡車力村"): {"new": "つがる市", "date": "2005-02-11", "type": "新設", "reading": "しゃりきむら"},
    ("千葉県", "安房郡天津小湊町"): {"new": "鴨川市", "date": "2005-02-11", "type": "新設", "reading": "あわぐんあまつこみなとまち"},
    ("滋賀県", "八日市市"): {"new": "東近江市", "date": "2005-02-11", "type": "新設", "reading": "ようかいちし"},
    ("滋賀県", "神崎郡永源寺町"): {"new": "東近江市", "date": "2005-02-11", "type": "新設", "reading": "かんざきぐんえいげんじちょう"},
    ("滋賀県", "神崎郡五個荘町"): {"new": "東近江市", "date": "2005-02-11", "type": "新設", "reading": "ごかしょうちょう"},
    ("滋賀県", "愛知郡愛東町"): {"new": "東近江市", "date": "2005-02-11", "type": "新設", "reading": "えちぐんあいとうちょう"},
    ("滋賀県", "愛知郡湖東町"): {"new": "東近江市", "date": "2005-02-11", "type": "新設", "reading": "ことうちょう"},
    ("熊本県", "阿蘇郡一の宮町"): {"new": "阿蘇市", "date": "2005-02-11", "type": "新設", "reading": "あそぐんいちのみやまち"},
    ("熊本県", "阿蘇郡阿蘇町"): {"new": "阿蘇市", "date": "2005-02-11", "type": "新設", "reading": "あそまち"},
    ("熊本県", "阿蘇郡波野村"): {"new": "阿蘇市", "date": "2005-02-11", "type": "新設", "reading": "なみのそん"},
    ("熊本県", "上益城郡矢部町"): {"new": "山都町", "date": "2005-02-11", "type": "新設", "reading": "かみましきぐんやべまち"},
    ("熊本県", "上益城郡清和村"): {"new": "山都町", "date": "2005-02-11", "type": "新設", "reading": "せいわそん"},
    ("熊本県", "阿蘇郡蘇陽町"): {"new": "山都町", "date": "2005-02-11", "type": "新設", "reading": "あそぐんそようまち"},
}

# 都道府県名のリスト
PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]

def extract_prefecture(address: str) -> Tuple[str, str]:
    """
    住所から都道府県名を抽出し、残りの住所と共に返す
    
    Args:
        address (str): 入力住所
    
    Returns:
        Tuple[str, str]: (都道府県名, 残りの住所)
    """
    for pref in PREFECTURES:
        if address.startswith(pref):
            return pref, address[len(pref):]
    return "", address

def normalize_city_name(address: str, date: str = None) -> str:
    """
    廃止された市区町村名を現在の名称に変換
    
    Args:
        address (str): 入力住所
        date (str, optional): 基準日（YYYY-MM-DD形式）。指定がない場合は最新の状態に変換
    
    Returns:
        str: 正規化された住所
    """
    # 都道府県名を抽出
    prefecture, remaining_address = extract_prefecture(address)
    if not prefecture:
        return address
    
    # 基準日の処理
    target_date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
    
    # 旧市町村名を探索
    normalized = remaining_address
    for (pref, old_city), info in CITY_CHANGES.items():
        if prefecture == pref and old_city in remaining_address:
            # 基準日チェック
            change_date = datetime.strptime(info["date"], "%Y-%m-%d")
            if not date or target_date >= change_date:
                # 新しい市町村名に置換
                normalized = remaining_address.replace(old_city, info["new"])
                break
    
    # 都道府県名と正規化された住所を結合
    return prefecture + normalized

def normalize_number(number: str) -> str:
    """漢数字と全角数字を半角算用数字に変換"""
    kanji_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
        '１': '1', '２': '2', '３': '3', '４': '4', '５': '5',
        '６': '6', '７': '7', '８': '8', '９': '9', '０': '0'
    }
    
    # 漢数字と全角数字を半角算用数字に変換
    result = number
    for kanji, digit in kanji_numbers.items():
        result = result.replace(kanji, digit)
    
    return result

def normalize_address_numbers(address: str) -> str:
    """
    住所の数字を正規化する
    - 丁目・番地・号の前の漢数字のみをアラビア数字に変換
    - その他の漢数字（地名等）はそのまま保持
    - 全角数字は半角数字に変換
    
    Parameters:
    -----------
    address : str
        正規化する住所
        
    Returns:
    --------
    str
        正規化された住所
    """
    # 全角数字を半角に変換
    normalized = address.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    
    # 丁目・番地・号の前の漢数字のみをアラビア数字に変換
    kanji_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9'
    }
    
    # 丁目・番地・号の前の漢数字のみを変換
    for kanji, arabic in kanji_numbers.items():
        normalized = re.sub(f'{kanji}(?=(丁目|番地?|号))', arabic, normalized)
    
    return normalized

def extract_address_parts(address: str) -> tuple:
    """住所から丁目、番地、号の数字を抽出"""
    # 数字を正規化
    normalized = normalize_address_numbers(address)
    
    # パターン1: ハイフン区切り (例: 1-4-5)
    pattern1 = r'(\d+)[-−ー](\d+)[-−ー](\d+)'
    match = re.search(pattern1, normalized)
    if match:
        return match.group(1), match.group(2), match.group(3)
    
    # パターン2: ハイフン区切り (例: 1-4)
    pattern2 = r'(\d+)[-−ー](\d+)'
    match = re.search(pattern2, normalized)
    if match:
        return match.group(1), match.group(2), None
    
    # パターン3: 丁目、番、号
    chome = None
    banchi = None
    go = None
    
    if '丁目' in normalized:
        parts = normalized.split('丁目')
        nums = re.findall(r'\d+', parts[0])
        if nums:
            chome = nums[-1]
            rest = parts[1]
        else:
            rest = normalized
    else:
        rest = normalized
    
    if '番' in rest:
        parts = rest.split('番')
        nums = re.findall(r'\d+', parts[0])
        if nums:
            banchi = nums[-1]
            rest = parts[1]
    
    if '号' in rest:
        nums = re.findall(r'\d+', rest.split('号')[0])
        if nums:
            go = nums[-1]
    
    return chome, banchi, go

def calculate_address_similarity(address1: str, address2: str) -> float:
    """
    2つの住所の類似度を計算する
    
    Parameters:
    -----------
    address1 : str
        比較する住所1
    address2 : str
        比較する住所2
        
    Returns:
    --------
    float
        類似度（0.0～1.0）
    """
    # 数字を正規化（地名の漢数字は保持）
    norm1 = normalize_address_numbers(address1)
    norm2 = normalize_address_numbers(address2)
    
    # 文字列を正規化（空白除去）
    norm1 = ''.join(norm1.split())
    norm2 = ''.join(norm2.split())
    
    # 完全一致の場合
    if norm1 == norm2:
        return 1.0
    
    # 部分文字列の場合
    if norm1 in norm2 or norm2 in norm1:
        return 0.8
    
    # 文字の一致率を計算
    matches = sum(1 for a, b in zip(norm1, norm2) if a == b)
    max_length = max(len(norm1), len(norm2))
    
    return matches / max_length if max_length > 0 else 0.0

def analyze_address_match_level(input_address: str, matched_address: str) -> Dict[str, bool]:
    """
    住所のマッチングレベルを分析する
    
    Parameters:
    -----------
    input_address : str
        入力された住所
    matched_address : str
        マッチした住所
        
    Returns:
    --------
    Dict[str, bool]
        各レベル（丁目、番地、号）のマッチング結果
    """
    # 数字を正規化（地名の漢数字は保持）
    input_norm = normalize_address_numbers(input_address)
    matched_norm = normalize_address_numbers(matched_address)
    
    # 丁目、番地、号を抽出
    def extract_numbers(address: str) -> Dict[str, str]:
        numbers = {
            'chome': '',
            'banchi': '',
            'go': ''
        }
        
        # 丁目を抽出
        chome_match = re.search(r'(\d+)丁目', address)
        if chome_match:
            numbers['chome'] = chome_match.group(1)
            
        # 番地を抽出
        banchi_match = re.search(r'(\d+)番地?', address)
        if banchi_match:
            numbers['banchi'] = banchi_match.group(1)
            
        # 号を抽出
        go_match = re.search(r'(\d+)号', address)
        if go_match:
            numbers['go'] = go_match.group(1)
            
        return numbers
    
    input_numbers = extract_numbers(input_norm)
    matched_numbers = extract_numbers(matched_norm)
    
    return {
        'chome_match': input_numbers['chome'] == matched_numbers['chome'] and input_numbers['chome'] != '',
        'banchi_match': input_numbers['banchi'] == matched_numbers['banchi'] and input_numbers['banchi'] != '',
        'go_match': input_numbers['go'] == matched_numbers['go'] and input_numbers['go'] != ''
    }

def normalize_city_name_with_history(address: str, date: str = None) -> str:
    """
    市町村合併履歴を考慮して市町村名を正規化する
    
    Parameters:
    -----------
    address : str
        正規化する住所
    date : str, optional
        基準日（YYYY-MM-DD形式）。指定がない場合は最新の状態を使用
    
    Returns:
    --------
    str
        正規化された住所
    """
    prefecture, remaining = extract_prefecture(address)
    if not prefecture:
        return address
        
    # 都道府県を除いた部分で市町村名を探す
    for (pref, old_city), change in CITY_CHANGES.items():
        if pref != prefecture:
            continue
            
        # 日付チェック
        if date and change['date'] > date:
            continue
            
        # 旧市町村名が含まれているかチェック
        if old_city in remaining:
            # 新市町村名に置換
            remaining = remaining.replace(old_city, change['new'])
            
    return f"{prefecture}{remaining}"

def get_city_reading(prefecture: str, city_name: str) -> str:
    """
    市町村名の読み仮名を取得する
    
    Parameters:
    -----------
    prefecture : str
        都道府県名
    city_name : str
        市町村名
    
    Returns:
    --------
    str
        読み仮名（見つからない場合は空文字列）
    """
    # 新市町村名で検索
    for (pref, _), change in CITY_CHANGES.items():
        if pref == prefecture and change['new'] == city_name:
            return change.get('reading', '')
            
    # 旧市町村名で検索
    for (pref, old_city), change in CITY_CHANGES.items():
        if pref == prefecture and old_city == city_name:
            return change.get('reading', '')
            
    return ''

def get_city_history(prefecture: str, city_name: str) -> List[Dict]:
    """
    市町村の変遷履歴を取得する
    
    Parameters:
    -----------
    prefecture : str
        都道府県名
    city_name : str
        市町村名
    
    Returns:
    --------
    List[Dict]
        変遷履歴のリスト。各要素は以下のキーを持つ辞書：
        - old_name: 旧市町村名
        - new_name: 新市町村名
        - date: 変更日
        - type: 変更種別（新設/編入）
        - reading: 読み仮名
    """
    history = []
    
    # 新市町村名として検索
    for (pref, old_city), change in CITY_CHANGES.items():
        if pref == prefecture and change['new'] == city_name:
            history.append({
                'old_name': old_city,
                'new_name': change['new'],
                'date': change['date'],
                'type': change['type'],
                'reading': change.get('reading', '')
            })
            
    # 旧市町村名として検索
    for (pref, old_city), change in CITY_CHANGES.items():
        if pref == prefecture and old_city == city_name:
            history.append({
                'old_name': old_city,
                'new_name': change['new'],
                'date': change['date'],
                'type': change['type'],
                'reading': change.get('reading', '')
            })
            
    # 日付でソート
    history.sort(key=lambda x: x['date'])
    return history

def improve_address_matching(input_address: str, candidates: List[str]) -> Tuple[str, float]:
    """
    住所マッチングの精度を改善する
    
    Parameters:
    -----------
    input_address : str
        入力住所
    candidates : List[str]
        マッチング候補の住所リスト
    
    Returns:
    --------
    Tuple[str, float]
        最もマッチする住所と類似度のタプル
    """
    best_match = None
    highest_similarity = -1
    
    # 入力住所から都道府県を抽出
    input_prefecture, input_remaining = extract_prefecture(input_address)
    
    for candidate in candidates:
        # 候補住所から都道府県を抽出
        candidate_prefecture, candidate_remaining = extract_prefecture(candidate)
        
        # 都道府県が一致しない場合はスキップ
        if input_prefecture and candidate_prefecture and input_prefecture != candidate_prefecture:
            continue
        
        # 住所の類似度を計算
        similarity = calculate_address_similarity(input_remaining, candidate_remaining)
        
        # 都道府県が一致する場合は類似度にボーナスを加算
        if input_prefecture and candidate_prefecture and input_prefecture == candidate_prefecture:
            similarity += 0.1
        
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = candidate
    
    return best_match or input_address, highest_similarity 