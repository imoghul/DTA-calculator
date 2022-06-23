cd scripts
python saveConfigDir.py
python -m PyInstaller -F --add-data "configdir.txt;." run.py
cp dist/*.exe ../run.exe
rm -rf build dist
rm *.spec
