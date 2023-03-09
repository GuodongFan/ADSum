
from __future__ import absolute_import
import os
import time

import torch
import random
import logging
import argparse
import numpy as np
from io import open

from openprompt import PromptDataLoader, PromptForGeneration
from openprompt.plms import T5TokenizerWrapper
from openprompt.prompts import PrefixTuningTemplate,SoftTemplate
from tqdm import tqdm
from transformers import (AdamW, get_linear_schedule_with_warmup,
						  RobertaConfig, RobertaModel, RobertaTokenizer, T5Config, T5ForConditionalGeneration, T5Tokenizer)

import bleu
from my_lib import read_prompt_examples, get_elapse_time, read_prompt_examples_pd

MODEL_CLASSES = {'roberta': (RobertaConfig, RobertaModel, RobertaTokenizer)}
#MODEL_CLASSES_ = {'t5': (T5Config, T5Tokenizer)}


def set_seed(seed=42):
	random.seed(seed)
	os.environ['PYTHONHASHSEED'] = str(seed)
	np.random.seed(seed)
	torch.manual_seed(seed)
	torch.cuda.manual_seed(seed)
	torch.backends.cudnn.deterministic = True


def read_arguments():
	parser = argparse.ArgumentParser()

	# outdated parameters
	parser.add_argument("--model_type", default=None, type=str, required=False,
						help="Model type: e.g. roberta")
	parser.add_argument("--model_name_or_path", default=None, type=str, required=False,
						help="Path to pre-trained model: e.g. roberta-base")

	# Required parameters
	parser.add_argument("--log_name", default=None, type=str, required=True)

	parser.add_argument("--output_dir", default="./RQ2/model_github_pt", type=str, required=False,
						help="The output directory where the model predictions and checkpoints will be written.")

	parser.add_argument("--data_dir", default="./data", type=str,
						help="Path to the dir which contains processed data for some languages")

	parser.add_argument("--lang", default=None, type=str, required=True,
						help="language to summarize")

	parser.add_argument("--no_cuda", default=False, action='store_true',
						help="Avoid using CUDA when available")
	parser.add_argument('--visible_gpu', type=str, default="",
						help="use how many gpus")

	parser.add_argument("--add_task_prefix", default=False, action='store_true',
						help="Whether to add task prefix for T5 and codeT5")
	parser.add_argument("--add_lang_ids", default=False, action='store_true',
						help="Whether to add language prefix for T5 and codeT5")

	parser.add_argument("--num_train_epochs", default=20, type=int,
						help="Total number of training epochs to perform.")

	parser.add_argument("--train_batch_size", default=32, type=int,
						help="Batch size per GPU/CPU for training.")
	parser.add_argument("--eval_batch_size", default=32, type=int,
						help="Batch size per GPU/CPU for evaluation.")
	parser.add_argument('--gradient_accumulation_steps', type=int, default=2,
						help="Number of updates steps to accumulate before performing a backward/update pass.")

	# other arguments
	parser.add_argument("--load_model_path", default=None, type=str,
						help="Path to trained model: Should contain the .bin files")
	parser.add_argument("--config_name", default="", type=str,
						help="Pretrained config name or path if not the same as model_name")
	parser.add_argument("--tokenizer_name", default="", type=str,
						help="Pretrained tokenizer name or path if not the same as model_name")
	parser.add_argument("--max_source_length", default=64, type=int,
						help="The maximum total source sequence length after tokenization. Sequences longer "
							 "than this will be truncated, sequences shorter will be padded.")
	parser.add_argument("--max_target_length", default=32, type=int,
						help="The maximum total target sequence length after tokenization. Sequences longer "
							 "than this will be truncated, sequences shorter will be padded.")
	parser.add_argument("--warm_up_ratio", default=0.1, type=float)

	# controlling arguments
	parser.add_argument("--do_train", action='store_true',
						help="Whether to run training.")
	parser.add_argument("--do_eval", action='store_true',
						help="Whether to run eval on the dev set.")
	parser.add_argument("--do_test", action='store_true',
						help="Whether to run eval on the dev set.")

	parser.add_argument("--do_lower_case", action='store_true',
						help="Set this flag if you are using an uncased model.")

	parser.add_argument("--learning_rate", default=5e-5, type=float,
						help="The initial learning rate for Adam.")
	parser.add_argument("--beam_size", default=10, type=int,
						help="beam size for beam search")
	parser.add_argument("--weight_decay", default=0.0, type=float,
						help="Weight decay if we apply some.")
	parser.add_argument("--adam_epsilon", default=1e-8, type=float,
						help="Epsilon for Adam optimizer.")
	parser.add_argument("--max_grad_norm", default=1.0, type=float,
						help="Max gradient norm.")
	parser.add_argument("--max_steps", default=-1, type=int,
						help="If > 0: set total number of training steps to perform. Override num_train_epochs.")
	parser.add_argument("--eval_steps", default=-1, type=int,
						help="")
	parser.add_argument("--train_steps", default=-1, type=int,
						help="")
	parser.add_argument("--local_rank", type=int, default=-1,
						help="For distributed training: local_rank")
	parser.add_argument('--seed', type=int, default=42,
						help="random seed for initialization")
	parser.add_argument('--early_stop_threshold', type=int, default=10)

	# print arguments
	args = parser.parse_args()

	return args


def main(args):
	set_seed(args.seed)

	train_num_sample = 10
	num_tokens = 50

	# data path
	train_filename = args.data_dir + "/" + "/github/train.csv"	# train
	dev_filename = args.data_dir + "/" + "/github/valid.csv"	# valid
	test_filename = args.data_dir + "/" + "/github/test.csv"	# test

	# Setup CUDA, GPU & distributed training
	os.environ["CUDA_VISIBLE_DEVICES"] = args.visible_gpu

	if args.local_rank == -1 or args.no_cuda:
		device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
		args.n_gpu = torch.cuda.device_count()
	# Initializes the distributed backend which will take care of synchronizing nodes/GPUs
	else:
		torch.cuda.set_device(args.local_rank)
		device = torch.device("cuda", args.local_rank)
		torch.distributed.init_process_group(backend='nccl')
		args.n_gpu = 1

	logger.warning("Process rank: %s, device: %s, n_gpu: %s, distributed training: %s",
				   args.local_rank, device, args.n_gpu, bool(args.local_rank != -1))

	args.device = device

	# make dir if output_dir not exist
	file_path = args.output_dir + '_sample_' + str(train_num_sample) + '_tokens_' + str(num_tokens)
	if os.path.exists(file_path) is False:
		os.makedirs(file_path)
	args.output_dir = file_path
	print(args.output_dir)

	# *********************************************************************************************************

	# read model --------------------------------------------------------------
	model_config = T5Config.from_pretrained("t5-base")
	#plm = T5ForConditionalGeneration.from_pretrained("./model/checkpoint-best-bleu/", config=model_config)
	plm = T5ForConditionalGeneration.from_pretrained("t5-base", config=model_config)
	tokenizer = T5Tokenizer.from_pretrained("t5-base")
	WrapperClass = T5TokenizerWrapper

	# define template
	promptTemplate = SoftTemplate(model=plm, tokenizer=tokenizer,
										  text='Text: {"placeholder":"text_a"} Summarization: {"mask"} ', initialize_from_vocab=True,
										   num_tokens=num_tokens)

	# get model
	model = PromptForGeneration(plm=plm, template=promptTemplate, freeze_plm=False, tokenizer=tokenizer,
									   plm_eval_mode=False)
	model.to(device)

	if args.load_model_path is not None:
		# load best checkpoint for best bleu
		output_dir = os.path.join(args.output_dir, 'checkpoint-best-bleu')
		if not os.path.exists(output_dir):
			raise Exception("Best bleu model does not exist!")

		model.load_state_dict(torch.load(os.path.join(output_dir, "pytorch_model.bin")))
		logger.info("reload model from {}".format(args.load_model_path))

	# parallel or distribute setting
	if args.local_rank != -1:
		# Distributed training
		try:
			# from apex.parallel import DistributedDataParallel as DDP
			from torch.nn.parallel import DistributedDataParallel as DDP
		except ImportError:
			raise ImportError(
				"Please install apex from https://www.github.com/nvidia/apex to use distributed and fp16 training.")

		model = DDP(model)
	elif args.n_gpu > 1:
		# multi-gpu training
		model = torch.nn.DataParallel(model)

	logger.info("Model created!!")

	# train part --------------------------------------------------------------
	if args.do_train:
		# Prepare training data loader
		train_examples = read_prompt_examples_pd(train_filename)

		# take an example
		wrapped_example = promptTemplate.wrap_one_example(train_examples[0])
		logger.info(wrapped_example)
		random.seed(1024)
		sample_num = train_num_sample
		train_examples = random.sample(train_examples, min(sample_num, len(train_examples)))
		print(len(train_examples))

		train_data_loader = PromptDataLoader(
			dataset=train_examples,
			tokenizer=tokenizer,
			template=promptTemplate,
			tokenizer_wrapper_class=WrapperClass,
			max_seq_length=args.max_source_length,
			decoder_max_length=args.max_target_length,
			shuffle=True,
			teacher_forcing=True,
			predict_eos_token=True,
			batch_size=args.train_batch_size
		)

		# Prepare optimizer and schedule (linear warmup and decay)
		no_decay = ['bias', 'LayerNorm.weight']
		optimizer_grouped_parameters = [
			{'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
			 'weight_decay': args.weight_decay},
			{'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
		]
		t_total = (len(train_data_loader) // args.gradient_accumulation_steps) * args.num_train_epochs
		optimizer = AdamW(optimizer_grouped_parameters, lr=args.learning_rate, eps=args.adam_epsilon)
		scheduler = get_linear_schedule_with_warmup(optimizer,
													num_warmup_steps=int(t_total * args.warm_up_ratio),
													num_training_steps=t_total)

		# Start training
		logger.info("***** Running training *****")
		logger.info("  Num examples = %d", len(train_examples))
		logger.info("  Batch size = %d", args.train_batch_size)
		logger.info("  Num epoch = %d", args.num_train_epochs)

		# used to save tokenized development data
		nb_tr_examples, nb_tr_steps, global_step, best_bleu, best_loss = 0, 0, 0, 0, 1e6
		early_stop_threshold = args.early_stop_threshold

		eval_dataloader = None
		dev_dataloader = None

		early_stop_count = 0
		for epoch in range(args.num_train_epochs):

			model.train()
			tr_loss = 0.0
			train_loss = 0.0

			# progress bar
			bar = tqdm(train_data_loader, total=len(train_data_loader))

			for batch in bar:
				batch = batch.to(device)

				loss = model(batch)

				if args.n_gpu > 1:
					loss = loss.mean()  # mean() to average on multi-gpu.
				if args.gradient_accumulation_steps > 1:
					loss = loss / args.gradient_accumulation_steps

				tr_loss += loss.item()
				train_loss = round(tr_loss * args.gradient_accumulation_steps / (nb_tr_steps + 1), 4)
				bar.set_description("epoch {} loss {}".format(epoch, train_loss))

				nb_tr_steps += 1
				loss.backward()

				if nb_tr_steps % args.gradient_accumulation_steps == 0:
					# Update parameters
					optimizer.step()
					optimizer.zero_grad()
					scheduler.step()
					global_step += 1

			# to help early stop
			this_epoch_best = False

			if args.do_eval:
				# Eval model with dev dataset
				nb_tr_examples, nb_tr_steps = 0, 0

				if eval_dataloader is None:
					# Prepare training data loader
					eval_examples = read_prompt_examples_pd(dev_filename)

					eval_dataloader = PromptDataLoader(
						dataset=eval_examples,
						tokenizer=tokenizer,
						template=promptTemplate,
						tokenizer_wrapper_class=WrapperClass,
						max_seq_length=args.max_source_length,
						decoder_max_length=args.max_target_length,
						shuffle=False,
						teacher_forcing=False,
						predict_eos_token=True,
						batch_size=args.eval_batch_size
					)
				else:
					pass

				logger.info("\n***** Running evaluation *****")
				logger.info("  Num examples = %d", len(eval_dataloader) * args.eval_batch_size)
				logger.info("  Batch size = %d", args.eval_batch_size)

				# Start Evaluating model
				model.eval()
				eval_loss = 0

				for batch in eval_dataloader:
					batch = batch.to(device)

					with torch.no_grad():
						loss = model(batch)

					eval_loss += loss.sum().item()

				# print loss of dev dataset
				print(eval_loss)
				result = {'epoch': epoch,
						  'eval_ppl': round(np.exp(eval_loss), 5),
						  'global_step': global_step + 1,
						  'train_loss': round(train_loss, 5)}

				for key in sorted(result.keys()):
					logger.info("  %s = %s", key, str(result[key]))
				logger.info("  " + "*" * 20)

				# save last checkpoint
				last_output_dir = os.path.join(args.output_dir, 'checkpoint-last')
				if not os.path.exists(last_output_dir):
					os.makedirs(last_output_dir)

				# Only save the model it-self
				model_to_save = model.module if hasattr(model, 'module') else model

				output_model_file = os.path.join(last_output_dir, "pytorch_model.bin")
				torch.save(model_to_save.state_dict(), output_model_file)

				logger.info("Previous best ppl:%s", round(np.exp(best_loss), 5))

				# save best checkpoint
				if eval_loss < best_loss:
					this_epoch_best = True

					logger.info("Achieve Best ppl:%s", round(np.exp(eval_loss), 5))
					logger.info("  " + "*" * 20)
					best_loss = eval_loss
					# Save best checkpoint for best ppl
					output_dir = os.path.join(args.output_dir, 'checkpoint-best-ppl')
					if not os.path.exists(output_dir):
						os.makedirs(output_dir)
					output_model_file = os.path.join(output_dir, "pytorch_model.bin")
					torch.save(model_to_save.state_dict(), output_model_file)

				# Calculate bleu
				this_bleu, dev_dataloader = calculate_bleu(dev_filename, args, tokenizer, device, model, promptTemplate, WrapperClass, is_test=False, dev_dataloader=dev_dataloader, best_bleu=best_bleu)

				if this_bleu > best_bleu:
					this_epoch_best = True

					logger.info(" Achieve Best bleu:%s", this_bleu)
					logger.info("  " + "*" * 20)
					best_bleu = this_bleu
					# Save best checkpoint for best bleu
					output_dir = os.path.join(args.output_dir, 'checkpoint-best-bleu')
					if not os.path.exists(output_dir):
						os.makedirs(output_dir)
					model_to_save = model.module if hasattr(model, 'module') else model  # Only save the model it-self
					output_model_file = os.path.join(output_dir, "pytorch_model.bin")
					torch.save(model_to_save.state_dict(), output_model_file)

			# whether to stop
			if this_epoch_best:
				early_stop_count = 0
			else:
				early_stop_count += 1
				if early_stop_count == early_stop_threshold:
					logger.info("early stopping!!!")
					break

	# use dev file and test file ( if exist) to calculate bleu
	if args.do_test:
		# read model
		output_dir = os.path.join(args.output_dir, 'checkpoint-best-bleu')
		if not os.path.exists(output_dir):
			raise Exception("Best bleu model does not exist!")

		model.load_state_dict(torch.load(os.path.join(output_dir, "pytorch_model.bin")))
		logger.info("reload model from {}".format(args.load_model_path))
		model.eval()

		files = []
		if dev_filename is not None:
			files.append(dev_filename)
		if test_filename is not None:
			files.append(test_filename)

		for idx, file in enumerate(files):
			calculate_bleu(file, args, tokenizer, device, model, promptTemplate, WrapperClass, output_file_name=str(idx), is_test=True)


def calculate_bleu(file_name, args, tokenizer, device, model, promptTemplate, WrapperClass, output_file_name=None, is_test=False, dev_dataloader=None,
				   best_bleu=None):
	logger.info("BLEU file: {}".format(file_name))

	# whether append postfix to result file
	if output_file_name is not None:
		output_file_name = "_" + output_file_name
	else:
		output_file_name = ""

	if is_test:
		file_prefix = "test"
	else:
		file_prefix = "dev"

	# if dev dataset has been saved
	if (not is_test) and (dev_dataloader is not None):
		eval_dataloader = dev_dataloader
	else:
		# read texts
		eval_examples = read_prompt_examples_pd(file_name)

		# only use a part for dev
		if not is_test:
			eval_examples = random.sample(eval_examples, min(2000, len(eval_examples)))

		eval_dataloader = PromptDataLoader(
			dataset=eval_examples,
			tokenizer=tokenizer,
			template=promptTemplate,
			tokenizer_wrapper_class=WrapperClass,
			max_seq_length=args.max_source_length,
			decoder_max_length=args.max_target_length,
			shuffle=False,
			teacher_forcing=False,
			predict_eos_token=True,
			batch_size=args.eval_batch_size
		)

	model.eval()

	# generate texts by source
	generated_texts = []
	groundtruth_sentence = []
	guids = []
	for batch in tqdm(eval_dataloader, total=len(eval_dataloader)):
		batch = batch.to(device)
		with torch.no_grad():
			_, output_sentence = model.generate(batch)

			generated_texts.extend(output_sentence)
			groundtruth_sentence.extend(batch['tgt_text'])
			guids.extend(batch['guid'])

	# write to file
	predictions = []

	with open(os.path.join(args.output_dir, file_prefix + "{}.output".format(output_file_name)), 'w') as f, open(
			os.path.join(args.output_dir, file_prefix + "{}.gold".format(output_file_name)), 'w') as f1:

		for ref, gold, idx in zip(generated_texts, groundtruth_sentence, guids):
			predictions.append(str(idx) + '\t' + ref)
			#f.write(ref + '\n')
			#f1.write(gold + '\n')
			f.write(str(idx) + '\t' + ref + '\n')
			f1.write(str(idx) + '\t' + gold + '\n')

	# compute bleu
	(goldMap, predictionMap) = bleu.computeMaps(predictions,
												os.path.join(args.output_dir, file_prefix + "{}.gold".format(output_file_name)))
	this_bleu = round(bleu.bleuFromMaps(goldMap, predictionMap)[0], 2)

	if is_test:
		logger.info("  %s = %s " % ("bleu-4", str(this_bleu)))
	else:
		logger.info("  %s = %s \t Previous best bleu %s" % ("bleu-4", str(this_bleu), str(best_bleu)))

	logger.info("  " + "*" * 20)

	return this_bleu, eval_dataloader


if __name__ == "__main__":
	my_args = read_arguments()

	# begin time
	begin_time = time.time()

	# logger for record
	logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
						datefmt='%m/%d/%Y %H:%M:%S',
						level=logging.INFO)
	logger = logging.getLogger(__name__)

	# write to file
	handler = logging.FileHandler(my_args.log_name)
	handler.setLevel(logging.INFO)
	logger.addHandler(handler)

	# write to console
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	logger.addHandler(console)

	# print args
	logger.info(my_args)

	main(my_args)

	logger.info("Finish training and take %s", get_elapse_time(begin_time))


