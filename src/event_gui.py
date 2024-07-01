import os
import json
import datetime
from PyQt5.QtWidgets import QLineEdit, QDateEdit, QPushButton, QFileDialog, QFormLayout, QLabel, QDialog, QTextEdit
from PyQt5.QtGui import QPixmap

class EventWindow(QDialog):
    def __init__(self, event_data, file_path, parent=None):
        super(EventWindow, self).__init__(parent)
        self.setWindowTitle(event_data['name'])
        self.setGeometry(200, 200, 400, 300)
        self.event_data = event_data
        self.file_path = file_path

        layout = QFormLayout()
        self.setLayout(layout)

        self.name_label = QLabel("Event Name:")
        self.name_text = QLineEdit(event_data['name'])
        self.name_text.textChanged.connect(self.save_changes)
        layout.addRow(self.name_label, self.name_text)

        self.date_label = QLabel("Event Date:")
        self.date_text = QDateEdit(self)
        event_date = datetime.date(event_data['date'][2], event_data['date'][0], event_data['date'][1])
        self.date_text.setDate(event_date)
        self.date_text.dateChanged.connect(self.save_changes)
        layout.addRow(self.date_label, self.date_text)

        self.description_label = QLabel("Description:")
        self.description_text = QTextEdit(event_data['description'])
        self.description_text.textChanged.connect(self.save_changes)
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
            self.image_view.setPixmap(pixmap.scaled(300, 200, aspectRatioMode=1))
        else:
            self.image_view.setText("No image available")

    def save_changes(self):
        self.event_data['name'] = self.name_text.text()
        self.event_data['date'] = [
            self.date_text.date().month(),
            self.date_text.date().day(),
            self.date_text.date().year()
        ]
        self.event_data['description'] = self.description_text.toPlainText()

        try:
            with open(self.file_path, 'r') as json_file:
                json_data = json.load(json_file)
            for event in json_data['events']:
                if event['name'] == self.event_data['name']:
                    event.update(self.event_data)
                    break
            with open(self.file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)
        except Exception as e:
            print(f"Error saving event data: {e}")

    def change_image(self):
        # Set the initial directory to the "images" subdirectory
        initial_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
        if not os.path.exists(initial_dir):
            os.makedirs(initial_dir)

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", initial_dir, "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        
        # Make sure the selected file is within the initial directory
        if file_path and os.path.commonpath([initial_dir, file_path]) == initial_dir:
            self.event_data['images'] = [file_path]
            pixmap = QPixmap(file_path)
            self.image_view.setPixmap(pixmap.scaled(300, 200, aspectRatioMode=1))
            self.save_changes()
        else:
            print("Selected file is not within the allowed directory.")