@echo off

REM This is the developer setup script for windows.
REM We assume you installed python in C:\Python27
SET PYTHON=C:\Python27

REM Update pip
%PYTHON%\Scripts\easy_install pip
%PYTHON%\Scripts\pip install virtualenv

REM Create the virtual environment named venv
%PYTHON%\Scripts\virtualenv --clear --distribute --system-site-packages venv 

REM Activate the virtual environment
CALL venv\Scripts\activate.bat

REM Update pip and distribute in venv
pip install --upgrade distribute

REM Install development requirements
pip install -r codalab\requirements\dev_azure.txt

ECHO "One time setup is complete. You are ready to proceed."
