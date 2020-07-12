#!/usr/bin/env python

import sys
import random

random.seed()
print(f'\n{"Heads" if random.randint(0, 1) else "Tails"}')