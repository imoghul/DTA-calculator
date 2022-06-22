#python -m PyInstaller -F --add-data "locations.json;." runFactory.py
python -m PyInstaller -F runFactory.py
cp dist/* .
rm -rf build
rm *.spec
