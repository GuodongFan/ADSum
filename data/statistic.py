import pandas as pd
import glob

files = glob.glob('./*/*.csv')
print(files)


for file in files:
    all_title_len = 0
    all_body_len = 0
    all_idx = 0
    all_messages = 0
    df = pd.read_csv(file)
    df.columns = ['prefix', 'body', 'title']
    #print(df)
    for index, row in df.iterrows():
        all_words = row['body'].split()
        for word in all_words:
            if word == '<SEP>':
                all_messages += 1
        new_list = [word for word in all_words if '<SEP>' not in word]
        number_words = len(new_list)
        #print(number_words)
        all_body_len += len(new_list)


        all_words = row['title'].split()
        new_list = [word for word in all_words if '<SEP>' not in word]
        number_words = len(new_list)
        #print(number_words)
        all_title_len += len(new_list)

        all_idx += 1
    print(file)
    print(f'body len {all_body_len/all_idx}')
    print(f'title len {all_title_len/all_idx}')
    print(f'messages len {all_messages}')
