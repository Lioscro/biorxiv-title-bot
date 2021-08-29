import os

from transformers import GPT2Tokenizer, GPT2LMHeadModel

def generate(model, tokenizer, category=None, seed=None):
    input = '<|title|>'
    if category:
        input += f'<|{category}|>'
    if seed:
        input += seed
    input_ids = tokenizer.encode(input, return_tensors='pt')
    samples = model.generate(
        input_ids,
        max_length=200,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        repetition_penalty=1.5,
        top_p=0.9,
        temperature=0.85,
        do_sample=True,
        top_k=125,
        early_stopping=True,
    )
    return tokenizer.decode(samples[0], skip_special_tokens=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('model_dir')
    parser.add_argument('-c')
    parser.add_argument('-s')
    args = parser.parse_args()
    data_dir = args.data_dir
    model_dir = args.model_dir
    category = args.c
    seed = args.s

    with open(os.path.join(data_dir, 'categories.txt'), 'r') as f:
        categories = [line.strip() for line in f if not line.isspace()]
    if category and category not in categories:
        raise Exception(f'Unknown category: {category}')

    model = GPT2LMHeadModel.from_pretrained(model_dir)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    print(generate(model, tokenizer, category, seed))
