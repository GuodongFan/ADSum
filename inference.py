import json
import string
from rouge import Rouge
import os
import torch
import pandas as pd
from tqdm import tqdm
from transformers.models.t5 import T5ForConditionalGeneration, T5Tokenizer,T5Config

from openprompt.plms import T5TokenizerWrapper
from openprompt import PromptDataLoader, PromptForGeneration
from openprompt.plms import T5TokenizerWrapper
from openprompt.prompts import PrefixTuningTemplate,SoftTemplate
from openprompt.data_utils import InputExample

WrapperClass = T5TokenizerWrapper

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_config = T5Config.from_pretrained("t5-base")
#model = T5ForConditionalGeneration.from_pretrained("t5-base", config=model_config)
model = T5ForConditionalGeneration.from_pretrained("./model_gitter_prompt/checkpoint-last", config=model_config)


tokenizer = T5Tokenizer.from_pretrained("t5-base")
rouge = Rouge()
model.to(DEVICE)
rouge1_score = 0
rouge2_score = 0
rougeL_score = 0
rouge_count = 0




generation_arguments = {
    "max_length": 20,
    "max_new_tokens": None,
    "min_length": 5,
    "temperature": 1.0,
    "do_sample": True,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.0,
    "num_beams": 20,
    "num_return_sequences":5
}


if __name__ == '__main__':

    #model = T5ForConditionalGeneration.from_pretrained("t5-base", config=model_config)
    plm = T5ForConditionalGeneration.from_pretrained("t5-base", config=model_config)

    promptTemplate = SoftTemplate(model=plm, tokenizer=tokenizer,
                                  text='summarize: {"placeholder":"text_a"} {"mask"}', initialize_from_vocab=True,
                                  num_tokens=20)
    # get model
    model = PromptForGeneration(plm=plm, template=promptTemplate, freeze_plm=False, tokenizer=tokenizer,
                                plm_eval_mode=True)
    model.load_state_dict(torch.load(os.path.join('./model_gitter_prompt/checkpoint-last', "pytorch_model.bin")))
    model.to(DEVICE)
    prefix = 'Text: {"placeholder":"text_a"} Summarization:'
    body = "<SEP> Hi, is someone use the latest Appium version and the inspector ? Because since I've updated my Appium version to the latest I'm no more able to select my UI elements through the app overview on the right side of the inspector. Is there a new option to enable this functionality ? <SEP> its a known issue, lots of people logged bugs for it <SEP> ok fine, we just have to wait for a fix then. Thanks for the information @Simon-Kaz"

    body = ",<SEP> oh wait i know how i can distinguished between bodyOrFilters <SEP> If first param is `object` then `bodyOrFilters` has to be `filters` <SEP> if first param is `string` then `bodyOrFilters` is `body` <SEP> :-) <SEP> Seems like it would be way easier if you j     ust put body as the first param <SEP> oh yeah then they would be always the same <SEP> 100% better <SEP> ```ts     protected async postRequest(body: any, ...filters: Filter <SEP> Awesome, thanks @keithlayne <SEP> :thumbsup:"
    body = 'i have read in the docs that a custom express server disables automatic static optimization . after doing some research i was unfortunately still not able to find out whether this means that every page is server-side rendered . or to put it in a different way : is it possible to serve static pages with a custom server ? would appreciate any help to clarify my confusion .'
    dataset = {}
    dataset['test'] = []
    input_example = InputExample(text_a=body, text_b='')
    dataset['test'].append(input_example)
    test_dataloader = PromptDataLoader(dataset=dataset["test"], template=promptTemplate, tokenizer=tokenizer,
                                       tokenizer_wrapper_class=WrapperClass, max_seq_length=512, decoder_max_length=20,
                                       batch_size=5, shuffle=False, teacher_forcing=False, predict_eos_token=True,
                                       truncate_method="head")



    for step, inputs in enumerate(test_dataloader):
        inputs = inputs.cuda()
        _, output_sentence = model.generate(inputs, **generation_arguments)
        print(output_sentence)