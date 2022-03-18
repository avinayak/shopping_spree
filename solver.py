import numpy as np
import json
import argparse
import logging

"""
Solves ShoppingSpree problem with a modified version of dijkstra's algorithm.
Basically, find the optimal path that maximizes score:
- score = number of items bought * 50 - sum of prices - time spent between shops
"""


def load_mall(filename: str):
    """ Loads the mall from the given file."""
    mall = []
    with open(filename) as f:
        mall = json.load(f)
    return mall, len(mall)


def gnerate_adjacency_matrix(mall, n_shops):
    """ Generates the adjacency matrix for a mall."""
    mall_adj_mat = np.ones((n_shops, n_shops)) * np.inf
    np.fill_diagonal(mall_adj_mat, 0)
    for i in range(n_shops):
        for j in range(n_shops):
            if i != j:
                for k in mall[i]['inStoreAdvertisements']:
                    if k['storeID'] == j:
                        mall_adj_mat[i, j] = k['timeToGetToStore']
    return mall_adj_mat


def get_maximal_items(mall):
    """ We want to maximize the score of the optimal path.
        The best startegy in regards to shopping is to simply buy everything that costs < 50.
        This ensure that (number of items bought * 50 - sum of prices) is maximized.
    """
    max_shop_score = []
    n_shops = len(mall)
    shopped_items = []
    for i in range(n_shops):
        good_items = [item for item in mall[i]
                      ['inventory'] if item["price"] < 50]
        prices = [item["price"] for item in good_items]
        score = len(prices)*50 - sum(prices)
        max_shop_score.append(score)
        shopped_items.append(good_items)
    return (max_shop_score, shopped_items)


def dijkstra(mall_adj_mat, start, max_shop_score):
    """
    dijkstra's algorithm(https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) 
    for finding the optimal path. This has been slightly modified 
    to include shop scores in path planning.

    Args:
        mall_adj_mat: the adjacency matrix of the mall
        start: start node for the dijkstra
        max_shop_score: maximal item scores for each shop

    Returns:
        dist: distance from start to each node
        prev: previous node in the optimal path
    """
    n_shops = len(mall_adj_mat)
    dist = np.full(n_shops, np.inf)
    prev = np.full(n_shops, -1)
    Q = list(range(n_shops))
    dist[start] = -max_shop_score[start]

    while Q:
        u = min(Q, key=lambda x: dist[x] - max_shop_score[x])
        Q.remove(u)
        for v in Q:
            if mall_adj_mat[u, v] != np.inf:
                alt = dist[u] + mall_adj_mat[u, v] - max_shop_score[v]
                if alt < dist[v] - max_shop_score[v]:
                    dist[v] = alt
                    prev[v] = u
    return dist, prev


def prev_to_path(prev, start, end):
    """ Unroll Djiikstra's prev array to find actual path."""
    path = [end]
    while path[-1] != start:
        path.append(prev[path[-1]])
    return path[::-1]


def dijkstra_runner(mall_adj_mat, max_shop_score, n_shops):
    """Runs Dijkstra's algorithm for all shops. In essence find all source optimal paths."""
    paths = {}
    for u in range(n_shops):
        dist, prev = dijkstra(mall_adj_mat, u, max_shop_score)
        for v in range(n_shops):
            if dist[u] != np.inf and u != v:
                paths[(u, v)] = prev_to_path(prev, u, v)
                score_mat[u, v] = -dist[v]
    return (score_mat, paths)


def generate_output(good_path, shop_good_items, mall_adj_mat):
    """Genenerates output readable by Sleek Team"""
    path_pairs = [(good_path[i], good_path[i+1])
                  for i in range(len(good_path)-1)]

    outstr = f"STORE_VISITED {good_path[0]} 0\n"
    for it in shop_good_items[good_path[0]]:
        outstr += f"ITEM_BOUGHT {it['itemID']} {it['price']}\n"

    for i, j in path_pairs:
        outstr += f"STORE_VISITED {j} {mall_adj_mat[i,j]}\n"
        for it in shop_good_items[j]:
            outstr += f"ITEM_BOUGHT {it['itemID']} {it['price']}\n"

    return outstr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Solves ShoppingSpree problem with a modified version of dijkstra's algorithm.")
    parser.add_argument("-f", "--file", type=str, required=True,
                        help="The file containing the mall.")
    parser.add_argument("-o", "--output", type=str,
                        required=True, help="The output file.")

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    logging.info('Loading mall file...')

    mall, n_shops = load_mall(args.file)
    mall_adj_mat = gnerate_adjacency_matrix(mall, n_shops)
    max_shop_score, shopped_items = get_maximal_items(mall)

    score_mat = np.full((n_shops, n_shops), 0)
    logging.info('Finding optimal paths...')
    score_mat, paths = dijkstra_runner(mall_adj_mat, max_shop_score, n_shops)

    optimal_score = score_mat.max()
    logging.info('Optimal score: %d', optimal_score)

    beg, end = np.where((score_mat == optimal_score))
    good_path = paths[(beg[0], end[0])]

    output = generate_output(good_path, shopped_items, mall_adj_mat)
    with open(args.output, 'w') as f:
        f.write(output)
