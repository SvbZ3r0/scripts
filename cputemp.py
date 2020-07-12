#!/usr/bin/env python

import os

if os.name != 'nt':
	print('This script currently supports Windows only')
	exit(1)

def cputemp():
	cmd = 'wmic /namespace:\\\\root\\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature /value'
	with os.popen(cmd) as fh:
		val = fh.read().split('=')[-1]
	val = (int(val) - 2731.5) / 10			# convert mK to °C
	return str(val)

if __name__ == '__main__':
	print(cputemp() + '°C')