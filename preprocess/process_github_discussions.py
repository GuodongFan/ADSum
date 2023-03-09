from sklearn.model_selection import train_test_split
from text_processor import Processor
from glob import glob
import json
import hashlib
import os
import sys
import math
from cleantext import clean
from readability import Readability
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import pandas as pd
import numpy as np
import json, re
import nltk

from tqdm import tqdm

DATA_DIR = 'D://data_discussions/'

if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)

marks = ['<url>', '<email>', '<percent>', '<money>', '<phone>', '<user>',
                     '<date>', '<number>', '<ukn>']

str_body = """
"<p dir=\"auto\">Hey <a class=\"user-mention notranslate\" data-hovercard-type=\"user\" data-hovercard-url=\"/users/calebporzio/hovercard\" data-octo-click=\"hovercard-link-click\" data-octo-dimensions=\"link_type:self\" href=\"https://github.com/calebporzio\">@calebporzio</a>! I'm trying this with version 3.2.0 and 3.2.2 and in either case the Alpine syntax inside the x-html is not evaluated when it's within a template block.</p>\n<div class=\"highlight highlight-text-html-basic notranslate position-relative overflow-auto\" data-snippet-clipboard-copy-content=\"&lt;ul x-data=&quot;{items: [...], x: 12}&quot;&gt;\n  &lt;li x-html=&quot;`&lt;h2 x-text=x&gt;&lt;/h2&gt;`&quot;&gt;&lt;/li&gt; &lt;!-- This works  --&gt;\n  &lt;template x-for=&quot;(item,i) in items&quot;&gt;\n     &lt;li x-html=&quot;`&lt;h2 x-text=item&gt;&lt;/h2&gt;`&quot;&gt;&lt;/li&gt; &lt;!-- This does not--&gt;\n  &lt;/template&gt;\n&lt;/ul&gt;\"><pre><span class=\"pl-kos\">&lt;</span><span class=\"pl-ent\">ul</span> <span class=\"pl-c1\">x-data</span>=\"<span class=\"pl-s\">{items: [...], x: 12}</span>\"<span class=\"pl-kos\">&gt;</span>\n  <span class=\"pl-kos\">&lt;</span><span class=\"pl-ent\">li</span> <span class=\"pl-c1\">x-html</span>=\"<span class=\"pl-s\">`&lt;h2 x-text=x&gt;&lt;/h2&gt;`</span>\"<span class=\"pl-kos\">&gt;</span><span class=\"pl-kos\">&lt;/</span><span class=\"pl-ent\">li</span><span class=\"pl-kos\">&gt;</span> <span class=\"pl-c\">&lt;!-- This works  --&gt;</span>\n  <span class=\"pl-kos\">&lt;</span><span class=\"pl-ent\">template</span> <span class=\"pl-c1\">x-for</span>=\"<span class=\"pl-s\">(item,i) in items</span>\"<span class=\"pl-kos\">&gt;</span>\n     <span class=\"pl-kos\">&lt;</span><span class=\"pl-ent\">li</span> <span class=\"pl-c1\">x-html</span>=\"<span class=\"pl-s\">`&lt;h2 x-text=item&gt;&lt;/h2&gt;`</span>\"<span class=\"pl-kos\">&gt;</span><span class=\"pl-kos\">&lt;/</span><span class=\"pl-ent\">li</span><span class=\"pl-kos\">&gt;</span> <span class=\"pl-c\">&lt;!-- This does not--&gt;</span>\n  <span class=\"pl-kos\">&lt;/</span><span class=\"pl-ent\">template</span><span class=\"pl-kos\">&gt;</span>\n<span class=\"pl-kos\">&lt;/</span><span class=\"pl-ent\">ul</span><span class=\"pl-kos\">&gt;</span></pre></div>
"""

def code2text(code_list):
    text = ''
    for code in code_list:
        if isinstance(code, NavigableString):
            text += code
        else:
            text+= ' ' + code.get_text()
    return text




def get_code(html):
    extract_list = ['highlight-source-js', 'snippet-clipboard-content', 'highlight-source-ts', 'highlight-text-html-basic', 'highlight']
    soup = BeautifulSoup(html, 'lxml')
    code_list = []

    for extract in extract_list:
        code = soup.find_all('div', class_=extract)
        code_list.extend([c for c in code])
        [s.extract() for s in code_list]

    code = code2text(set(code_list))

    #info = [s.extract() for s in code_list]
    return code, soup.text

# replace miscellaneous information in title
def improve_title(issue_title):
    original_len = len(issue_title)
    issue_title = re.sub("^(\s*\[.*?\])+", "", issue_title)  # remove starting [tag]
    pos = issue_title.find(": ")
    if -1 < pos < len(issue_title) - original_len / 2:
        issue_title = issue_title[pos + 1:].strip()  # removing starting tag:
    issue_title = re.sub("^(\s*\[.*?\])+", "", issue_title)  # remove starting [tag] x2
    issue_title = re.sub("(\*{1,})(.+?)(\*{1,})", lambda x: x.group(2), issue_title)  # remove emphasis
    return issue_title.strip()

# TITLE expressiveness filter: title should with token number within [5,15] and contain no urls
def rule1checker(issue_title, issue_title_word):
    length = len(issue_title_word)
    if length < 3:
        return True
    if length > 18:
        return True
    if len(re.findall("(https?|ftp)://[^\s/$.?#].[^\s]*", issue_title)) > 0:
        return True
    return False


# TITLE relation filter: title hit token count should meet threshold
def rule2checker(issue_title_words, issue_body_words):
    body_words_set = set(issue_body_words)
    cnt_each = 0
    for word in issue_title_words:
        if word in body_words_set:
            cnt_each += 1
    if cnt_each <= len(issue_title_words) * 0.3:  # less than 30% tokens hit, not one-sentence summarization
        return True
    return False


# TITLE copy (directly extract) filter: title copied substring length threshold
def rule3checker(issue_title, issue_title_tokenize, issue_body_tokenize):
    title_words = [x.lower() for x in issue_title_tokenize]
    body_words = [x.lower() for x in issue_body_tokenize]
    exp = ""
    # build substring location RE: (\s+AA)(\s+BB)(\s+CC)(\s+DD) to match AA BB CC (more postfix in title), BB CC DD (more prefix in title), AA BB DD (more tokens, such as punctuations, in title) etc. in body.
    for _ in title_words:
        _ = re.escape(_)
        exp += "(" + "\s+" + _ + ")?"
    re_iter = re.compile(exp)
    each_cnt = 0
    for s in re_iter.finditer(" " + " ".join(body_words)):
        each_each_cnt = 0
        for _ in s.groups():
            if _ is not None:
                each_each_cnt += 1
        each_cnt = max(each_cnt, each_each_cnt)
    if each_cnt >= len(title_words) * 0.7:  # bad title - abnormal tag
        return True
    return False



def hashhex(s):
  """Returns a heximal formated SHA1 hash of the input string."""
  h = hashlib.sha1()
  h.update(s.encode())
  return h.hexdigest()

def filter_rub(text):
    text = str.lower(text)
    fields = text.split(' ')
    all_num = len(fields)
    mark_num = 0
    for field in fields:
        if field in marks:
            mark_num += 1

    return mark_num/all_num


def write_urls(urls, filename):
    with open(filename, 'w') as file:
        for url in urls:
            file.write(url)
            file.write('\n')

def filter_data(text):
    result = clean(text,
                   fix_unicode=True,  # fix various unicode errors
                   to_ascii=True,  # transliterate to closest ASCII representation
                   lower=True,  # lowercase text
                   no_line_breaks=True,  # fully strip line breaks as opposed to only normalizing them
                   no_urls=True,  # replace all URLs with a special token
                   no_emails=True,  # replace all email addresses with a special token
                   no_phone_numbers=True,  # replace all phone numbers with a special token
                   no_numbers=False,  # replace all numbers with a special token
                   no_digits=False,  # replace all digits with a special token
                   no_currency_symbols=True,  # replace all currency symbols with a special token
                   no_punct=False,  # remove punctuations
                   replace_with_punct="",  # instead of removing punctuations you may replace them
                   replace_with_url="<URL>",
                   replace_with_email="<EMAIL>",
                   replace_with_phone_number="<PHONE>",
                   replace_with_number="<NUMBER>",
                   replace_with_digit="<DIGIT>",
                   replace_with_currency_symbol="<CUR>",
                   lang="en")

    return result

def readability(text):
    r = Readability(text)
    return r.flesch()

fetures_list = [
    'New Features & Project Ideas',
    'Ideas / Proposals',
    'Show & Tell',
    'Extension request',
    'Ideas / Feature request',
    'Show and tell',
    'Suggestions',
    'Feature Ideas',
    'Features',
    'Help: Model Advice',
    'Show and Tell',
    'Idea pool',
    'Ideas & Suggestions',
    'Feature Suggestions',
    'Ideas / Feature Requests',
'Ideas',
'Q&A / Support',

]

bug_list = [
'Bugs',
'Error / Bug Report',

]

question_list = [
    'Help & Questions',
    'WTF Questions',
    'Help: Other Questions',
    'Questions',
    'General help wanted',
    'FAQ & Tips',
    'Help / Questions',
    'Q&A',
    'Help',
    'Question & Answer',
    'Feature Requests',
    'Help: Coding & Implementations',
    'Q & A',
    'Questions and Help',
    'Help: Best practices',
    'code help: RL / MetaLearning'
]

general_list = [
    'General - Components / Directives / etc',
    'General',
    'Discussions',
]

def get_type(type):
    for s in fetures_list:
        if type == s:
            return 'feature request'
    for s in question_list:
        if type == s:
            return 'question and answer'
    for s in general_list:
        if type == s:
            return 'general'
    return 'other'

if __name__ == '__main__':
    #process = Processor()

    all_count = 0
    files = glob("./src/crawler_github/data/discussions_*.txt")
    print("**process discussion**")
    for file in tqdm(files, total=len(files)):
        with open(file, 'r') as read_file:
            lines = read_file.readlines()
            count = len(lines)
            all_count += count

    print('all count ', all_count)

    with open("./src/process_data/refined_38964issues_reponobodytitlespctok.json") as file:
        jdata = json.load(file)
        print(len(jdata))

    #exit(0)

    generation_txt =  DATA_DIR + "data.csv"
    class_text = DATA_DIR + "class.csv"

    train_csv = DATA_DIR + 'train.csv'
    test_csv = DATA_DIR + 'test.csv'
    valid_csv = DATA_DIR + 'valid.csv'

    random_seed = 1024
    all_urls = []
    categories = {}
    all_count = 0

    # test

    code, body = get_code(str_body)
    body = filter_data(body)
    print(body)
    print('**example**')
    print(code)

    if True:

        # 如果存在生成的文件则删除, 不然data会累积
        if os.path.exists("%s" % generation_txt):
            os.remove(generation_txt)
        if os.path.exists("%s" % class_text):
            os.remove(class_text)
        files = glob("./src/crawler_github/data/discussions_*.txt")
        print("**process discussion**")
        for file in tqdm(files, total=len(files)):
            with open(file, 'r') as read_file:
                lines = read_file.readlines()
                for line in lines:
                    j_line = json.loads(line)
                    url = j_line['node']['url']
                    title = j_line['node']['title']
                    body = j_line['node']['bodyHTML']
                    upvoteCount = j_line['node']['upvoteCount']
                    isanswer = j_line['node']['answer']
                    category = j_line['node']['category']['name']
                    all_urls.append(url)
                    filename = hashhex(url )+ ".story"
                    #if upvoteCount > 1 or isanswer:

                    #code, body = get_code(body)
                    #title = improve_title(title)
                    title = filter_data(title)
                    body = filter_data(body)
                    #code = filter_data(code)

                    #print('code: ', code)
                    #code = code.replace('<code>', ' ')
                    #code = code.replace('</code>', ' ')
                    #body = body + ' <code> ' + code
                    #body = body.split()[0:200]

                    issue_body_tokenize = nltk.word_tokenize(body)
                    issue_title_tokenize = nltk.word_tokenize(title)

                    issue_title_words = [x.lower() for x in issue_title_tokenize if re.match("\S*[A-Za-z0-9]+\S*", x)]
                    issue_body_words = [x.lower() for x in issue_body_tokenize if
                                        re.match("\S*[A-Za-z0-9]+\S*", x)]

                    if (rule1checker(title, issue_title_words)) \
                            or (rule2checker(issue_title_words, issue_body_words)) \
                            or (
                            rule3checker(title, issue_title_tokenize,
                                         issue_body_tokenize)):  # can disable any rule for ablation
                        continue
                    columns = ['prefix', 'input_text', 'target_text']
                    data = pd.DataFrame([['summarization', body, title]], columns=columns)
                    data.to_csv('%s' % generation_txt, mode='a', index=False, header=False)
                    data = pd.DataFrame([['classify', body, category]], columns=columns)
                    data.to_csv('%s' % class_text, mode='a', index=False, header=False)
                    '''if len(title.split(' ')) >= 3 and len(body) > 30 and len(category) > 0:
                        if upvoteCount > 5 or isanswer:
                            all_count += 1
                            print(title)
                            if categories.get(category) == None:
                                categories[category] = 1
                            else:
                                categories[category] += 1
                            columns = ['prefix', 'input_text', 'target_text']
                            data = pd.DataFrame([['sum', ' '.join(body), title]], columns=columns)
                            data.to_csv('./%s' % generation_txt, mode='a', index=False, header=False)
                            data = pd.DataFrame([['type', ' '.join(body), category]], columns=columns)
                            data.to_csv('./%s' % class_text, mode='a', index=False, header=False)'''
        print(all_count)
        print(categories)
        for key, val in categories.items():
            print(key)

        for key, val in categories.items():
            print(val)
        '''                with open(DATA_DIR + filename, 'w') as write_file:
                            try:
                                title = process(title)
                                if filter_rub(title) > 0.8:
                                    print('filter rub > 0.8 ', title)
                                    continue
                                body = process(body)
                                write_file.write(body)
                                write_file.write('\n@highlight\n')
                                write_file.write(title)
                            except:
                                print('exception:')
                                print(file)
                                print(url)
        
        '''

    # 删掉之前生成的.txt文件 重新生成
    files = glob(DATA_DIR + '*.txt')
    files.append(train_csv)
    files.append(test_csv)
    files.append(valid_csv)
    for file in files:
        if os.path.exists(file):
            os.remove(file)
    texts = [generation_txt, None]
    for index_text, file in enumerate(texts):
        if file == None:
            continue
        data = pd.read_csv('%s' % file)
        data.columns = ['prefix', 'input_text', 'target_text']

        train_data, valid_test_data = train_test_split(data, test_size=0.3, random_state=random_seed)
        test_data, valid_data = train_test_split(valid_test_data, test_size=0.5, random_state=random_seed)
        dic = set()
        with open(DATA_DIR + "body.train.txt", "a", encoding='utf-8') as fbody, open(DATA_DIR + "title.train.txt", "a", encoding='utf-8') as ftitle:
            bodies = train_data['prefix'] + ': ' + train_data['input_text'] + '\n'
            titles = train_data['target_text'] + '\n'
            if index_text == 1: # 如果是类型
                titles = [get_type(x)+'\n' for x in train_data['target_text']]
            fbody.writelines(bodies)
            ftitle.writelines(titles)
            columns = ['prefix', 'input_text', 'target_text']
            input_tolist = train_data['input_text'].values.tolist()
            pre_list = train_data['prefix'].values.tolist()
            target_list = train_data['target_text'].values.tolist()
            for idx, input in enumerate(input_tolist):
                target_text = target_list[idx]
                if index_text == 1:
                    target_text = get_type(target_text)
                data = pd.DataFrame([[pre_list[idx], input, target_text]], columns=columns)
                data.to_csv(train_csv, mode='a', index=False, header=False)

        with open(DATA_DIR + "body.valid.txt", "a", encoding='utf-8') as fbody, open(DATA_DIR + "title.valid.txt", "a", encoding='utf-8') as ftitle:
            bodies = valid_data['prefix'] + ': ' + valid_data['input_text'] + '\n'
            titles = valid_data['target_text'] + '\n'
            if index_text == 1:
                titles = [get_type(x)+'\n' for x in valid_data['target_text']]
            fbody.writelines(bodies)
            ftitle.writelines(titles)

            input_tolist = valid_data['input_text'].values.tolist()
            pre_list = valid_data['prefix'].values.tolist()
            target_list = valid_data['target_text'].values.tolist()
            for idx, input in enumerate(input_tolist):
                target_text = target_list[idx]
                if index_text == 1:
                    target_text = get_type(target_text)
                columns = ['prefix', 'input_text', 'target_text']
                data = pd.DataFrame([[pre_list[idx], input, target_text]], columns=columns)
                data.to_csv(valid_csv, mode='a', index=False, header=False)

        with open(DATA_DIR + "body.test.txt", "a", encoding='utf-8') as fbody, open(DATA_DIR + "title.test.txt", "a", encoding='utf-8') as ftitle:
            bodies = test_data['prefix'] + ': ' + test_data['input_text'] + '\n'
            titles = test_data['target_text'] + '\n'
            if index_text == 1:
                titles = [get_type(x)+'\n' for x in test_data['target_text']]
            fbody.writelines(bodies)
            ftitle.writelines(titles)

            input_tolist = test_data['input_text'].values.tolist()
            pre_list = test_data['prefix'].values.tolist()
            target_list = test_data['target_text'].values.tolist()
            for idx, input in enumerate(input_tolist):
                target_text = target_list[idx]
                if index_text == 1:
                    target_text = get_type(target_text)
                columns = ['prefix', 'input_text', 'target_text']
                data = pd.DataFrame([[pre_list[idx], input, target_text]], columns=columns)
                data.to_csv(test_csv, mode='a', index=False, header=False)

        print(dic)
