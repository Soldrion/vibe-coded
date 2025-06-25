import sys
import os
import time
import shutil
import tempfile
import requests
import subprocess

def wait_for_app_to_exit(app_dir, timeout=15):
    """Wait a few seconds for the app to close."""
    time.sleep(3)

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

            os.replace(tmp_path, local_path)

        except Exception as e:
            errors.append(f"Failed to update {filename}: {e}")

    return errors

def restart_app(app_dir):
    """Restart the app whether it's source or frozen."""
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
        subprocess.Popen([exe_path])
    else:
        main_script = os.path.join(app_dir, "main.py")
        if not os.path.exists(main_script):
            print("Main script not found, cannot restart.")
            return
        subprocess.Popen([sys.executable, main_script])

def main():
    if len(sys.argv) < 2:
        print("Usage: updater.py <app_directory>")
        sys.exit(1)

    app_dir = sys.argv[1]

    print("Waiting for app to exit...")
    wait_for_app_to_exit(app_dir)

    print("Downloading updates...")
    errors = download_and_replace_files(app_dir)

    if errors:
        print("Update finished with errors:")
        for err in errors:
            print("  -", err)
    else:
        print("Update completed successfully.")

    print("Restarting app...")
    restart_app(app_dir)

    print("Updater done.")
    sys.exit(0)

if __name__ == "__main__":
    main()
