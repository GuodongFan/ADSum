from rouge import Rouge
from bert_score import score
import json

total_bert = 0
total_rouge = 0
bert_list = []
rouge_list = []
count = 0
rouger = Rouge()
with open('./appium.json', 'r') as file:
    arrays = json.load(file)

    count = len(arrays)
    for item in arrays:
        ref = item['former']
        pred = item['update']
        (P, R, F), hashname = score([pred], [ref], lang="en", return_hash=True)
        total_bert += F
        print(float(F))
        bert_list.append(float(F))

    print('calculate rouge')

    for item in arrays:
        ref = item['former']
        pred = item['update']
        scores = rouger.get_scores(pred, ref)
        total_rouge += scores[0]['rouge-l']['f']
        print(scores[0]['rouge-l']['f'])
        rouge_list.append(scores[0]['rouge-l']['f'])


print(bert_list)
print(rouge_list)
print(total_rouge / count)
print(total_bert / count)


total_bert = 0
total_rouge = 0
bert_list = []
rouge_list = []
count = 0
rouger = Rouge()
with open('./ts.json', 'r') as file:
    arrays = json.load(file)

    count = len(arrays)
    for item in arrays:
        ref = item['former']
        pred = item['update']
        scores = rouger.get_scores(pred, ref)
        (P, R, F), hashname = score([pred], [ref], lang="en", return_hash=True)
        total_bert += F
        print(float(F))
        bert_list.append(float(F))

    print('calculate rouge')

    for item in arrays:
        ref = item['former']
        pred = item['update']
        scores = rouger.get_scores(pred, ref)
        (P, R, F), hashname = score([pred], [ref], lang="en", return_hash=True)
        total_rouge += scores[0]['rouge-l']['f']
        print(scores[0]['rouge-l']['f'])
        rouge_list.append(scores[0]['rouge-l']['f'])


print(bert_list)
print(rouge_list)
print(total_rouge / count)
print(total_bert / count)
bert_list = []
rouge_list = []
total_bert = 0
total_rouge = 0
count = 0
with open('./eth.json', 'r') as file:
    arrays = json.load(file)

    count = len(arrays)
    for item in arrays:
        ref = item['former']
        pred = item['update']
        scores = rouger.get_scores(pred, ref)
        (P, R, F), hashname = score([pred], [ref], lang="en", return_hash=True)
        total_bert += F
        print(float(F))
        bert_list.append(float(F))

    print('calculate rouge')

    for item in arrays:
        ref = item['former']
        pred = item['update']
        scores = rouger.get_scores(pred, ref)
        (P, R, F), hashname = score([pred], [ref], lang="en", return_hash=True)
        total_rouge += scores[0]['rouge-l']['f']
        print(scores[0]['rouge-l']['f'])
        rouge_list.append(scores[0]['rouge-l']['f'])

print(bert_list)
print(rouge_list)
print(total_rouge / count)
print(total_bert / count)