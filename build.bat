@REM change directory into the scripts directory
cd scripts 
@REM create or update the configdir.txt to contain the config dir that the script will use in the .exe
python saveConfigDir.py 
@REM create the exe including the configdir.txt in it
python -m PyInstaller -F --add-data "configdir.txt;." --icon="..\deps\phononic_icon.ico" run.py 
@REM remove extra .spec file
del run.spec 
@REM move the exe from dist to parent directory
@REM move dist\run.exe ..\run.exe 