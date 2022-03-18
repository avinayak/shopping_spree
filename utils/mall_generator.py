import json
import random
import uuid
from random import sample, random, randint

"""
This script generates a random mall with 4 configrable parameters:
- number of shops
- minimum number of shops that can be travelled from one shop
- maximum time taken between shops
- max price of a product
"""

N_SHOPS = 11
MIN_DEGREE = 2
MAX_TIME = 100
MAX_PRICE = 100

if __name__ == "__main__":
    mall = []
    for i in range(N_SHOPS):
        shop = {"storeID": i}
        possible_shops = list(range(N_SHOPS))
        possible_shops.remove(i)
        possible_shops_sample = sample(
            possible_shops, randint(MIN_DEGREE, N_SHOPS-1))

        shop["inventory"] = [{"itemID": str(uuid.uuid4()), "price": round(random(
        )*MAX_PRICE, 2)} for _ in range(randint(1, 10))]
        shop["inStoreAdvertisements"] = [{"storeID": j, "timeToGetToStore": round(random(
        )*MAX_TIME, 2)} for j in possible_shops_sample]
        mall.append(shop)

    print(json.dumps(mall))
