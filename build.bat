@REM change directory into the scripts directory
cd scripts 
@REM create or update the configdir.txt to contain the config dir that the script will use in the .exe
@REM python saveConfigDir.py 
@REM create the exe including the configdir.txt in it
@REM python -m PyInstaller -F --add-data "configdir.txt;." --icon="..\deps\phononic_icon.ico" run.py 
python -m PyInstaller -F --icon="..\deps\phononic_icon.ico" run.py 
@REM remove extra .spec file
del run.spec 
@REM copy the exe from dist to parent directory
copy dist\run.exe ..\run.exe