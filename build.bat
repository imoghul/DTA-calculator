cd scripts
python saveConfigDir.py
python -m PyInstaller -F --add-data "configdir.txt;." runFactory.py
del runFactory.spec
move dist\runFactory.exe ..\run.exe