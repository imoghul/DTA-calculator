cd scripts Rem change directory into the scripts directory
python saveConfigDir.py Rem create or update the configdir.txt to contain the config dir that the script will use in the .exe
python -m PyInstaller -F --add-data "configdir.txt;." runFactory.py Rem create the exe including the configdir.txt in it
del runFactory.spec Rem remove extra .spec file
move dist\runFactory.exe ..\run.exe Rem move the exe from dist to parent directory