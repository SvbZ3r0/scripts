import sys
import random

random.seed()
print(f'\n{"Heads" if random.randint(0, 2) else "Tails"}')