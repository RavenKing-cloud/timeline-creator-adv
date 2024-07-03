import sys
import json
import os
import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QFileDialog, QLabel, QScrollArea, QMainWindow,
                             QAction, QToolBar, QInputDialog, QVBoxLayout, QListWidget, QLineEdit, QDateEdit, 
                             QPushButton, QFileDialog, QFormLayout, QLabel, QDialog, QTextEdit, QMessageBox,
                             QListWidgetItem, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt
from src.render import render_timeline
from src.sort import sort_json
from src.date_select import DateDialog


class EventWindow(QDialog):
    def __init__(self, event_data, file_path, parent=None):
        super(EventWindow, self).__init__(parent)
        self.setWindowTitle(event_data['name'])
        self.setGeometry(200, 200, 400, 300)
        self.event_data = event_data
        self.file_path = file_path
        self.modified = False  # Track if changes are made

        layout = QFormLayout()
        self.setLayout(layout)

        self.name_label = QLabel("Event Name:")
        self.name_text = QLineEdit(event_data['name'])
        layout.addRow(self.name_label, self.name_text)

        self.date_label = QLabel("Event Date:")
        self.date_text = QDateEdit(self)
        event_date = datetime.date(event_data['date'][2], event_data['date'][0], event_data['date'][1])
        self.date_text.setDate(event_date)
        layout.addRow(self.date_label, self.date_text)

        self.description_label = QLabel("Description:")
        self.description_text = QTextEdit(event_data['description'])
        layout.addRow(self.description_label, self.description_text)

        self.image_label = QLabel("Image:")
        self.image_button = QPushButton("Add Image" if not event_data['images'] else "Change Image")
        self.image_button.clicked.connect(self.change_image)
        layout.addRow(self.image_label, self.image_button)

        self.image_view = QLabel()
        layout.addRow(self.image_view)

        if event_data['images']:
            image_path = event_data['images'][0]
            pixmap = QPixmap(image_path)
            self.image_view.setPixmap(pixmap.scaled(300, 200, aspectRatioMode=Qt.KeepAspectRatio))
        else:
            self.image_view.setText("No image available")

        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_event)
        layout.addRow(self.save_button)

        # Delete button
        self.delete_button = QPushButton("Delete Event")
        self.delete_button.clicked.connect(self.delete_event)
        layout.addRow(self.delete_button)

    def save_event(self):
        # Update event_data with current values from UI
        new_name = self.name_text.text()
        new_date = [
            self.date_text.date().month(),
            self.date_text.date().day(),
            self.date_text.date().year()
        ]
        new_description = self.description_text.toPlainText()

        try:
            # Read existing JSON data
            with open(self.file_path, 'r') as json_file:
                json_data = json.load(json_file)

            # Find and update the specific event
            for event in json_data['events']:
                if event['name'] == self.event_data['name']:
                    event['name'] = new_name
                    event['date'] = new_date
                    event['description'] = new_description
                    # Preserve existing images paths (relative)
                    event['images'] = self.event_data['images']
                    break

            # Write updated JSON data back to the file
            with open(self.file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)

            self.modified = False  # Reset modified flag after saving

            # Show confirmation message
            QMessageBox.information(self, 'Save Successful', 'Event data has been successfully saved.')

            # Reload events into selector and timeline in MainWindow
            mainWindow.load_events_into_selector(self.file_path)
            mainWindow.render_timeline_from_file(self.file_path)

        except Exception as e:
            print(f"Error saving event data: {e}")

    def change_image(self):
        # Change or add image logic
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", image_dir, "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        
        if file_path and os.path.commonpath([image_dir, file_path]) == image_dir:
            # Save relative path in event_data
            rel_path = os.path.relpath(file_path, os.path.dirname(__file__))
            self.event_data['images'] = [rel_path]

            # Display image in image_view
            pixmap = QPixmap(file_path)
            self.image_view.setPixmap(pixmap.scaled(300, 200, aspectRatioMode=Qt.KeepAspectRatio))
        else:
            print("Selected file is not within the allowed directory.")

    def delete_event(self):
        confirm = QMessageBox.question(self, 'Delete Event', 'Are you sure you want to delete this event?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                with open(self.file_path, 'r') as json_file:
                    json_data = json.load(json_file)

                json_data['events'] = [event for event in json_data['events'] if event['name'] != self.event_data['name']]

                with open(self.file_path, 'w') as json_file:
                    json.dump(json_data, json_file, indent=4)

                # Reload events into selector and timeline in MainWindow
                mainWindow.load_events_into_selector(self.file_path)
                mainWindow.render_timeline_from_file(self.file_path)

                self.accept()  # Close the dialog after deletion
            except Exception as e:
                print(f"Error deleting event: {e}")

    def reject(self):
        # Override reject to handle cancel/close button
        if self.modified:
            confirm = QMessageBox.question(self, 'Discard Changes', 'Discard changes made to this event?',
                                           QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.Yes:
                super(EventWindow, self).reject()
        else:
            super(EventWindow, self).reject()

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

        # Add dark mode toggle action
        self.dark_mode = False
        dark_mode_action = QAction(QIcon.fromTheme("weather-night"), "Toggle Dark Mode", self)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        toolbar.addAction(dark_mode_action)

        # Layout
        main_layout = QVBoxLayout()

        # Horizontal layout to manage size allocation
        h_layout = QHBoxLayout()

        # ListWidget for event selection
        self.event_list = QListWidget()
        self.event_list.setFixedWidth(250)  # Adjust the width as needed
        self.event_list.itemClicked.connect(self.display_event)
        h_layout.addWidget(self.event_list)

        # Scroll Area for timeline display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # QLabel to display the rendered image
        self.lbl_image = QLabel()
        scroll_area.setWidget(self.lbl_image)

        h_layout.addWidget(scroll_area)

        main_layout.addLayout(h_layout)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            app.setStyle("Fusion")
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
        else:
            app.setStyle("Fusion")
            palette = QPalette()
            app.setPalette(palette)
        self.render_timeline_from_file(self.current_file_path)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)", options=options)

        if file_path:
            self.current_file_path = file_path
            self.render_timeline_from_file(file_path)
            self.load_events_into_selector(file_path)

    def render_timeline_from_file(self, file_path):
        try:
            img_path = render_timeline(file_path, self.dark_mode)
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
                                json.dump(json_data, json_file, indent=4)
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
                                    json.dump(json_data, json_file, indent=4)

                                print(f"Event '{event_name}' added to {self.current_file_path}")
                                sort_json(self.current_file_path)
                                # Reload events into selector and timeline
                                self.load_events_into_selector(self.current_file_path)
                                self.render_timeline_from_file(self.current_file_path)
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
        image_dir = os.path.join(os.path.dirname(__file__), 'images')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", image_dir, "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            return os.path.relpath(file_path, os.path.dirname(__file__))
        else:
            return None

    def load_events_into_selector(self, file_path):
        self.event_list.clear()
        try:
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
                for event in json_data.get('events', []):
                    event_date = datetime.date(event['date'][2], event['date'][0], event['date'][1])
                    event_text = f"{event['name']} ({event_date.strftime('%B %d, %Y')})"
                    item = QListWidgetItem(event_text)
                    item.setData(Qt.UserRole, event)
                    self.event_list.addItem(item)
        except Exception as e:
            print(f"Error loading events: {e}")

    def display_event(self, item):
        event_data = item.data(Qt.UserRole)
        if event_data:
            self.event_window = EventWindow(event_data, self.current_file_path)
            result = self.event_window.exec_()
            if result == QDialog.Accepted:
                self.load_events_into_selector(self.current_file_path)
                self.render_timeline_from_file(self.current_file_path)

    def get_date(self, title):
        date_dialog = DateDialog(title, self)
        return date_dialog.get_date()

"""Not Currently used or working: vvv"""
#class SingleLineListJsonEncoder(json.JSONEncoder):
#    def encode(self, obj):
#        if isinstance(obj, list):
#            return '[' + ', '.join(self.encode(el) for el in obj) + ']'
#        return super(SingleLineListJsonEncoder, self).encode(obj)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
