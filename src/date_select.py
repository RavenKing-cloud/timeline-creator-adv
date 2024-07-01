import datetime
from PyQt5.QtWidgets import QVBoxLayout, QDateEdit, QDialog, QVBoxLayout, QDialogButtonBox

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