import glob
import json
import os

from tqdm import tqdm

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    args = parser.parse_args()
    out_dir = args.out_dir

    papers = {}
    for path in tqdm(sorted(glob.glob(os.path.join(out_dir, '_*.json')))):
        with open(path, 'r') as f:
            collection = json.load(f)
        for paper in collection:
            doi = paper['doi']
            if doi not in papers or (
                int(paper['version']) > int(papers[doi]['version'])
            ):
                papers[doi] = paper

    path = os.path.join(out_dir, 'papers.json')
    with open(path, 'w') as f:
        json.dump(papers, f)
