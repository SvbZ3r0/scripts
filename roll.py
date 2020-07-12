#!/usr/bin/env python

import sys
import random

random.seed()

def parse_args():
	if len(sys.argv) > 2:
		print('Invalid command.\n')
		exit(1)
	if len(sys.argv) == 1:
		return 6
	else:
		return int(sys.argv[1])

def roll(n):
	return random.randint(1, n)

if __name__ == '__main__':
	print(f'\n{roll(parse_args())}')
