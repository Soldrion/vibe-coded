import sys
import requests
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui_main import MainWindow
from datetime import datetime
import time
from PyQt5.QtCore import QTimer
APP_VERSION = "1.0.0"

def check_for_updates(current_version, parent=None):
    import requests
    try:
        url = f"https://raw.githubusercontent.com/Soldrion/vibe-coded/main/tracking%20ap/thing_tracker/version.txt?nocache={int(time.time())}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            latest = response.text.strip()
            print(f"version from github: '{latest}'")
            if latest and latest != current_version:
                # Use QTimer.singleShot to delay the message box so the window is ready
                QTimer.singleShot(0, lambda: QMessageBox.information(
                    parent,
                    "Update Available",
                    f"A new version is available: {latest}\n\nPlease update :)"
                ))
    except Exception as e:
        print("Update check failed:", e)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # IMPORTANT: show the window BEFORE showing any message boxes

    check_for_updates(APP_VERSION, parent=window)

    sys.exit(app.exec_())
