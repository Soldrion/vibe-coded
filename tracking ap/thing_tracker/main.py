import sys
import requests
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui_main import MainWindow
from datetime import datetime
APP_VERSION = "1.0.0"
def check_for_updates(current_version, parent=None):
    try:
        url = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/version.txt"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            latest = response.text.strip()
            if latest and latest != current_version:
                QMessageBox.information(
                    parent,
                    "Update Available",
                    f"A new version is available: {latest}\n\nPlease visit GitHub to update."
                )
    except Exception as e:
        print("Update check failed:", e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # IMPORTANT: show the window BEFORE showing any message boxes

    check_for_updates(APP_VERSION, parent=window)

    sys.exit(app.exec_())

