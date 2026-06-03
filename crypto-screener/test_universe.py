import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from universe_builder import build_universe

coins = build_universe()

print("Jumlah Coin:", len(coins))

for coin in coins[:20]:
    print(coin)