import sys
import json
import os
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFileDialog, QLabel, QScrollArea, QMainWindow,
                             QAction, QToolBar, QInputDialog, QDateEdit, QDialog, QVBoxLayout, QDialogButtonBox, 
                             QComboBox, QTextEdit, QFormLayout)
from PyQt5.QtGui import QPixmap, QIcon
from src.render import render_timeline
from src.sort import sort_json


class SingleLineListJsonEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, list):
            return '[' + ', '.join(self.encode(el) for el in obj) + ']'
        return super(SingleLineListJsonEncoder, self).encode(obj)


class DateDialog(QDialog):
    def __init__(self, title, parent=None):
        super(DateDialog, self).__init__(parent)
        self.setWindowTitle(title)

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(datetime.date.today())

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.date_edit)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_date(self):
        if self.exec_() == QDialog.Accepted:
            return self.date_edit.date().toPyDate()
        else:
            return None


class EventWindow(QDialog):
    def __init__(self, event_data, parent=None):
        super(EventWindow, self).__init__(parent)
        self.setWindowTitle(event_data['name'])
        self.setGeometry(200, 200, 400, 300)

        layout = QFormLayout()
        self.setLayout(layout)

        self.name_label = QLabel("Event Name:")
        self.name_text = QLabel(event_data['name'])
        layout.addRow(self.name_label, self.name_text)

        self.date_label = QLabel("Event Date:")
        event_date = datetime.date(event_data['date'][2], event_data['date'][0], event_data['date'][1])
        self.date_text = QLabel(event_date.strftime("%B %d, %Y"))
        layout.addRow(self.date_label, self.date_text)

        self.description_label = QLabel("Description:")
        self.description_text = QTextEdit(event_data['description'])
        self.description_text.setReadOnly(True)
        layout.addRow(self.description_label, self.description_text)

        if event_data['images']:
            self.image_label = QLabel("Image:")
            image_path = event_data['images'][0]  # Assuming one image per event for simplicity
            pixmap = QPixmap(image_path)
            self.image_view = QLabel()
            self.image_view.setPixmap(pixmap.scaled(300, 200, aspectRatioMode=1))
            layout.addRow(self.image_label, self.image_view)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_file_path = None

    def initUI(self):
        self.setWindowTitle('ONE-Liner - Timeline Editor')
        self.setGeometry(100, 100, 1400, 820)

        # Create a top toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Add actions to the toolbar
        open_action = QAction(QIcon.fromTheme("document-open"), "Open Timeline", self)
        open_action.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_action)

        create_action = QAction(QIcon.fromTheme("document-new"), "Create New Timeline", self)
        create_action.triggered.connect(self.create_timeline)
        toolbar.addAction(create_action)

        add_event_action = QAction(QIcon.fromTheme("list-add"), "Add Event to Timeline", self)
        add_event_action.triggered.connect(self.add_event_to_timeline)
        toolbar.addAction(add_event_action)

        # Layout
        layout = QVBoxLayout()

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # QLabel to display the rendered image
        self.lbl_image = QLabel()
        scroll_area.setWidget(self.lbl_image)

        layout.addWidget(scroll_area)

        # ComboBox for event selection
        self.event_selector = QComboBox()
        self.event_selector.currentIndexChanged.connect(self.display_event)
        layout.addWidget(self.event_selector)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)", options=options)

        if file_path:
            self.current_file_path = file_path
            self.render_timeline_from_file(file_path)
            self.load_events_into_selector(file_path)

    def render_timeline_from_file(self, file_path):
        try:
            img_path = render_timeline(file_path)
            pixmap = QPixmap(img_path)
            self.lbl_image.setPixmap(pixmap)
            self.lbl_image.setScaledContents(False)
        except Exception as e:
            print(f"Error rendering timeline: {e}")

    def create_timeline(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Create New JSON File", "", "JSON Files (*.json)", options=options)

        if file_path:
            timeline_name, ok = QInputDialog.getText(self, "Timeline Name", "Enter the timeline name:")
            if ok and timeline_name:
                start_date = self.get_date("Start Date")
                if start_date:
                    end_date = self.get_date("End Date")
                    if end_date:
                        json_data = {
                            "timeline_name": timeline_name,
                            "start_date": [start_date.month, start_date.day, start_date.year],
                            "end_date": [end_date.month, end_date.day, end_date.year],
                            "events": []
                        }

                        try:
                            with open(file_path, 'w') as json_file:
                                json.dump(json_data, json_file, indent=4, cls=SingleLineListJsonEncoder)
                            self.current_file_path = file_path
                            print(f"New JSON file created: {file_path}")
                            self.render_timeline_from_file(file_path)
                        except Exception as e:
                            print(f"Error creating JSON file: {e}")
                    else:
                        print("Invalid end date.")
                else:
                    print("Invalid start date.")
            else:
                print("Timeline name cannot be empty.")

    def get_date(self, title):
        date_dialog = DateDialog(title, self)
        return date_dialog.get_date()

    def add_event_to_timeline(self):
        if self.current_file_path:
            try:
                with open(self.current_file_path, 'r') as json_file:
                    json_data = json.load(json_file)

                event_name, ok = QInputDialog.getText(self, "Add Event", "Enter the event name:")
                if ok and event_name:
                    event_date = self.get_date("Select Event Date")
                    if event_date:
                        description, ok = QInputDialog.getText(self, "Event Description", "Enter the event description:")
                        if ok:
                            image_file = self.get_image_file()
                            if image_file:
                                new_event = {
                                    "name": event_name,
                                    "date": [event_date.month, event_date.day, event_date.year],
                                    "description": description,
                                    "images": [image_file]
                                }
                                json_data["events"].append(new_event)

                                with open(self.current_file_path, 'w') as json_file:
                                    json.dump(json_data, json_file, indent=4, cls=SingleLineListJsonEncoder)

                                print(f"Event '{event_name}' added to {self.current_file_path}")
                                sort_json(self.current_file_path)
                                self.render_timeline_from_file(self.current_file_path)
                                self.load_events_into_selector(self.current_file_path)
                            else:
                                print("No image selected.")
                        else:
                            print("Event description cannot be empty.")
                    else:
                        print("Invalid event date.")
                else:
                    print("Event name cannot be empty.")
            except Exception as e:
                print(f"Error adding event to JSON file: {e}")
        else:
            print("No file is currently open.")

    def get_image_file(self):
        image_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", image_dir, "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            return os.path.relpath(file_path, os.path.dirname(__file__))
        else:
            return None

    def load_events_into_selector(self, file_path):
        self.event_selector.clear()
        try:
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
                for event in json_data.get('events', []):
                    event_date = datetime.date(event['date'][2], event['date'][0], event['date'][1])
                    event_text = f"{event['name']} ({event_date.strftime('%B %d, %Y')})"
                    self.event_selector.addItem(event_text, event)
        except Exception as e:
            print(f"Error loading events: {e}")

    def display_event(self):
        event_data = self.event_selector.currentData()
        if event_data:
            self.event_window = EventWindow(event_data)
            self.event_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
