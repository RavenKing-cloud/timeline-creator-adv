import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QScrollArea
from PyQt5.QtGui import QPixmap
from src.render import *

# Install dependencies
install_pillow()
install_pyqt()

# PyQt Application Window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ONE-Liner - Timeline Editor')
        self.setGeometry(100, 100, 1400, 820)

        # Layout
        layout = QVBoxLayout()

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # QLabel to display the rendered image
        self.lbl_image = QLabel()
        scroll_area.setWidget(self.lbl_image)

        layout.addWidget(scroll_area)

        # Button to open file dialog
        self.btn_open = QPushButton('Open JSON File', self)
        self.btn_open.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.btn_open)

        self.setLayout(layout)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)", options=options)

        if file_path:
            # Render timeline based on selected JSON file path
            img_path = render_timeline(file_path)

            # Display the rendered image in QLabel
            pixmap = QPixmap(img_path)
            self.lbl_image.setPixmap(pixmap)
            self.lbl_image.setScaledContents(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())