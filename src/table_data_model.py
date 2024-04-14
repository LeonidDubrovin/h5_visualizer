import numpy as np

from PyQt6 import QtCore

from src.mark import Mark


class TableDataModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._data = np.empty(shape=0)
        self._headers = {}
        self._marked_rows: [Mark] = []

    def get_data(self) -> np.ndarray:
        return self._data

    def get_marked_data_for_save(self):
        mark_arr = np.array([np.array([mark.color.name() if mark else ' ']) for mark in self._marked_rows])
        data = self._data.astype(str)
        return np.hstack((data, mark_arr))

    def get_headers(self):
        return self._headers

    def get_marked_rows(self) -> list:
        return self._marked_rows

    def set_items(self, items):
        self.beginResetModel()
        self._data = items
        self.update_marked_rows(np.empty(shape=0))
        self.endResetModel()

    def set_headers(self, headers):
        self.beginResetModel()
        self._headers = headers
        self.endResetModel()

    def update_marked_rows(self, marks: np.ndarray):
        self.beginResetModel()
        self._marked_rows = [None] * self._data.shape[0]

        for idx, row_arr in enumerate(self._data):
            for mark in marks:
                if mark.xmin <= row_arr[0] <= mark.xmax:
                    self._marked_rows[idx] = mark
                    break

        self.endResetModel()

    def around_data(self, accuracy: int):
        np.around(self._data, accuracy, out=self._data)

    def rowCount(self, *args, **kwargs) -> int:
        return len(self._data)

    def columnCount(self, *args, **kwargs) -> int:
        if len(self._data) > 0:
            return len(self._data[0])
        return 0

    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole):
        if not index.isValid():
            return

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            value = self._data[index.row(), index.column()]
            return str(value)

        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            mark = self._marked_rows[index.row()]
            if mark:
                return QtCore.QVariant(mark.color)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._headers.get(section)
