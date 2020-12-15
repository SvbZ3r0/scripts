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

class CurrencyExchange():
	def __init__(self):
		# self.from_curr, self.to_curr, self.val = args
		self.data = dict()
		with open(os.path.join(os.path.dirname(sys.argv[0]), 'data', 'curx.conf')) as f:
			conf = json.load(f)
		self.URL = 'https://openexchangerates.org/api/{0}?app_id={1}&base=USD&show_alternative=true&prettyprint=false'.format('{0}', conf['APP_KEY'])
		self.cache_file = os.path.join(os.path.dirname(sys.argv[0]), 'data', 'rates.json')
		# create 'data' folder if it doesn't already exist
		Path(os.path.dirname(self.cache_file)).mkdir(parents=True, exist_ok=True)
		self.load_rates()

	def write_to_file(self):
		try:
			with open(self.cache_file, 'w', encoding='utf-8') as cache:
				json.dump(self.data, cache, indent=4)
		except IOError:
			print('Unable to cache results.', file=sys.stderr)
			pass

	def load_rates(self):
		try:
			with open(self.cache_file, 'r', encoding='utf-8') as cache:
				self.data = json.load(cache)
		except FileNotFoundError:
			self.create_cache()
			return
		time_since_last_update = datetime.datetime.today() - datetime.datetime.strptime(self.data['date'], '%a, %d %b %Y %H:%M:%S %Z')
		if time_since_last_update > datetime.timedelta(days=1):
			print('Updating rates')
			self.get_current_rates()

	def get_current_rates(self, overwrite = False):
		url = self.URL.format('latest.json')
		try:
			r = requests.get(url)
			r.raise_for_status()
		except ConnectionError:
			print('Unable to update exchange rates.', file=sys.stderr)
			return
		except:
			# TODO change this
			print('Unable to update exchange rates.', file=sys.stderr)
			return
		data = self.data
		data['date'] = r.headers['Last-Modified']
		_rates = r.json()
		data['base'] = _rates['base']
		_rates = _rates['rates']
		# TODO add functionality for help option
		for k,v in _rates.items():
			data['rates'][k]['rate'] = v
		self.data = data
		self.write_to_file()

	def create_cache(self):
		url = self.URL.format('currencies.json')
		try:
			r = requests.get(url)
			r.raise_for_status()
		except:
			# TODO
			print('Unable to get exhange rates', file=sys.stderr)
			exit(1)
		print(r.text)
		currencies = json.loads(r.text)
		# data['date'] = datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%d')
		data['date'] = r.headers['Last-Modified']	# format '%a, %d %b %Y %H:%M:%S %Z'
		data['base'] = 'USD'
		data['rates'] = dict()
		for k,v in currencies.items():
			data['rates'][k] = {'name': v}
		data['etag'] = r.headers['Etag']
		url = self.URL.format('latest.json')
		try:
			r = requests.get(url)
			r.raise_for_status()
		except:
			# TODO
			pass
		rates = json.loads(r.text)['rates']
		for k,v in currencies.items():
			data['rates'][k]['rate'] = rates[k]
		self.data = data
		self.write_to_file()

	def convert(self, from_curr, to_curr, val):
		rate = 0
		base = self.data['base']
		rates = self.data['rates']
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
		converted = f'{val * rate :.2f}'
		fmt = 'i' if to_curr == 'INR' else 'w'
		converted = conv(converted, fmt)
		if 'symbol' in rates[to_curr].keys():
			converted = rates[to_curr]['symbol'] + ' ' + converted
		return converted


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

if __name__ == '__main__':
	args = parse_args()
	converter = CurrencyExchange()
	converted = converter.convert(*args)
	print(converted)
