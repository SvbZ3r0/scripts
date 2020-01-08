import os
import sys
import json
import requests
import datetime
from pathlib import Path

URL = 'https://api.exchangeratesapi.io/latest'
cache_file = os.path.join(os.path.dirname(sys.argv[0]), 'data', 'currency rates.json')
rates = dict()

# TODO add support for currency symbols on supported OS

def parse_args():
	if len(sys.argv) != 4:
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

def get_rate_current():
	try:
		r = requests.get(URL)
		r.raise_for_status()
	except ConnectionError:
		print('Unable to retrieve exchange rates.')
		exit(1)
	except:
		# TODO change this
		print('Unable to retrieve exchange rates.')
		exit(1)
	_rates = r.json()
	# TODO add functionality for help option
	# rates['date'] = _rates['date']
	# rates['base'] = _rates['base']
	# for c,v in _rates['rates'].items():
	# 	rates[c]['rate'] = v
	rates = _rates
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
		return get_rate_current()
	# Exchange rates API is updated at 4:00 pm CET (7:00 am PST)
	if datetime.datetime.strptime(rates['date'], '%Y-%m-%d') - datetime.datetime.today() > datetime.timedelta(days=1, hours=7):
		return get_rate_current()
	return rates

def convert(rates, from_curr, to_curr, val):
	rate = 0
	if from_curr == rates['base']:
		rate = rates['rates'][to_curr]
	elif from_curr not in rates['rates']:
		print(f'Unknown currency: {from_curr}')
		exit(1)
	if to_curr == rates['base']:
		rate = 1 / rates['rates'][from_curr]
	elif to_curr not in rates['rates']:
		print(f'Unknown currency: {to_curr}')
		exit(1)
	if not rate:
		rate = rates['rates'][to_curr] / rates['rates'][from_curr]
	return val * rate

if __name__ == '__main__':
	# create 'data' folder if it doesn't already exist
	Path(os.path.dirname(cache_file)).mkdir(parents=True, exist_ok=True)
	args = parse_args()
	converted = convert(get_rates_cache(), *args)
	print(f'{converted:.2f}')
