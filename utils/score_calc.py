import sys

with open(sys.argv[1]) as f:
    lines = f.readlines()
    times = []
    prices = []
    score = 0
    for line in lines:
        clean_line = line.strip()
        if clean_line.startswith("#") or clean_line == "":
            continue
        elif clean_line.startswith("STORE_VISITED"):
            s = float(clean_line.split(" ")[2])
            times.append(s)
            score = 50*len(prices) - sum(prices) - sum(times)
            print(clean_line, "->", score)
        elif clean_line.startswith("ITEM_BOUGHT"):
            s = float(clean_line.split(" ")[2])
            prices.append(s)            
            score = 50*len(prices) - sum(prices) - sum(times)
            print(clean_line,"->", score)
    
    print(score)
