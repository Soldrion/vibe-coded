import sys
import os
import subprocess
import requests
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QComboBox, QDateEdit, QCheckBox, QLabel, QCalendarWidget,
    QTimeEdit, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QDate, QTime
from tracker_model import TrackedItem
from storage import save_items, load_items
from utils import filter_items
from datetime import datetime, date
try:
    from notifier import send_notification
except ImportError:
    send_notification = None


class MainWindow(QMainWindow):
    def load_app_version(self):
        try:
            base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            version_path = os.path.join(base, "version.txt")
            with open(version_path, "r") as f:
                return f.read().strip()
        except Exception:
            return "unknown"

    def __init__(self):
        super().__init__()

        self.APP_VERSION = self.load_app_version()
        self.setWindowTitle(f"Thing Tracker v{self.APP_VERSION}")
        self.setMinimumSize(950, 650)

        self.items = load_items()

        self.init_ui()
        self.refresh_list()
        self.check_notifications()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        input_layout = QHBoxLayout()

        input_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Thing name")
        input_layout.addWidget(self.name_input)

        input_layout.addWidget(QLabel("Tags:"))
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("tag1, tag2")
        input_layout.addWidget(self.tag_input)

        input_layout.addWidget(QLabel("Repeating?"))
        self.repeat_input = QComboBox()
        self.repeat_input.addItems(["None", "Daily", "Weekly", "Fortnightly", "Monthly", "Yearly"])
        input_layout.addWidget(self.repeat_input)


        input_layout.addWidget(QLabel("Priority:"))
        self.priority_input = QComboBox()
        self.priority_input.addItems(["Low", "Medium", "High"])
        input_layout.addWidget(self.priority_input)

        input_layout.addWidget(QLabel("Start Date:"))
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate())
        input_layout.addWidget(self.start_date_input)

        input_layout.addWidget(QLabel("Start Time:"))
        self.start_time_input = QTimeEdit()
        self.start_time_input.setDisplayFormat("HH:mm")
        self.start_time_input.setTime(QTime.currentTime())
        input_layout.addWidget(self.start_time_input)

        input_layout.addWidget(QLabel("Due Date:"))
        self.due_input = QDateEdit()
        self.due_input.setCalendarPopup(True)
        self.due_input.setDate(QDate.currentDate())
        input_layout.addWidget(self.due_input)

        input_layout.addWidget(QLabel("End Time:"))
        self.end_time_input = QTimeEdit()
        self.end_time_input.setDisplayFormat("HH:mm")
        self.end_time_input.setTime(QTime.currentTime().addSecs(3600))
        input_layout.addWidget(self.end_time_input)

        input_layout.addWidget(QLabel("Done?"))
        self.completed_input = QCheckBox()
        input_layout.addWidget(self.completed_input)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_item)
        input_layout.addWidget(self.add_button)

        self.update_button = QPushButton("Update App")
        self.update_button.clicked.connect(self.run_update_helper)
        input_layout.addWidget(self.update_button)
        self.notify_button = QPushButton("Check Notifications")
        self.notify_button.clicked.connect(self.check_notifications)
        input_layout.addWidget(self.notify_button)

        main_layout.addLayout(input_layout)

        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by name or tag...")
        self.search_bar.textChanged.connect(self.refresh_list)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_bar)
        main_layout.addLayout(search_layout)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(8)
        self.tree.setHeaderLabels([
            "Name", "Tags", "Start Date", "Start Time", "Due", "End Time", "Priority", "Done"
        ])
        self.tree.setDragDropMode(QTreeWidget.InternalMove)
        self.tree.itemChanged.connect(self.handle_item_changed)
        main_layout.addWidget(self.tree)

        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.refresh_list)
        main_layout.addWidget(QLabel("Filter from Due Date:"))
        main_layout.addWidget(self.calendar)

    def add_item(self):
        name = self.name_input.text().strip()
        tags = [t.strip() for t in self.tag_input.text().split(",") if t.strip()]
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        start_time = self.start_time_input.time().toString("HH:mm")
        due_date = self.due_input.date().toString("yyyy-MM-dd")
        end_time = self.end_time_input.time().toString("HH:mm")
        priority = self.priority_input.currentText()
        completed = self.completed_input.isChecked()

        if not name:
            return

        item = TrackedItem(
            name=name,
            tags=tags,
            start_date=start_date,
            start_time=start_time,
            due_date=due_date,
            end_time=end_time,
            completed=completed,
            priority=priority,
            fields={}
        )
        self.items.append(item)
        save_items(self.items)
        self.clear_inputs()
        self.refresh_list()

    def clear_inputs(self):
        self.name_input.clear()
        self.tag_input.clear()
        self.priority_input.setCurrentIndex(0)
        self.start_date_input.setDate(QDate.currentDate())
        self.start_time_input.setTime(QTime.currentTime())
        self.due_input.setDate(QDate.currentDate())
        self.end_time_input.setTime(QTime.currentTime().addSecs(3600))
        self.completed_input.setChecked(False)

    def refresh_list(self):
        self.tree.blockSignals(True)
        self.tree.clear()
        query = self.search_bar.text().lower()
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        selected_dt = datetime.strptime(selected_date, "%Y-%m-%d")

        filtered = filter_items(self.items, query)
        filtered = [i for i in filtered if datetime.strptime(i.due_date, "%Y-%m-%d") >= selected_dt]

        for i in filtered:
            row = QTreeWidgetItem([
                i.name,
                ", ".join(i.tags),
                i.start_date,
                i.start_time,
                i.due_date,
                i.end_time,
                i.priority,
                ""
            ])
            row.setFlags(row.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            row.setCheckState(7, Qt.Checked if i.completed else Qt.Unchecked)
            self.tree.addTopLevelItem(row)

        self.tree.blockSignals(False)
        self.tree.sortItems(2, Qt.AscendingOrder)

    def handle_item_changed(self, item, column):
        if column == 7:
            name = item.text(0)
            start_date = item.text(2)
            start_time = item.text(3)
            due = item.text(4)
            end_time = item.text(5)
            checked = item.checkState(7) == Qt.Checked

            for tracked in self.items:
                if (tracked.name == name and tracked.due_date == due and
                    tracked.start_date == start_date and tracked.start_time == start_time
                    and tracked.end_time == end_time):
                    tracked.completed = checked
                    save_items(self.items)
                    break

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected = self.tree.selectedItems()
            if not selected:
                return
            for item in selected:
                name = item.text(0)
                due = item.text(4)
                start_date = item.text(2)
                start_time = item.text(3)
                end_time = item.text(5)

                for tracked in self.items:
                    if (tracked.name == name and tracked.due_date == due and
                        tracked.start_date == start_date and tracked.start_time == start_time
                        and tracked.end_time == end_time):
                        self.items.remove(tracked)
                        break
            save_items(self.items)
            self.refresh_list()
        else:
            super().keyPressEvent(event)

    def check_notifications(self):
        if not send_notification:
            print("Notifier not available. Install pydbus or equivalent.")
            return

        today = date.today()
        due_tasks = []
        for task in self.items:
            due_date = datetime.strptime(task.due_date, "%Y-%m-%d").date()
            if due_date <= today and not task.completed:
                due_tasks.append(task)

        if not due_tasks:
            send_notification("Thing Tracker", "No tasks due or overdue.")
        else:
            body = "\n".join(f"{t.name} (Due: {t.due_date})" for t in due_tasks)
            send_notification("Thing Tracker - Due Tasks", body)

    def run_update_helper(self):
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller binary
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))

        updater_path = os.path.join(app_dir, "updater")

        if not os.path.exists(updater_path):
            # If updater is a .exe on Windows, add .exe extension
            if sys.platform == "win32":
                updater_path_exe = updater_path + ".exe"
                if os.path.exists(updater_path_exe):
                    updater_path = updater_path_exe
                else:
                    QMessageBox.warning(self, "Update Error", f"Updater binary not found at:\n{updater_path} or {updater_path_exe}")
                    return
            else:
                QMessageBox.warning(self, "Update Error", f"Updater binary not found at:\n{updater_path}")
                return

        # Optionally check for updates here before running updater

        try:
            subprocess.Popen([updater_path, app_dir])
        except Exception as e:
            QMessageBox.warning(self, "Update Error", f"Failed to start updater:\n{e}")
            return

        # Close the app after launching updater
        app = QApplication.instance()
        if app:
            app.quit()
