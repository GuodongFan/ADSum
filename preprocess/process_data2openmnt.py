import pandas as pd

for name in ['appium', 'ts', 'ethereum']:

    df = pd.read_csv('./data/gitter/{}.csv'.format(name), header=None)

    bodies = []
    tiles = []
    for index, row in df.iterrows():
        bodies.append(row[1].strip()+'\n')
        tiles.append(row[2]+'\n')

    with open('./data/gitter/body.{}.txt'.format(name), 'w') as file:
        file.writelines(bodies)

    with open('./data/gitter/title.{}.txt'.format(name), 'w') as file:
        file.writelines(tiles)

df = pd.read_csv('./data/github/test.csv')
bodies = []
tiles = []
for index, row in df.iterrows():
    bodies.append(row[1].strip() + '\n')
    tiles.append(row[2] + '\n')

with open('./data/github/discussion_title.test.txt'.format(name), 'w', encoding='utf-8') as file:
    file.writelines(tiles)