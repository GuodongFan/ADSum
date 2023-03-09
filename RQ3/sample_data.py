import os.path
import random
import numpy as np
import json
import csv

#sample 50 github data
discussion_data_dir = './RQ3/compare_discussion'
random.seed(1024)
number_set = list(range(0, 3975))
random_list = []
num_sample = 50

for i in range(num_sample):
    choice_num = random.choice(number_set)
    number_set.remove(choice_num)
    random_list.append(choice_num)

result = []

with open(os.path.join(discussion_data_dir, 'body.test.txt'), encoding='utf-8') as body_f:
    body_lines = body_f.readlines()
    body_randoms = np.array(body_lines)[random_list]

with open(os.path.join(discussion_data_dir, 'iTAPE_step_25000_minlen8.txt'), encoding='utf-8') as itape_f:
    iTAPE_lines = itape_f.readlines()
    itape_randoms = np.array(iTAPE_lines)[random_list]

with open(os.path.join(discussion_data_dir, 'test_1.output'), encoding='utf-8') as out_f:
    our_lines = out_f.readlines()
    our_randoms = np.array(our_lines)[random_list]

with open(os.path.join(discussion_data_dir, 'title.test.txt'), encoding='utf-8') as gd_f:
    gd_lines = gd_f.readlines()
    gd_randoms = np.array(gd_lines)[random_list]

for idx, one in enumerate(body_randoms):
    result.append({'body':one, 'itape':itape_randoms[idx], 'our':our_randoms[idx], 'gd': gd_randoms[idx]})

with open(os.path.join(discussion_data_dir, 'discussion.data'), 'w') as file:
    json.dump(result, file)


#sample 50 gitter data
dialog_data_dir = './RQ3/compare_dialog'
number_set = list(range(1, 1000))
random_list = []
num_sample = 50
result = []

for i in range(num_sample):
    choice_num = random.choice(number_set)
    number_set.remove(choice_num)
    random_list.append(choice_num)

with open(os.path.join(dialog_data_dir, 'appium.csv'), encoding='utf-8') as body_f:
    csv_list = []
    csv_reader = csv.reader(body_f)
    for line in csv_reader:
        pre, body, title = line
        csv_list.append(body)
    body_randoms = np.array(csv_list)[random_list]

gd_randoms = []
with open(os.path.join(dialog_data_dir, 'test_1.gold'), encoding='utf-8') as gd_f:
    new_lines = []
    gd_lines = gd_f.readlines()
    for line in gd_lines:
        fields = line.split('\t')
        new_lines.append(fields[1])
    gd_randoms = np.array(new_lines)[random_list]

our_randoms = []
with open(os.path.join(dialog_data_dir, 'test_1.output'), encoding='utf-8') as out_f:
    new_lines = []
    our_lines = out_f.readlines()
    for line in our_lines:
        fields = line.split('\t')
        new_lines.append(fields[1])
    our_randoms = np.array(new_lines)[random_list]

for idx, one in enumerate(body_randoms):
    result.append({'body':one, 'our':our_randoms[idx], 'gd': gd_randoms[idx]})

with open(os.path.join(dialog_data_dir, 'dialog.data'), 'w') as file:
    json.dump(result, file)