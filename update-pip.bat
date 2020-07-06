python -m pip install -U pip
for /F "delims===" %%i in ('pip freeze -l') do pip install -U %%i