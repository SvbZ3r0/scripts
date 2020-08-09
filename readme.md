# Personal use scripts

These scripts were written for personal use. You are free to do with these as you wish.

### cputemp.bat

Retrieves the temperature of the CPU. Windows only. May not work on all machines.

### cputemp.py

Gets the CPU temperature in a python script. For now, Windows only. May not work on all machines.

### curx.py

Commandline currency conversion.

##### Requirements: 
[`Open Exchange Rate API Key`](https://openexchangerates.org/signup/free)

[`number_format.py`](https://github.com/SvbZ3r0/scripts#number_formatpy) (*Optional*)

##### Usage:
```
curx.py <val> <from> [to]
```

To currency defaults to INR (₹).

### number_format.py

Adds commas(,) to numbers to format them according to Indian or Western format.

##### Usage:
```
number_format.py [-i|-w] <num>
```

Format defaults to Indian.

### pdfmerge.py

Launches GUI to merge multiple PDFs into a single document.

##### Requirements: 
[`pyQt5`](https://pypi.org/project/PyQt5/)

[`pyPDF2`](https://pypi.org/project/PyPDF2/)

```
pip install PyQt5
pip install PyPDF2
```

### tasks.py

Commandline TODO list manager. Written with the Enigma skin on Rainmeter in mind.

##### Usage:
```
tasks.py
tasks.py add <todo>
tasks.py del <num>
tasks.py rot <steps>
tasks.py prom <num>
tasks.py demo <num>
tasks.py pop
```

### roll.py

Rolls a n-sided die.

##### Usage:
```
roll.py [n]
```

Defaults to 6-sided die.

### toss.py

Tosses a coin

### update-pip.bat

Updates all pip packages
