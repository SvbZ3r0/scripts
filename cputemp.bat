:: Source - https://stackoverflow.com/a/24005062/4477680

@echo off
setlocal
for /f "skip=1 tokens=2 delims==" %%A in (
	'wmic /namespace:\\root\wmi PATH MSAcpi_ThermalZoneTemperature get CurrentTemperature /value'
	:: MSAcpi_ThermalZoneTemperature gives temp in centiKelvin
	) do set /a "HunDegCel=(%%~A*10)-27315"
echo %HunDegCel:~0,-2%.%HunDegCel:~-2%°C
echo.
:: alt248 °