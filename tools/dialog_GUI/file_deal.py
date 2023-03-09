import json
import pandas as pd

df = pd.read_json('data/text/dialog.json', encoding='utf-8')
body = df['body'].tolist()
our = df['our'].tolist()
gd = df['gd'].tolist()
for i in range(len(body)):
    summary_1 = our[i]
    summary_2 = gd[i]
    dialog = body[i].split('< code >')[0]
    code = body[i].split('< code >')[1]
    s1 = summary_1.split('\t')[1].split('\n')[0]
    s2 = summary_2.split('\t')[1].split('\n')[0]
    print(code)

