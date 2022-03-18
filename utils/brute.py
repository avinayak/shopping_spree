from itertools import chain, combinations
from itertools import permutations

import numpy as np
import json
from joblib import Parallel, delayed

""" Parallel brute force solver for solving mall problem of smaller varitey.
    This file is not for evaluvation.
"""


data = []
with open("data/mall_test.json") as f:
    data = json.load(f)

n_shops = len(data)

dist_mat = np.ones((n_shops, n_shops)) * np.inf
np.fill_diagonal(dist_mat, 0)

for i in range(n_shops):
    for j in range(n_shops):
        if i != j:
            for k in data[i]['inStoreAdvertisements']:
                if k['storeID'] == j:
                    dist_mat[i, j] = k['timeToGetToStore']


def get_items_scores():
    ss = []
    shop_good_items = []
    for i in range(n_shops):
        good_items = [item for item in data[i]
                      ['inventory'] if item["price"] < 50]
        prices = [item["price"] for item in good_items]
        score = len(prices)*50 - sum(prices)
        ss.append(score)
        shop_good_items.append(good_items)
    return (ss, shop_good_items)


ss, shop_good_items = get_items_scores()


def genout(good_path, shop_good_items):
    path_pairs = [(good_path[i], good_path[i+1])
                  for i in range(len(good_path)-1)]

    outstr = f"STORE_VISITED {good_path[0]} 0\n"
    for it in shop_good_items[good_path[0]]:
        outstr += f"ITEM_BOUGHT {it['itemID']} {it['price']}\n"

    for i, j in path_pairs:
        outstr += f"STORE_VISITED {j} {dist_mat[i,j]}\n"
        for it in shop_good_items[j]:
            outstr += f"ITEM_BOUGHT {it['itemID']} {it['price']}\n"
    with open('brute_out.txt', 'w') as f:
        f.write(outstr)


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


max_score = 0
max_path = 0


def brute(p):
    scoresum = ss[p[0]]
    for s, e in [[p[i], p[i+1]] for i in range(len(p)-1)]:
        if dist_mat[s, e] != np.inf:
            scoresum += ss[e] - dist_mat[s, e]
        else:
            return (0, p)
    return (scoresum, p)


for g in powerset(range(n_shops)):
    if len(g) > 1:
        results = Parallel(n_jobs=8)(delayed(brute)(p)
                                     for p in permutations(g))
        score, bpath = max(results, key=lambda x: x[0])
        if max_score < score:
            max_score = score
            max_path = bpath
            print(max_score, max_path)
            genout(max_path, shop_good_items)
