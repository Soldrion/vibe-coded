import sys
import os
import time
import shutil
import tempfile
import requests
import subprocess
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMessageBox


def get_desktop_path():
    """Return the path to the user's desktop folder."""
    if sys.platform == "win32":
        return os.path.join(os.environ["USERPROFILE"], "Desktop")
    else:
        return os.path.join(os.path.expanduser("~"), "Desktop")


def log_message(message):
    """Append log message to update.log on the desktop."""
    desktop_path = get_desktop_path()
    log_path = os.path.join(desktop_path, "update.log")
    with open(log_path, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        f.write(f"{timestamp} {message}\n")


def show_message(title, message, error=False):
    app = QApplication([])
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Critical if error else QMessageBox.Information)
    msg_box.exec_()
    app.quit()


def wait_for_app_to_exit(timeout=3):
    time.sleep(timeout)


def download_and_replace_files(app_dir):
    files_to_update = [
        "main.py",
        "ui_main.py",
        "tracker_model.py",
        "storage.py",
        "utils.py",
    ]
    base_url = "https://raw.githubusercontent.com/Soldrion/vibe-coded/main/tracking%20ap/thing_tracker/"

    errors = []
    for filename in files_to_update:
        try:
            url = base_url + filename
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content = response.content

            local_path = os.path.join(app_dir, filename)
            backup_path = local_path + ".bak"

            if os.path.exists(local_path):
                shutil.copy2(local_path, backup_path)

            tmp_fd, tmp_path = tempfile.mkstemp()
            with os.fdopen(tmp_fd, 'wb') as tmp_file:
                tmp_file.write(content)

            shutil.move(tmp_path, local_path)
            log_message(f"Updated {filename} successfully.")

        except Exception as e:
            error_msg = f"Failed to update {filename}: {e}"
            errors.append(error_msg)
            log_message(error_msg)

    return errors


def restart_app(app_dir):
    """Restart the main application."""
    try:
        if getattr(sys, 'frozen', False):
            log_message("Restarting compiled app.")
            if sys.platform == "win32":
                CREATE_NO_WINDOW = 0x08000000
                DETACHED_PROCESS = 0x00000008
                subprocess.Popen([sys.executable], creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS)
            else:
                subprocess.Popen([sys.executable], preexec_fn=os.setsid)
        else:
            main_py = os.path.join(app_dir, "main.py")
            if os.path.exists(main_py):
                log_message("Restarting Python script.")
                subprocess.Popen([sys.executable, main_py])
            else:
                log_message("main.py not found, could not restart.")
                show_message("Restart Failed", "main.py not found. App not restarted.", error=True)
    except Exception as e:
        log_message(f"Restart failed: {e}")
        show_message("Restart Failed", f"Failed to restart app:\n{e}", error=True)


def main():
    if len(sys.argv) < 2:
        show_message("Updater Error", "Usage: updater.py <app_directory>", error=True)
        return

    app_dir = sys.argv[1]
    log_message("=== Update started ===")
    wait_for_app_to_exit()

    log_message("Downloading updates...")
    errors = download_and_replace_files(app_dir)

    if errors:
        msg = "\n".join(errors)
        show_message("Update Completed with Errors", msg, error=True)
        log_message("Update finished with errors.")
    else:
        show_message("Update Successful", "The application was updated successfully.")
        log_message("Update finished successfully.")

    restart_app(app_dir)
    log_message("=== Update done ===\n")
    SystemExit

if __name__ == "__main__":
    main()
