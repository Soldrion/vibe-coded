# Thing Tracker

Thing Tracker is this little app I made to track tasks for me.
All it does is create and track tasks from a JSON file.

I made it mostly just to learn about Qt and UI stuff
Vibe coded at first, took on the actual making of it once i understood what was what

no elevated permissions are required

## Installation Instructions

Supported platforms: Linux (KDE)

### Prerequisites:

Python or Python3
pip
Pyinstaller
PyQt5
pydbus

#### Download binaries here:
https://github.com/Soldrion/vibe-coded/releases


#### Build from source:

Run this in your terminal emulator:
```
git clone https://github.com/Soldrion/vibe-coded/tree/main
```

#### Compiled binary
then cd into thing_tracker...
and run this to compile the app
```
pyinstaller --onefile --add-data "ui_main.py:." main.py
```
#### Not compiled (for easy modding)
```
python main.py
```

## Updating
Updating is a two-step process.

#### Step 1
Move the binaries and rebuild script into an isolated file.
#### Step 2
Open main, then press update. This will make a bunch of .py, .py.bak, and .spec files. Don't worry about them, unless you want to mod the app.
#### Step 3
Run the rebuild script in your console.
#### Step 4 
Exit it and move the binaries where you want.
