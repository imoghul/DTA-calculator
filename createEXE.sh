python saveConfigDir.py
python -m PyInstaller -F --add-data "configdir.txt;." runFactory.py
cp dist/* .
rm -rf build
rm *.spec
