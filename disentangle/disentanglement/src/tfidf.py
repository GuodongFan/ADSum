from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import spacy
import numpy as np
import pandas as pd
import argparse

nlp = spacy.load('en_core_web_sm')

# 数据预处理操作：分词，去停用词，词性筛选
def dataPrepos(text, stopkey):
    l = []
    pos = ['NOUN', 'PRON', 'PROPN', 'PERSON', 'vn', 'l', 'a', 'd']  # 定义选取的词性
    doc = nlp(text)
    seg = [t for t in doc]
    for i in seg:
        if i.text not in stopkey and i.pos_ in pos:  # 去停用词 + 词性筛选
            l.append(i.text)
    print(l)
    return l

def getKeywords_tfidf(data,stopkey,topK):
    corpus = data # 将所有文档输出到一个list中，一行就是一个文档
    # 1、构建词频矩阵，将文本中的词语转换成词频矩阵
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus) # 词频矩阵,a[i][j]:表示j词在第i个文本中的词频
    # 2、统计每个词的tf-idf权值
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)
    # 3、获取词袋模型中的关键词
    word = vectorizer.get_feature_names()
    # 4、获取tf-idf矩阵，a[i][j]表示j词在i篇文本中的tf-idf权重
    weight = tfidf.toarray()
    # 5、打印词语权重
    keys = []
    for i in range(len(weight)):
        print("-------这里输出第", i+1 , u"篇文本的词语tf-idf------")

        df_word,df_weight = [],[] # 当前文章的所有词汇列表、词汇对应权重列表
        for j in range(len(word)):
            #print(word[j],weight[i][j])
            df_word.append(word[j])
            df_weight.append(weight[i][j])
        df_word = pd.DataFrame(df_word,columns=['word'])
        df_weight = pd.DataFrame(df_weight,columns=['weight'])
        word_weight = pd.concat([df_word, df_weight], axis=1) # 拼接词汇列表和权重列表
        word_weight = word_weight.sort_values(by="weight",ascending = False) # 按照权重值降序排列
        keyword = np.array(word_weight['word']) # 选择词汇列并转成数组格式
        word_split = [keyword[x] for x in range(0,topK)] # 抽取前topK个词汇作为关键词
        word_split = " ".join(word_split)
        keys.append(word_split.encode("utf-8"))

    return keys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine predictions.')
    parser.add_argument('--files', help='Files containing the predictions.', nargs="+")
    args = parser.parse_args()

    print(args.files)

    for file in args.files:
        data = []
        ending = '.tok.txt'
        if file.endswith(ending):
            out_filename = file[:-len(ending)]
        with open(file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                data.append(line)

        result = getKeywords_tfidf(data, [], 5)
        with open(out_filename+'.tfidf.txt', 'wb+') as outfile:
            for line in result:
                outfile.write(line)
                outfile.write(b'\n')
