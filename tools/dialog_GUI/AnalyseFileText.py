import re
import json

# 用于生成字符串型的内容
with open("./data/content.annotation(1).txt", encoding="utf-8") as file:
    text = file.read()
    text_list = []
    # 对话组
    dialog_lists = text.split(
        "--------------------------------------------------------------------------------------------------")
    for i in range(len(dialog_lists)):
        message_data = ""
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
                            message = " <" + info_list[1] + "> " + info_list[2]
                        else:
                            message = " <" + info_list[1] + "> " + " "
                        message_data += message
            text_list.append(message_data)

with open("./data/test1.json", "w", encoding='utf-8') as file:
    text = json.dumps(text_list)
    file.write(text)
