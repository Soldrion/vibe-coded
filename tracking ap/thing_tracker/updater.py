import sys
import os
import shutil
import tempfile
import requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox

def log_message(message):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    log_file = os.path.join(desktop, "update.log")
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")

def show_message(title, message, error=False):
    app = QApplication.instance() or QApplication([])
    msg_box = QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Critical if error else QMessageBox.Information)
    msg_box.exec_()
    if not QApplication.instance():
        app.quit()

def download_and_replace_files(app_dir):
    base_url = "https://raw.githubusercontent.com/Soldrion/vibe-coded/main/tracking%20ap/thing_tracker/"
    files = ["main.py", "ui_main.py", "tracker_model.py", "storage.py", "utils.py"]

    errors = []
    for fname in files:
        try:
            url = base_url + fname
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            content = r.content

            local_path = os.path.join(app_dir, fname)
            backup_path = local_path + ".bak"

            if os.path.exists(local_path):
                shutil.copy2(local_path, backup_path)

            tmp_fd, tmp_path = tempfile.mkstemp()
            with os.fdopen(tmp_fd, 'wb') as tmp_file:
                tmp_file.write(content)

            shutil.move(tmp_path, local_path)
            log_message(f"Updated {fname} successfully.")
        except Exception as e:
            err = f"Failed to update {fname}: {e}"
            errors.append(err)
            log_message(err)

    return errors

def restart_app(app_dir):
    try:
        if getattr(sys, 'frozen', False):
            # Relaunch the executable
            if sys.platform == "win32":
                CREATE_NO_WINDOW = 0x08000000
                DETACHED_PROCESS = 0x00000008
                subprocess.Popen([sys.executable], creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS)
            else:
                import os
                import subprocess
                subprocess.Popen([sys.executable], preexec_fn=os.setsid)
        else:
            main_py = os.path.join(app_dir, "main.py")
            if os.path.exists(main_py):
                subprocess.Popen([sys.executable, main_py])
            else:
                show_message("Restart Failed", "main.py not found. Cannot restart app.", error=True)
    except Exception as e:
        show_message("Restart Failed", f"Failed to restart app:\n{e}", error=True)

def main():
    if len(sys.argv) < 2:
        show_message("Updater Error", "Usage: updater.py <app_directory>", error=True)
        return

    app_dir = sys.argv[1]

    log_message("=== Update started ===")

    errors = download_and_replace_files(app_dir)

    if errors:
        show_message("Update Completed with Errors", "\n".join(errors), error=True)
    else:
        show_message("Update Successful", "The application was updated successfully.")

    restart_app(app_dir)
    log_message("=== Update done ===")

if __name__ == "__main__":
    main()
