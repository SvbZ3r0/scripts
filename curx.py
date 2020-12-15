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
		try:
			return float(num)
		except TypeError:
			print("Please enter a valid number", file=sys.stderr)
			exit(1)

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
	parser = argparse.ArgumentParser()
	parser.add_argument('value')
	parser.add_argument('from_', metavar='from' )
	parser.add_argument('to', nargs='?', default='inr')
	args = parser.parse_args()
	return args.from_.upper(), args.to.upper(), float(conv(args.value))

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
		print('Unable to cache results.\n', file=sys.stderr)
		# exit(1)
		pass
	return tmp

def get_rates_current(overwrite = False):
	url = URL.format('latest.json')
	with open(cache_file, 'r', encoding='utf-8') as cache:
		rates = json.load(cache)
	try:
		r = requests.get(url)
		r.raise_for_status()
	except ConnectionError:
		print('Unable to update exchange rates.', file=sys.stderr)
		return rates
		exit(1)
	except:
		# TODO change this
		print('Unable to update exchange rates.', file=sys.stderr)
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
		print('Unable to cache results.\n', file=sys.stderr)
		pass
	return rates

def get_rates():
	try:
		with open(cache_file, 'r', encoding='utf-8') as cache:
			rates = json.load(cache)
	except FileNotFoundError:
		return create_cache()
	time_since_last_update = datetime.datetime.today() - datetime.datetime.strptime(rates['date'], '%a, %d %b %Y %H:%M:%S %Z')
	if time_since_last_update > datetime.timedelta(days=1):
		print('Updating rates')
		return get_rates_current()
	return rates

def convert(rates, from_curr, to_curr, val):
	rate = 0
	base = rates['base']
	rates = rates['rates']
	if from_curr == base:
		try:
			rate = rates[to_curr]['rate']
		except KeyError:
			print(f'Unknown currency: {to_curr}', file=sys.stderr)
			exit(1)
	elif from_curr not in rates:
		print(f'Unknown currency: {from_curr}', file=sys.stderr)
		exit(1)
	if to_curr == base:
		rate = 1 / rates[from_curr]['rate']
	elif to_curr not in rates:
		print(f'Unknown currency: {to_curr}', file=sys.stderr)
		exit(1)
	if not rate:
		rate = rates[to_curr]['rate'] / rates[from_curr]['rate']
	conv_rate = f'{val * rate :.2f}'
	fmt = 'i' if to_curr == 'INR' else 'w'
	conv_rate = conv(conv_rate, fmt)
	if 'symbol' in rates[to_curr].keys():
		conv_rate = rates[to_curr]['symbol'] + ' ' + conv_rate
	return conv_rate

if __name__ == '__main__':
	# create 'data' folder if it doesn't already exist
	Path(os.path.dirname(cache_file)).mkdir(parents=True, exist_ok=True)
	args = parse_args()
	converted = convert(get_rates(), *args)
	print(converted)
