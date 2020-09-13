#!/usr/bin/env python

import sys

def conv(number, fmt):
	num = ''.join(number.split(','))

	try:
		if '.' in num:
			num = float(num)
		else:
			num = int(num)
	except ValueError:
		print(f'Invalid number: {number}')
		exit()

	if fmt == 'w':
		num = f'{num:,}'
	else:
		if type(num) == float:	# isinstance(num, float)
			num, dec = str(num).split('.')
			dec = '.' + dec
		else:
			num = str(num)
			dec = ''
		_num = num[::-1]
		_num = [_num[:3]]+[_num[3:][i:i+2] for i in range(0, len(_num)-3, 2)]
		_num = ','.join(_num)
		num = _num[::-1] + dec

	return num

def parseargs():
	if len(sys.argv) == 1:
		print('Missing arguments.')
		exit()

	if len(sys.argv) == 3:
		if sys.argv[1] != '-i' and sys.argv[1] != '-w':
			print(f'Invalid flag: {sys.argv[1]}')
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