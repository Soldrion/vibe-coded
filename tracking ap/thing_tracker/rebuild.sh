#!/bin/bash
set -e
echo "Starting rebuild..."
echo "*********************************"\n
echo "*********************************"\n
echo "Make sure you have no other .py, .bak, .txt, .md, or .spec files in the directory where this script is run."
read -r -p "Are you sure? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    continue
else
    echo "Please close this window."
fi

echo "*********************************"\n
echo "*********************************"\n
cd "$(dirname "$0")"

if [[ -d venv311 ]]; then
    source venv311/bin/activate
fi
pyinstaller --onefile updater.py
pyinstaller --onefile --add-data "ui_main.py:." --add-data "storage.py:." --add-data "notifier.py:." --add-data "tracker_model.py:." --add-data "utils.py:." --add-data "version.txt:." main.py
echo "*********************************"
echo "Rebuild complete. Cleaning up..."
echo "*********************************"
rm -f *.py *.bak *.spec *.txt *.md
rm -rf build
mv dist/main $("pwd")/main
mv dist/updater $("pwd")/updater
rm -rf dist

echo "Please close this window."
done
