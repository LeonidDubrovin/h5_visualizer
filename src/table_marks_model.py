import numpy as np

from PyQt6 import QtCore

from mark import Mark


class TableMarksModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._marks = np.empty(shape=0)

    def get_marks(self):
        return self._marks

    def get_mark(self, idx: int) -> Mark:
        return self._marks[idx]

    def set_marks(self, marks):
        self.beginResetModel()
        self._marks = marks
        self.endResetModel()

    def add_mark(self, mark: Mark):
        self.beginResetModel()
        self._marks = np.append(self._marks, mark)
        self.endResetModel()

    def have_collisions(self, new_mark: Mark) -> bool:
        result = False
        for mark in self._marks:
            if not (new_mark.xmax <= mark.xmin or mark.xmax <= new_mark.xmin):
                result = True
        return result

    def rowCount(self, *args, **kwargs) -> int:
        return len(self._marks)

    def columnCount(self, *args, **kwargs) -> int:
        # вывод в одну колонку
        return 1

    def delete_mark(self, item):
        self.set_marks(np.delete(self._marks, item.row()))

    def delete_marks(self):
        self.set_marks(np.empty(shape=0))

    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole):
        if not index.isValid():
            return

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            item = self._marks[index.row()]
            return "{0:0.2f}  |  ".format(item.xmin) + "{0:0.2f}".format(item.xmax)

        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            mark = self._marks[index.row()]
            return QtCore.QVariant(mark.color)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return "Метки"
