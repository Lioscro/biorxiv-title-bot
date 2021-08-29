import json
import os
import time

import requests
from tqdm import tqdm

URL = 'https://api.biorxiv.org/details/biorxiv/2000-01-01/3000-01-01'

def fetch(cursor=0):
    response = requests.get(f'{URL}/{cursor}')
    response.raise_for_status()
    decoded = response.json()
    total = decoded['messages'][0]['total']
    return total, decoded['collection']

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('out_dir')
    parser.add_argument('interval', type=float)
    args = parser.parse_args()
    out_dir = args.out_dir
    interval = args.interval

    cursor = 0
    total = fetch()[0]
    pbar = tqdm(total=total)
    while cursor < total:
        path = os.path.join(out_dir, f'_{str(cursor).zfill(len(str(total)))}.json')
        exists = False
        try:
            with open(path, 'r') as f:
                json.load(f)
            exists = True
        except:
            pass

        if not exists:
            total, collection = fetch(cursor)
            pbar.total = total
            with open(path, 'w') as f:
                json.dump(collection, f)
            time.sleep(interval)
        cursor += 100
        pbar.update(100)
        pbar.refresh()
    pbar.close()
