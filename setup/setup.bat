@echo off

echo Creating virtual environment...
cd ..
mkdir env
cd env
py -m venv ImageProcessorEnv
echo .
echo Successfully created virtual environment
cd ../setup
pip install -r requirements.txt
echo Successfully installed required packages