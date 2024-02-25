from PyQt6 import QtWidgets
from ui.edit_settings_dialog import Ui_Dialog


class SettingsEditDialog(QtWidgets.QDialog):
    def __init__(self, csv_delimiter, csv_accuracy, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.btnAdd.clicked.connect(self.accept)
        self.ui.btnCancel.clicked.connect(self.reject)

        self.ui.txtCsvDelimeter.setText(csv_delimiter)
        self.ui.txtCsvAccuracy.setText(str(csv_accuracy))

    def get_data(self):
        return {
            "csv_delimiter": self.ui.txtCsvDelimeter.text(),
            "csv_accuracy": self.ui.txtCsvAccuracy.text(),
        }
