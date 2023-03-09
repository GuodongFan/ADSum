import json
import string
from rouge import Rouge
import torch
import pandas as pd
from tqdm import tqdm
from transformers.models.t5 import T5ForConditionalGeneration, T5Tokenizer, T5Config
from openprompt import PromptDataLoader, PromptForGeneration
from openprompt.prompts import PrefixTuningTemplate, SoftTemplate
from openprompt.plms import T5TokenizerWrapper
from openprompt.data_utils import InputExample, InputFeatures

from openprompt.plms import T5TokenizerWrapper

WrapperClass = T5TokenizerWrapper

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_config = T5Config.from_pretrained("t5-base")
model = T5ForConditionalGeneration.from_pretrained("t5-base", config=model_config)
tokenizer = T5Tokenizer.from_pretrained("t5-base")


def get_title(prefix, input_text):
    model = T5ForConditionalGeneration.from_pretrained("./model/checkpoint-best-bleu", config=model_config)
    model.to(DEVICE)
    text = prefix + ": " + input_text
    print(text)
    input_ids = tokenizer(prefix + ": " + input_text, return_tensors="pt", max_length=256, padding="max_length",
                          truncation=True)
    summary_text_ids = model.generate(
        input_ids=input_ids["input_ids"].to(DEVICE),
        attention_mask=input_ids["attention_mask"].to(DEVICE),
        bos_token_id=model.config.bos_token_id,
        eos_token_id=model.config.eos_token_id,
        length_penalty=1.2,
        top_k=5,
        top_p=0.95,
        max_length=20,
        min_length=7,
        num_beams=10,
    )
    title = tokenizer.decode(summary_text_ids[0], skip_special_tokens=True)
    if (len(title) > 0 and title[-1] in string.punctuation):
        title = title[:-1] + " " + title[-1]
    return title


generation_arguments = {
    "max_length": 20,
    "max_new_tokens": None,
    "min_length": 7,
    "temperature": 1.0,
    "do_sample": False,
    "top_k": 5,
    "top_p": 0.95,
    "repetition_penalty": 1.0,
    "num_beams": 10,
    "num_return_sequences": 5
}

if __name__ == '__main__':
    prefix = "Summarization"

    with open('./data/test1.json') as file:
        j = file.read()
        j_list = json.load(j)
        for input in j_list:
            title = get_title(prefix, input)
            print('Title: ', title)
