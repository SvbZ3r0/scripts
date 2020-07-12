#!/usr/bin/env python

import os
import sys
import json
import argparse
import datetime
import requests
from pathlib import Path

try:
	from number_format import conv
except ImportError:
	def conv(num, fmt):
		return num

with open(os.path.join(os.path.dirname(sys.argv[0]), 'data', 'curx.conf')) as f:
	conf = json.load(f)
APP_KEY = conf['APP_KEY']
URL = 'https://openexchangerates.org/api/{0}?app_id={1}&base=USD&show_alternative=true&prettyprint=false'.format('{0}', APP_KEY)
cache_file = os.path.join(os.path.dirname(sys.argv[0]), 'data', 'rates.json')
rates = dict()

def curx_man():
	# TODO
	exit(0)

def parse_args():
	if len(sys.argv) == 1: curx_man()
	elif len(sys.argv) != 4:
		if len(sys.argv) == 3: sys.argv += ['inr']
		else:
			print(f'Invalid command. \nUsage: {os.path.basename(sys.argv[0])} <value> <from> <to>')
			exit(1)
	try:
		val = float(sys.argv[1])
	except ValueError:
		print(f'Invalid value: {sys.argv[1]}')
	try:
		from_curr = sys.argv[2].upper()
	except AttributeError:
		print(f'Invalid currency: {sys.argv[2]}')
	try:
		to_curr = sys.argv[3].upper()
	except AttributeError:
		print(f'Invalid currency: {sys.argv[3]}')
	return from_curr, to_curr, val

def create_cache():
	url = URL.format('currencies.json')
	try:
		r = requests.get(url)
		r.raise_for_status()
	except:
		# TODO
		pass
	print(r.text)
	currencies = json.loads(r.text)
	tmp = dict()
	# tmp['date'] = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
	tmp['date'] = r.headers['Last-Modified']
	# format '%a, %d %b %Y %H:%M:%S %Z'
	tmp['base'] = 'USD'
	tmp['rates'] = dict()
	for k,v in currencies.items():
		tmp['rates'][k] = {'name': v}
		# tmp['rates'][k]['name'] = v
	tmp['etag'] = r.headers['Etag']
	url = URL.format('latest.json')
	try:
		r = requests.get(url)
		r.raise_for_status()
	except:
		# TODO
		pass
	rates = json.loads(r.text)['rates']
	for k,v in currencies.items():
		tmp['rates'][k]['rate'] = rates[k]
	try:
		with open(cache_file, 'w', encoding='utf-8') as cache:
			json.dump(tmp, cache, indent=4)
	except IOError:
		print('Unable to cache results.\n')
		# exit(1)
		pass
	return tmp

def get_rate_current(overwrite = False):
	url = URL.format('latest.json')
	with open(cache_file, 'r', encoding='utf-8') as cache:
		rates = json.load(cache, encoding='utf-8')
	try:
		r = requests.get(url)
		r.raise_for_status()
	except ConnectionError:
		print('Unable to update exchange rates.')
		return rates
		exit(1)
	except:
		# TODO change this
		print('Unable to update exchange rates.')
		return rates
		exit(1)
	rates['date'] = r.headers['Last-Modified']
	_rates = r.json()
	rates['base'] = _rates['base']
	_rates = _rates['rates']
	# TODO add functionality for help option
	for k,v in _rates.items():
		rates['rates'][k]['rate'] = v
	try:
		with open(cache_file, 'w', encoding='utf-8') as cache:
			json.dump(rates, cache, indent=4)
	except IOError:
		print('Unable to cache results.\n')
		pass
	return rates

def get_rates_cache():
	try:
		with open(cache_file, 'r', encoding='utf-8') as cache:
			rates = json.load(cache, encoding='utf-8')
	except FileNotFoundError:
		return create_cache()
	time_since_last_update = datetime.datetime.today() - datetime.datetime.strptime(rates['date'], '%a, %d %b %Y %H:%M:%S %Z')
	if time_since_last_update > datetime.timedelta(days=1):
		print('Updating rates')
		return get_rate_current()
	return rates

def convert(rates, from_curr, to_curr, val):
	rate = 0
	if from_curr == rates['base']:
		rate = rates['rates'][to_curr]['rate']
	elif from_curr not in rates['rates']:
		print(f'Unknown currency: {from_curr}')
		exit(1)
	if to_curr == rates['base']:
		rate = 1 / rates['rates'][from_curr]['rate']
	elif to_curr not in rates['rates']:
		print(f'Unknown currency: {to_curr}')
		exit(1)
	if not rate:
		rate = rates['rates'][to_curr]['rate'] / rates['rates'][from_curr]['rate']
	conv_rate = val * rate
	conv_rate = f'{conv_rate:.2f}'
	fmt = 'i' if to_curr == 'INR' else 'w'
	conv_rate = conv(conv_rate, fmt)
	if 'symbol' in rates['rates'][to_curr].keys():
		conv_rate = rates['rates'][to_curr]['symbol'] + ' ' + conv_rate
	return conv_rate

if __name__ == '__main__':
	# create 'data' folder if it doesn't already exist
	Path(os.path.dirname(cache_file)).mkdir(parents=True, exist_ok=True)
	args = parse_args()
	converted = convert(get_rates_cache(), *args)
	print(converted)
	# print(f'{converted:.2f}')
