from PyQt6 import QtWidgets, QtGui
from ui.edit_mark_dialog import Ui_Dialog

from mark import Mark


class MarkEditDialog(QtWidgets.QDialog):
    def __init__(self, mark: Mark, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self._color: QtGui.QColor = mark.color

        self.ui.btnEdit.clicked.connect(self.accept)
        self.ui.btnCancel.clicked.connect(self.reject)
        self.ui.btnColorPick.clicked.connect(self.color_picker)

        self.ui.txtXmin.setText(str(mark.xmin))
        self.ui.txtXmax.setText(str(mark.xmax))
        self.ui.frameColor.setStyleSheet("background-color: " + self._color.name())

    def get_mark(self) -> Mark:
        return Mark(xmin=float(self.ui.txtXmin.text()), xmax=float(self.ui.txtXmax.text()), color=self._color)

    def color_picker(self):
        color = QtWidgets.QColorDialog.getColor()
        color.setAlphaF(Mark.get_alpha())
        self._color = color
        self.ui.frameColor.setStyleSheet("background-color: " + self._color.name())


