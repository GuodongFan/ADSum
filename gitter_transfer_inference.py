import json
import string
from rouge import Rouge
import torch
import pandas as pd
from tqdm import tqdm
from transformers.models.t5 import T5ForConditionalGeneration, T5Tokenizer,T5Config

from openprompt.plms import T5TokenizerWrapper


WrapperClass = T5TokenizerWrapper

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_config = T5Config.from_pretrained("t5-base")
#model = T5ForConditionalGeneration.from_pretrained("t5-base", config=model_config)
model = T5ForConditionalGeneration.from_pretrained("../model/checkpoint-best-bleu", config=model_config)


tokenizer = T5Tokenizer.from_pretrained("t5-base")
rouge = Rouge()
model.to(DEVICE)
rouge1_score = 0
rouge2_score = 0
rougeL_score = 0
rouge_count = 0


def get_title(prefix, input_text, model):
    print(prefix + ": " + input_text)
    input_ids = tokenizer(prefix+": "+input_text ,return_tensors="pt", max_length=512, padding="max_length", truncation=True)
    summary_text_ids = model.generate(
        input_ids=input_ids["input_ids"].to(DEVICE),
        attention_mask=input_ids["attention_mask"].to(DEVICE),
        bos_token_id=model.config.bos_token_id,
        eos_token_id=model.config.eos_token_id,
        length_penalty=1.2,
        top_k=5,
        top_p=0.95,
        max_length=20,
        min_length=5,
        num_beams=10,
    )
    title = tokenizer.decode(summary_text_ids[0], skip_special_tokens=True)
    return title

generation_arguments = {
    "max_length": 20,
    "max_new_tokens": None,
    "min_length": 5,
    "temperature": 1.0,
    "do_sample": False,
    "top_k": 5,
    "top_p": 0.95,
    "repetition_penalty": 1.0,
    "num_beams": 10,
    "num_return_sequences":5
}


if __name__ == '__main__':

    model = T5ForConditionalGeneration.from_pretrained("t5-base", config=model_config)
    #model = T5ForConditionalGeneration.from_pretrained("./model_github_ft/checkpoint-best-bleu", config=model_config)
    model.to(DEVICE)

    data_csv = pd.read_csv('./data/gitter/appium.csv', header=None)
    #data_csv = pd.read_csv('./data/github/test.csv')
    ground_truth = './output/gd.out'
    gen_output = './output/gen.out'

    with open(ground_truth, 'w', encoding='utf-8') as file1, open(gen_output, 'w', encoding='utf-8') as file2:
        for idx, row in tqdm(data_csv.iterrows(), total=len(data_csv)):
            prefix = row[0]
            body = row[1]
            truth = row[2]
            title = get_title('summarize', body, model)
            print(title)
            file1.write(truth+'\n')
            file2.write(title+'\n')


