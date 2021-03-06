#!/usr/bin/env python

import sys

def conv(number, fmt='n'):
	number = str(number)
	try:
		num, dec = number.split('.')
	except ValueError:
		num = number
		dec = ''
	num = ''.join(num.split(','))
	try:
		_ = str(int(num))
		if dec != '':
			_ = str(int(dec))
	except ValueError:
		print(f'Invalid number: {number}', file=sys.stderr)
		exit(1)

	if fmt == 'n':
		return f'{num}.{dec}'

	if fmt == 'w':
		num = f'{int(num):,}.{dec}'
	elif fmt == 'i':
		_num = num[::-1]
		_num = [_num[:3]]+[_num[3:][i:i+2] for i in range(0, len(_num)-3, 2)]
		_num = ','.join(_num)
		num = f'{_num[::-1]}.{dec}'
	return num

def parseargs():
	if len(sys.argv) == 1:
		print('Missing arguments.', file=sys.stderr)
		exit()

	if len(sys.argv) == 3:
		if sys.argv[1] != '-i' and sys.argv[1] != '-w':
			print(f'Invalid flag: {sys.argv[1]}', file=sys.stderr)
			exit()
		fmt = sys.argv[1][-1]
		number = sys.argv[2]
	else:
		fmt = 'i'
		number = sys.argv[1]
	return number, fmt

if __name__ == '__main__':
	number, fmt = parseargs()
	num = conv(number, fmt)
	print(num)