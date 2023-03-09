"""
为ｇitter聊天纪录里面的时间加上Ｔ
"""
import glob

files = glob.glob('src/disentanglement/proposed_dataset/original_format/*/*.ascii.txt')


for file_name in files:

    lines = None
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(file_name,"w",encoding="UTF-8") as file:
        for line in lines:
            splits = line.split(" ",1)
            file.write(splits[0]+"T"+splits[1])