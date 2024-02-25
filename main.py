import random
import sys
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from PyQt6 import QtWidgets, QtCore

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
from matplotlib.backend_bases import MouseButton

from ui.main_window import Ui_MainWindow
from settings import SettingsEditDialog

matplotlib.use('QT5Agg')


class ItemsModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._data = np.empty(shape=0)
        self.headers = {}

    def set_items(self, items):
        self.beginResetModel()
        self._data = items
        self.endResetModel()

    def set_headers(self, headers):
        self.beginResetModel()
        self.headers = headers
        self.endResetModel()

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
            # info = self.dataset[index.row()]
            # col = index.column()
            # return f'{info[col]}'
            value = self._data[index.row(), index.column()]
            return str(value)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self.headers.get(section)


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.csv_delimiter = ';'
        self.csv_accuracy = 4

        self.horizontalLayout_1 = QtWidgets.QHBoxLayout(self.ui.plotFrame)
        self.horizontalLayout_1.setObjectName("horizontalLayout_1")
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.horizontalLayout_1.addWidget(self.canvas)

        self.ui.menuActionOpen_h5.triggered.connect(self.on_btnOpenH5File_click)
        self.ui.menuActionSave_csv.triggered.connect(self.on_btnSaveCvsFile_click)
        self.ui.menuActionEditSettings.triggered.connect(self.on_btnEditSettings_click)

        self.model = ItemsModel()
        self.lastTblItemsItemClicked = None
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self.setWindowTitle("h5 visualizer")
        self.update_plot()

    def update_plot(self):
        data = self.model._data
        if data.shape and data.shape[0]:
            if len(data.shape) == 2:
                cols = data.shape[1]
                for i in range(1, cols):
                    plt.plot(data[:, 0], data[:, i], label=self.model.headers[i])

            plt.grid(True, color="grey", linewidth="0.4", linestyle="-.")
            plt.legend()
            self.canvas.draw()

    def on_btnOpenH5File_click(self):
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите файл", filter="h5 (*.h5);;hdf5  (*.hdf5)")

        if file and file[0]:
            with h5py.File(file[0], "r") as f:
                a_group_key = list(f.keys())[0]

                ds_arr = np.array(f[a_group_key][:])
                names = ds_arr.dtype.names
                dict_names = {k: v for k, v in enumerate(names)}

                rows = ds_arr.shape[0]
                cols = len(names)
                float_arr = np.empty(shape=(rows, cols))

                for i in range(rows):
                    arr = np.asarray(list(map(float, ds_arr[i])), dtype='float64')
                    float_arr[i] = arr

                np.around(float_arr, 4, out=float_arr)
                self.model.set_headers(dict_names)
                self.model.set_items(float_arr)
                self.update_plot()

    def on_btnSaveCvsFile_click(self):
        try:
            file = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить файл', 'data', "csv (*.csv)")
            if file and file[0]:
                names = list(self.model.headers.values())
                np.savetxt(file[0], names, newline=self.csv_delimiter, fmt="%s")
                with open(file[0], 'ab') as f:
                    np.savetxt(f, [''], delimiter=self.csv_delimiter, fmt="%s")
                    np.savetxt(f, self.model._data, delimiter=self.csv_delimiter, fmt=f"%.{self.csv_accuracy}f")
                QtWidgets.QMessageBox.about(self, "Save csv", "Данные успешно сохранены в файл: " + file[0])
            else:
                raise Exception("Данные не сохранены в файл")
        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка сохранения в файл", str(ex))

    def on_btnEditSettings_click(self):
        dialog = SettingsEditDialog(self.csv_delimiter, self.csv_accuracy)
        result = dialog.exec()
        if result == 0:
            return

        data = dialog.get_data()
        if data['csv_accuracy']:
            self.csv_delimiter = data['csv_delimiter']

        if data['csv_accuracy']:
            try:
                self.csv_accuracy = int(float(data['csv_accuracy']))
            except:
                pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
