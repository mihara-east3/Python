import requests
import pandas as pd

APP_ID = "c28dfcf13a260f963f76011d414c56affc82f487"
API_URL = "http://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

params = {
    "appId": APP_ID,
    'statsDataId': '0003425296',   # 普通貿易統計 貿易統計_全国分 概況品別国別表 概況品別国別表 輸入 2021~2023
    'cdCat01': '30501030',              # 液化天然ガス
    "lang": "J"                                     # 日本語を指定
}

response = requests.get(API_URL, params=params)
data = response.json()

# 統計データからデータ部取得
values = data['GET_STATS_DATA']['STATISTICAL_DATA']['DATA_INF']['VALUE']

# JSONからDataFrameを作成
df = pd.DataFrame(values)

# メタ情報取得
meta_info = data['GET_STATS_DATA']['STATISTICAL_DATA']['CLASS_INF']['CLASS_OBJ']

# 統計データのカテゴリ要素をID(数字の羅列)から、意味のある名称に変更する
for class_obj in meta_info:

    # メタ情報の「@id」の先頭に'@'を付与した文字列が、統計データの列名と対応している
    column_name = '@' + class_obj['@id']

    # 統計データの列名を「@code」から「@name」に置換するディクショナリを作成
    id_to_name_dict = {}
    if isinstance(class_obj['CLASS'], list):
        for obj in class_obj['CLASS']:
            id_to_name_dict[obj['@code']] = obj['@name']
    else:
        id_to_name_dict[class_obj['CLASS']['@code']] = class_obj['CLASS']['@name']

    # ディクショナリを用いて、指定した列の要素を置換
    df[column_name] = df[column_name].replace(id_to_name_dict)

# 統計データの列名を変換するためのディクショナリを作成
col_replace_dict = {'@unit': '単位', '$': '値'}
for class_obj in meta_info:
    org_col = '@' + class_obj['@id']
    new_col = class_obj['@name']
    col_replace_dict[org_col] = new_col

# ディクショナリに従って、列名を置換する
new_columns = []
for col in df.columns:
    if col in col_replace_dict:
        new_columns.append(col_replace_dict[col])
    else:
        new_columns.append(col)
df.columns = new_columns
# ここまでで、DBを列指向形式でのデータを抽出　仕上がりはdfデータフレーム
###

df1 = df[df["概況品目表の数量・金額"] != "単位"].copy()     #"概況品目表の数量・金額"] = "単位" を含む行を削除
df2 = df1[df1["概況品目表の数量・金額"].str.contains("合計") == False].copy() 	# 年度合計を含む行を削除
df3 = df2.drop("概況品目(輸入)", axis=1)
df4 = df3.drop("単位", axis=1)
df4["値"] = df4["値"].astype(int)

# underscore ('_')を基に文字列を分割
df4[['月度', '種別']] = df4["概況品目表の数量・金額"].str.split('_', expand=True)
# '時間軸(年次)'と'月度'を結合して新たな日付データを生成
df4['日付'] =df4['時間軸(年次)'] + df4['月度']

# 日付データをフォーマット変換
df4['日付'] = pd.to_datetime(df4['日付'], format="%Y年%m月")
###
df5 = df4.pivot_table(index="日付", columns="種別", values = "値", aggfunc="sum")
df5["単価"] = df5["金額"]/df5["数量"]*1000

# CSVファイルとして保存
df5.to_csv('./e-Stat/LNG.csv', index=True,encoding='utf-8-sig')