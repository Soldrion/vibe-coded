# vibe coded projects
I didnt actually truly vibe code, just asked the gipity how to use Qt
:
:
:
:
:




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
