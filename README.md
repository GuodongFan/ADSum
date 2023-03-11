# Code For "Dialog Summarization for Software Collaborative Platform via Tuning Pre-trained Models"

## Ⅰ Preprocess

For Github data.

python ./preprocess/process_github_discussions.py

For Gitter data.

/disentangle/disentanglement/tools/preprocessing/

## Ⅱ Dialog Disentanglement 
Gitter dialogs Disentanglement (method 1)

```
python disentangle.py gitter
--train src/disentanglement/proposed_dataset/original_format/*/*.annotation.txt
--hidden 512
--layers 2
--nonlin softsign
--word-vectors src/disentanglement/data/glove-ubuntu.txt
--epochs 5
--dynet-autobatch
--drop 0
--learning-rate 0.018804
--learning-decay-rate 0.103
--seed 10
--clip 3.740
--weight-decay 1e-07
--opt sgd
--max-dist 51
```

```
python disentangle.py gitter
--model ./gitter.dy_9.model
--test ./data/gitter/ethereum/welcome/content.annotation.txt
--test-start 0
--hidden 512
--layers 2
--nonlin softsign
--word-vectors src/disentanglement/data/glove-ubuntu.txt
--max-dist 51
```

For GitterAnalysis (method 2)
```
csv_construct.py 
data_cleaning.py 
merge.tab.py 
thread_identification.py 
evaluation.py`
```

## Ⅲ Tuning Github

```
python github_finetune_t5_title.py \
--visible_gpu 1 \
--max_source_length 256 \
--max_target_length 20 \
--log_name log/log \
--do_train \
--do_eval \
--do_test \
--train_batch_size 10 \
--train_batch_size 10 \
--eval_batch_size 10 \
```

```
python github_prompt_t5_title.py \
--visible_gpu 1 \
--max_source_length 256 \
--max_target_length 20 \
--log_name log/log \
--do_train \
--do_eval \
--do_test \
--train_batch_size 10 \
--train_batch_size 10 \
--eval_batch_size 10 \
```

```
python github_finetune_gpt2_title.py \
--model_name_or_path gpt2 \
--model_name gpt2 \
--do_train \
--do_eval \
--do_predict \
--train_file data/github/train.csv \
--validation_file  data/github/valid.csv \
--test_file data/github/test.csv \
--source_prefix "summarize: " \
--output_dir ./output_dir \
--overwrite_output_dir \
--per_device_train_batch_size=10 \
--per_device_eval_batch_size=10 \
--predict_with_generate \
--eval_steps=50 \
--logging_steps=50 \
--num_train_epochs=20 \
--learning_rate=1e-4 \
--max_source_length=256 \
--generation_max_length=276 \
--text_column src \
--summary_column tgt \
--evaluation_strategy epoch \
--save_strategy epoch \
--load_best_model_at_end True \
```


## Ⅳ Tuning Gitter

```
python gitter_prompt_t5_title.py \
--visible_gpu 1 \
--max_source_length 256 \
--max_target_length 20 \
--log_name log/log \
--do_train \
--do_eval \
--do_test \
--train_batch_size 10 \
--train_batch_size 10 \
--eval_batch_size 10 \
```

```
python gitter_finetune_t5_title.py \
--visible_gpu 1 \
--max_source_length 256 \
--max_target_length 20 \
--log_name log/log \
--do_train \
--do_eval \
--do_test \
--train_batch_size 10 \
--train_batch_size 10 \
--eval_batch_size 10 \
```

## Ⅴ Calculate the metrics such as bleu rouge

`python eval.py`

## Ⅵ Annotation Tool

`/tools/dialog_GUI/view.py`

## VII Requirements
```
pytorch 1.12.0
openprompt 1.0.1
tokenizers 0.12.1
nltk 3.7
numpy 1.22.3
nlgeval
```