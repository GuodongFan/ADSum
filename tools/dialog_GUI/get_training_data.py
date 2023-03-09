import json
import pandas as pd

data_json = [
    {
        "dialog":'./data/dialogs/appium.json',
        "title":'./data/annotations/annotation_appium_2.json',
        "result":'./data/csv/appium.csv'
    },
    {
        "dialog": './data/dialogs/ethereum.json',
        "title": './data/annotations/annotation_ethereum_2.json',
        "result": './data/csv/ethereum.csv'
    },
    {
        "dialog": './data/dialogs/ts.json',
        "title": './data/annotations/annotation_ts_2.json',
        "result": './data/csv/ts.csv'
    },
]


for dialog_title in data_json:

    dialog_dic = {}
    with open(dialog_title['dialog']) as file:
        dialog_j = json.loads(file.read())
        for one in dialog_j:
            print(one)
            id = one['id']
            datas = one['data']
            dialog_text = ''
            for d in datas:
                dialog_text += ' <SEP> ' + d['text']
            dialog_dic[id] = dialog_text

    data_prefix = []
    data_dialogs = []
    data_titles = []
    with open(dialog_title['title']) as file:
        title_j = json.loads(file.read())
        for one in title_j:
            id = one['dialog_id']
            title = one['title']
            type = one['type']
            if int(type) == 4:
                continue
            if len(title) == 0:
                continue
            dialog_text = dialog_dic.get(id)
            if dialog_text == None:
                continue
            #print(dialog_text)
            #print(title)
            data_prefix.append('Summarization')
            data_dialogs.append(dialog_text.replace('\n', ' '))
            data_titles.append(title.replace('\n', ' '))

    #字典中的key值即为csv中列名
    dataframe = pd.DataFrame({'prefix':data_prefix,'dialog':data_dialogs, 'title': data_titles})
    #将DataFrame存储为csv,index表示是否显示行名，default=True
    dataframe.to_csv(dialog_title['result'], index=False,sep=',')