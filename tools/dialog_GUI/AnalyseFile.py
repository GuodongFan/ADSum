import re
import json
# 这是用于生成JSON格式的对象以用于程序的对话信息生成
with open("data/text/TypeScript.txt", encoding="utf-8") as file:
    text = file.read()
    text_list = []
    message_id = 0
    # 对话组
    dialog_lists = text.split(
        "--------------------------------------------------------------------------------------------------")
    for i in range(len(dialog_lists)):
        message_data = []
        message_list = dialog_lists[i].split("\n")
        # 如果对话组对话条数多于2条
        if len(message_list) > 4:
            # 解析对话组
            for j in range(len(message_list)):
                # 解析每条对话的内容(包括用户,时间,对话内容)
                info_list = re.split("[\[\t\]<>]", message_list[j].strip())
                while "" in info_list:  # 判断是否有空值在列表中
                    info_list.remove("")  # 如果有就直接通过remove删除
                if len(message_list[j]) != 0:
                    if len(info_list) != 0 and len(message_list[j]) != 0:
                        if len(info_list) > 2:
                            message = {"time": info_list[0], "name": info_list[1], "text": info_list[2]}
                        else:
                            message = {"time": info_list[0], "name": info_list[1], "text": ''}
                        message_data.append(message)
            one = {"id": message_id, "data": message_data}
            text_list.append(one)
            message_id = message_id + 1

with open("data/dialogs/TypeScript.json", "w", encoding='utf-8') as file:
    text = json.dumps(text_list)
    file.write(text)
