import glob
import json

files = glob.glob('./statistic_data/manual_score/*_discussion.json')
print(files)

for file in files:
    with open(file, 'r') as f:
        js = json.load(f)
        for one in js:
            score = json.loads(one['score'])
            if len(score) != 3:
                continue

            print(score['itape'][3])

files = glob.glob('./statistic_data/manual_score/*_dialog.json')
print(files)

for file in files:
    with open(file, 'r') as f:
        js = json.load(f)
        for one in js:
            score = json.loads(one['score'])
            if len(score) != 2:
                continue

            #print(score['gd'][0])

