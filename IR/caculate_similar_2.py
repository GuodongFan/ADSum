import pickle
import faiss
import torch
import numpy as np
#import Levenshtein
from nlgeval import compute_metrics
from tqdm import tqdm

from transformers import RobertaTokenizer, RobertaModel
import pandas as pd

from bert_whitening import sents_to_vecs, transform_and_normalize
MODEL_NAME = 'microsoft/codebert-base' # 本地模型文件
dim = 256

df = pd.read_csv("data/gitter/appium.csv", header=None)
test_code_list = df[1].tolist()
test_id_list = df[2].tolist()


df = pd.read_csv("data/gitter/ts.csv", header=None)
train_code_list = df[1].tolist()
train_id_list = df[2].tolist()


tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
model = RobertaModel.from_pretrained(MODEL_NAME)
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(DEVICE)

def calculate_time_difference(t1 , t2, is_abs = True):
    if t1[-1] == ']':
        t1 = t1[:-1]
    if t2[-1] == ']':
        t2 = t2[:-1]
    if t1[0] == '[':
        t1 = t1[1:]
    if t2[0] == '[':
        t2 = t2[1:]
    if t1[-1] == 'Z':
        t1 = t1[:-1]
    if t2[-1] == 'Z':
        t2 = t2[:-1]
    if is_abs:
        return abs(parse(t1)-parse(t2)).days
    else:
        return (parse(t1)-parse(t2)).days

def sim_jaccard(s1, s2):
    """jaccard相似度"""
    s1, s2 = set(s1), set(s2)
    ret1 = s1.intersection(s2)  # 交集
    ret2 = s1.union(s2)  # 并集
    sim = 1.0 * len(ret1) / len(ret2)
    return sim

class Retrieval(object):
    def __init__(self):
        f = open('models/code_vector_whitening_issues.pkl', 'rb')
        self.bert_vec = pickle.load(f)
        f.close()
        f = open('models/kernel_issues.pkl', 'rb')
        self.kernel = pickle.load(f)
        f.close()
        f = open('models/bias_issues.pkl', 'rb')
        self.bias = pickle.load(f)
        f.close()

        self.id2text = None
        self.vecs = None
        self.ids = None
        self.index = None

    def encode_file(self):
        all_texts = []
        all_ids = []
        all_vecs = []
        for i in range(len(train_code_list)):
            all_texts.append(train_code_list[i])
            all_ids.append(i)
            all_vecs.append(self.bert_vec[i].reshape(1,-1))
        all_vecs = np.concatenate(all_vecs, 0)
        id2text = {idx: text for idx, text in zip(all_ids, all_texts)}
        self.id2text = id2text
        self.vecs = np.array(all_vecs, dtype="float32")
        self.ids = np.array(all_ids, dtype="int64")

    def build_index(self, n_list):
        quant = faiss.IndexFlatIP(dim)
        index = faiss.IndexIVFFlat(quant, dim, min(n_list, self.vecs.shape[0]))
        index.train(self.vecs)
        index.add_with_ids(self.vecs, self.ids)
        self.index = index

    def single_query(self, code, topK):
        body = sents_to_vecs([code], tokenizer, model)
        body = transform_and_normalize(body, self.kernel, self.bias)
        vec = body[[0]].reshape(1, -1).astype('float32')
        _, sim_idx = self.index.search(vec, topK)
        max_idx = sim_idx[0]
        '''sim_idx = sim_idx[0].tolist()
        max_score = 0
        max_idx = 0
        code_score_list = []
        ast_score_list = []
        for j in sim_idx:
            code_score = sim_jaccard(train_code_list[j].split(), code.split())
            ast_score = Levenshtein.seqratio(str(train_code_list[j]).split(), str(code).split())
            code_score_list.append(code_score)
            ast_score_list.append(ast_score)
        for i in range(len(sim_idx)):
            code_score = code_score_list[i]
            ast_score = ast_score_list[i]
            score = 0.7*code_score + 0.3*ast_score
            if score > max_score:
                max_score = score
                max_idx = sim_idx[i]'''
        return np.array(train_code_list)[sim_idx], np.array(train_id_list)[sim_idx], np.array(train_code_list)[max_idx]

if __name__ == '__main__':
    ccgir = Retrieval()
    print("Sentences to vectors")
    ccgir.encode_file()
    print("加载索引")
    ccgir.build_index(n_list=1)
    ccgir.index.nprob = 1
    sim_nl_list, c_list, sim_score_list, nl_list = [], [], [], []
    data_list = []
    for i in tqdm(range(len(test_code_list))):
        #if isinstance(test_id_list[i], float) and test_id_list[i] >= 0:
        #print('truth:%d'  %(test_id_list[i]))
        print('问题 ', test_code_list[i])
        sim_code, sim_id, most_sim_code = ccgir.single_query(test_code_list[i], topK=10)
        print(sim_id)
        print(sim_code)
        print(most_sim_code)
        sim_nl_list.append(str(sim_id[0][0]).replace('\n', '')+'\n')
        nl_list.append(test_id_list[i].replace('\n', '')+'\n')

    df = pd.DataFrame(nl_list)
    df.to_csv("nl.csv", index=False,header=None)
    df = pd.DataFrame(sim_nl_list)
    df.to_csv("sim.csv", index=False,header=None)

    metrics_dict = compute_metrics(hypothesis='sim.csv',
                                   references=['nl.csv'],no_skipthoughts=True, no_glove=True)

    with open('./ir.txt', 'w', encoding='utf-8') as f:
        f.writelines(sim_nl_list)
