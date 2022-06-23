cd scripts
python saveConfigDir.py
python -m PyInstaller -F --add-data "configdir.txt;." runFactory.py
move dist\runFactory.exe ..