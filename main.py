import random
import sys
import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from PyQt6 import QtWidgets, QtCore, QtGui

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import RectangleSelector, SpanSelector
import matplotlib
from matplotlib.backend_bases import MouseButton

from ui.main_window import Ui_MainWindow
from settings_edit import SettingsEditDialog
from mark_edit import MarkEditDialog
from pan_and_zoom import PanAndZoom

matplotlib.use('QT5Agg')


class TableDataModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._data = np.empty(shape=0)
        self._headers = {}
        self._marked_rows = []

    def get_data(self) -> np.ndarray:
        return self._data

    def get_marked_data_for_save(self):
        mark_arr = np.array([np.array(['x' if val else ' ']) for val in self._marked_rows])
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
        self._marked_rows = [False] * self._data.shape[0]
        for mark in marks:
            for idx, row_arr in enumerate(self._data):
                if mark.xmin <= row_arr[0] <= mark.xmax:
                    self._marked_rows[idx] = True

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
            if self._marked_rows[index.row()]:
                bgColor = QtGui.QColor(255, 0, 0, 127)
                return QtCore.QVariant(QtGui.QColor(bgColor))

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self._headers.get(section)


class Mark:
    xmin = None
    xmax = None
    color = None

    def __init__(self, xmin, xmax):
        self.xmin = xmin
        self.xmax = xmax


class TableMarksModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._marks = np.empty(shape=0)

    def get_marks(self):
        return self._marks

    def set_marks(self, marks):
        self.beginResetModel()
        self._marks = marks
        self.endResetModel()

    def add_mark(self, mark: Mark):
        self.beginResetModel()
        self._marks = np.append(self._marks, mark)
        self.endResetModel()

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

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return "Метки"


class MyPlot:
    _canvas = None
    _static_ax = None
    _current_xmin = None
    _current_xmax = None

    _span_marks = None

    def __init__(self):
        fig = plt.figure()
        fig.pan_zoom = PanAndZoom(fig)
        self._canvas = FigureCanvas(fig)
        self._static_ax = self._canvas.figure.subplots()

    def get_canvas(self):
        return self._canvas

    def get_ax(self):
        return self._static_ax

    def get_xmin_xmax(self):
        return self._current_xmin, self._current_xmax

    @staticmethod
    def clear_xmin_xmax():
        MyPlot._current_xmin = None
        MyPlot._current_xmax = None

    def add_span_mark(self, xmin: float, xmax: float):
        self._static_ax.axvspan(xmin=xmin, xmax=xmax, facecolor='0.5', alpha=0.5)

    def draw_plot(self, data: np.array, headers: dict, marks):
        self._static_ax.cla()

        if len(data.shape) == 2:
            cols = data.shape[1]
            for i in range(1, cols):
                # scatter or plot
                self._static_ax.scatter(data[:, 0], data[:, i], label=headers[i])

        self._static_ax.grid(True, color="grey", linewidth="0.4", linestyle="-.")
        self._static_ax.legend()
        plt.xlabel(headers[0])

        toggle_selector = self.get_selector(self._static_ax)
        plt.connect('key_press_event', toggle_selector)

        for mark in marks:
            self.add_span_mark(mark.xmin, mark.xmax)

        self._canvas.draw()

    @staticmethod
    def deactivate_selector():
        MyPlot._current_xmin = None
        MyPlot._current_xmax = None
        MyPlot.toggle_selector.SS.clear()

    @staticmethod
    def get_selector(ax):
        MyPlot.toggle_selector.SS = SpanSelector(ax, MyPlot.line_select_callback,
                                                 "horizontal",
                                                 button=[MouseButton.LEFT],
                                                 useblit=True,
                                                 props=dict(alpha=0.5, facecolor="tab:blue"),
                                                 interactive=True,
                                                 drag_from_anywhere=True)
        return MyPlot.toggle_selector

    @staticmethod
    def line_select_callback(xmin, xmax):
        print("xmin, xmax: ", xmin, xmax)
        MyPlot._current_xmin = xmin
        MyPlot._current_xmax = xmax

    @staticmethod
    def toggle_selector(event):
        print(' Key pressed.')


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.csv_delimiter = ';'
        self._csv_accuracy = 4

        self.verticalLayout_1 = QtWidgets.QVBoxLayout(self.ui.plotFrame)
        self.verticalLayout_1.setObjectName("horizontalLayout_1")

        self._my_plot = MyPlot()
        self.verticalLayout_1.addWidget(NavigationToolbar(self._my_plot.get_canvas(), self))
        self.verticalLayout_1.addWidget(self._my_plot.get_canvas())

        self.ui.menuActionOpen_h5.triggered.connect(self.on_btnOpenH5File_click)
        self.ui.menuActionSave_csv.triggered.connect(self.on_btnSaveCvsFile_click)
        self.ui.menuActionEditSettings.triggered.connect(self.on_btnEditSettings_click)
        self.ui.btnAddMark.clicked.connect(self.on_btnAddMark_click)
        self.ui.btnEditMark.clicked.connect(self.on_btnEditMark_click)
        self.ui.btnDeleteMark.clicked.connect(self.on_btnDeleteMark_click)

        self._table_data = TableDataModel()
        self.ui.tableViewData.setModel(self._table_data)
        self.ui.tableViewData.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        self._table_marks = TableMarksModel()
        self.ui.tableViewMarks.setModel(self._table_marks)
        self.ui.tableViewMarks.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.setWindowTitle("h5 visualizer")
        self.draw_graphic()

    def update_app(self):
        self._table_marks.delete_marks()
        self.draw_graphic()

    def draw_graphic(self):
        data = self._table_data.get_data()
        if data.size and data.shape and data.shape[0]:
            self._my_plot.draw_plot(data=data,
                                    headers=self._table_data.get_headers(),
                                    marks=self._table_marks.get_marks())

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

                res_arr = np.around(float_arr, self._csv_accuracy)
                self._table_data.set_headers(dict_names)
                self._table_data.set_items(res_arr)

                self.update_app()

    def on_btnSaveCvsFile_click(self):
        try:
            file = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить файл', 'data', "csv (*.csv)")
            if file and file[0]:
                res_data = self._table_data.get_marked_data_for_save()

                names = list(self._table_data.get_headers().values())
                np.savetxt(file[0], names, newline=self.csv_delimiter, fmt="%s")
                with open(file[0], 'ab') as f:
                    np.savetxt(f, [''], delimiter=self.csv_delimiter, fmt="%s")
                    np.savetxt(f, res_data, delimiter=self.csv_delimiter, fmt="%s")
                QtWidgets.QMessageBox.about(self, "Save csv", "Данные успешно сохранены в файл: " + file[0])
            else:
                raise Exception("Данные не сохранены в файл")
        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка сохранения в файл: ", str(ex))

    def on_btnEditSettings_click(self):
        dialog = SettingsEditDialog(self.csv_delimiter, self._csv_accuracy)
        result = dialog.exec()
        if result == 0:
            return

        data = dialog.get_data()
        if data['csv_delimiter']:
            self.csv_delimiter = data['csv_delimiter']

        if data['csv_accuracy']:
            try:
                self._csv_accuracy = int(float(data['csv_accuracy']))
                self._table_data.around_data(self._csv_accuracy)
            except:
                pass

    def on_btnAddMark_click(self):
        try:
            xmin, xmax = self._my_plot.get_xmin_xmax()
            if xmin and xmax:
                self._my_plot.clear_xmin_xmax()
                self._table_marks.add_mark(Mark(xmin=xmin, xmax=xmax))
                self._table_data.update_marked_rows(self._table_marks.get_marks())
                self._my_plot.draw_plot(data=self._table_data.get_data(),
                                        headers=self._table_data.get_headers(),
                                        marks=self._table_marks.get_marks())
        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка добавления метки: ", str(ex))

    def on_btnEditMark_click(self):
        try:
            item = self.ui.tableViewMarks.currentIndex()
            mark = self._table_marks.get_marks()[item.row()]
            dialog = MarkEditDialog(mark.xmin, mark.xmax)
            err = dialog.exec()
            if err == 0:
                return

            data = dialog.get_data()
        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка мзменения метки: ", str(ex))

    def on_btnDeleteMark_click(self):
        try:
            item = self.ui.tableViewMarks.currentIndex()
            if item.isValid():
                self._table_marks.delete_mark(item)
                self._table_data.update_marked_rows(self._table_marks.get_marks())
                self._my_plot.draw_plot(data=self._table_data.get_data(),
                                        headers=self._table_data.get_headers(),
                                    marks=self._table_marks.get_marks())
        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка удаления метки: ", str(ex))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
