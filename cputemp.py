import os

def cputemp():
	with os.popen('cputemp.bat') as fh:
		return fh.read()

if __name__ == '__main__':
	print(cputemp().strip())