@echo off
echo Clearing Python cache...
echo.

REM Remove __pycache__ directories
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM Remove .pyc files
del /s /q *.pyc 2>nul

echo.
echo Cache cleared!
echo.
echo Now run: python test_setup.py
pause
