import pandas as pd
import os
import re

# chatroom group html id issue mentions sent text urls username

Appium_file = 'test_Typescript'

columns = ['chatroom', 'group', 'html', 'id', 'issue', 'mentions', 'sent', 'text', 'urls', 'username']

list_data = []
with open(os.path.join('./proposed_dataset/original_format/', Appium_file, 'Typescript.ascii.txt'), 'r', encoding='utf-8') as file:
    lines = file.readlines()

    for idx, line in enumerate(lines):
        fields = line.split()
        sent = fields[0].replace('T', ' ').replace('[', '').replace(']', '')
        username = fields[1]
        username = username.replace('<', '').replace('>', '')
        text = ' '.join(fields[2:]).strip()
        chatroom = Appium_file
        group = Appium_file
        html = text
        id = str(idx)
        issues = ''

        mentions = []
        for field in fields[2:]:
            if re.match(r'^@[\u4E00-\u9FA5A-Za-z0-9_]+$', field):
                mentions.append(field.replace('@', ''))
        mentions = (',').join(mentions)

        urls = []
        for field in fields[2:]:
            if re.match(r'^https?:/{2}\w.+$', field):
                urls.append(field)
        urls = (',').join(urls)
        list_data.append([chatroom, group, html, id, issues, mentions, sent, text, urls, username])


    data = pd.DataFrame(list_data, columns=columns)
    data.to_csv('./data/test.csv')
