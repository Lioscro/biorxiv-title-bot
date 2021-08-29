.PHONY : fetch train generate

PYTHON=python

fetch:
	$(PYTHON) scripts/fetch.py data 0.5

combine: data/_*.json
	$(PYTHON) scripts/combine.py data

prepare: data/papers.json
	$(PYTHON) scripts/prepare.py data/papers.json data 0.9

train:
	$(PYTHON) scripts/train.py --model_type gpt2 --model_name_or_path gpt2 \
		--train_file data/train.txt --do_train \
		--validation_file data/eval.txt --do_eval \
		--per_device_train_batch_size 1 \
		--save_steps -1 --output_dir model

download:
	mkdir -p model
	wget $(MODEL_URL) -qO- | tar -xvzf - -C model

generate:
	$(PYTHON) scripts/generate.py data model
