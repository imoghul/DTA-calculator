#python -m PyInstaller -F --add-data "configdir.txt;." runFactory.py
python -m PyInstaller -F runFactory.py
cp dist/* .
rm -rf build
rm *.spec
