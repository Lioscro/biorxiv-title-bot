import glob
import json
import os

from sklearn.model_selection import train_test_split
from tqdm import tqdm

def clean_category(category):
    return category.lower().strip().strip('.').replace(' ', '_') or 'uncategorized'

def format_titles(papers):
    titles = []
    categories = set()
    for doi, paper in papers.items():
        category = clean_category(paper['category'])
        categories.add(category)
        titles.append(f'<|title|><|{category}|>{paper["title"]}')
    return titles, categories


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('out_dir')
    parser.add_argument('split', type=float)
    args = parser.parse_args()
    path = args.path
    out_dir = args.out_dir
    split = args.split

    with open(path, 'r') as f:
        papers = json.load(f)
    titles, categories = format_titles(papers)

    train_set, eval_set = train_test_split(titles, train_size=split)
    print(f'train: {len(train_set)}')
    print(f'eval: {len(eval_set)}')

    with open(os.path.join(out_dir, 'train.txt'), 'w') as f:
        f.write('<|endoftext|>'.join(train_set))
    with open(os.path.join(out_dir, 'eval.txt'), 'w') as f:
        f.write('<|endoftext|>'.join(eval_set))
    with open(os.path.join(out_dir, 'categories.txt'), 'w') as f:
        for category in categories:
            f.write(f'{category}\n')
