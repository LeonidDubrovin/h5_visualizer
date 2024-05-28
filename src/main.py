import random
import sys
import h5py
import numpy as np
from PyQt6 import QtWidgets, QtGui

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib

from ui.main_window import Ui_MainWindow
from edit_settings import SettingsEditDialog
from edit_mark import MarkEditDialog
from mark import Mark
from table_marks_model import TableMarksModel
from table_data_model import TableDataModel
from plot_model import MyPlot, GraphTypes


matplotlib.use('QT5Agg')


class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.csv_delimiter = ';'
        self._csv_accuracy = 4
        self._selected_graph_type: GraphTypes = GraphTypes.plot

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

        graph_types = [dt.value for dt in GraphTypes]
        self.ui.comboBoxScatterPlot.addItems(graph_types)
        self.ui.comboBoxScatterPlot.currentIndexChanged.connect(self.onChangedComboBoxScatterPlot)

        self.draw_graphic()

    def update_app(self):
        self._table_marks.delete_marks()
        self.draw_graphic()

    def draw_graphic(self):
        try:
            data = self._table_data.get_data()
            if data.size and data.shape and data.shape[0]:
                self._my_plot.draw_plot(data=data,
                                        headers=self._table_data.get_headers(),
                                        marks=self._table_marks.get_marks(),
                                        graph_type=self._selected_graph_type)
        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка выбора типа графика: ", str(ex))

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
                names.append('mark color')
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
                color = QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                color.setAlphaF(Mark.get_alpha())
                tmp_mark = Mark(xmin=xmin, xmax=xmax, color=color)

                if self._table_marks.have_collisions(tmp_mark):
                    raise Exception("Метка включает в себя другие метки")

                dialog = MarkEditDialog(tmp_mark)
                err = dialog.exec()
                if err == 0:
                    return

                mark = dialog.get_mark()

                if self._table_marks.have_collisions(mark):
                    raise Exception("Метка включает в себя другие метки")

                self._my_plot.clear_xmin_xmax()

                self._table_marks.add_mark(mark)
                self._table_data.update_marked_rows(self._table_marks.get_marks())
                self._my_plot.draw_plot(data=self._table_data.get_data(),
                                        headers=self._table_data.get_headers(),
                                        marks=self._table_marks.get_marks(),
                                        graph_type=self._selected_graph_type)

        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка добавления метки: ", str(ex))

    def on_btnEditMark_click(self):
        try:
            item = self.ui.tableViewMarks.currentIndex()
            mark = self._table_marks.get_mark(item.row())
            dialog = MarkEditDialog(mark)
            err = dialog.exec()
            if err == 0:
                return

            edited_mark = dialog.get_mark()

            if edited_mark.xmin:
                mark.xmin = edited_mark.xmin
            if edited_mark.xmax:
                mark.xmax = edited_mark.xmax
            if edited_mark.color:
                mark.color = edited_mark.color

            self._my_plot.update_plot(marks=self._table_marks.get_marks())
            self._table_data.update_marked_rows(self._table_marks.get_marks())

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
                                        marks=self._table_marks.get_marks(),
                                        graph_type=self._selected_graph_type)
        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка удаления метки: ", str(ex))

    def onChangedComboBoxScatterPlot(self, idx):
        try:
            for gt in GraphTypes:
                if gt.value == self.ui.comboBoxScatterPlot.currentText():
                    self._selected_graph_type = gt
                    self._my_plot.draw_plot(data=self._table_data.get_data(),
                                            headers=self._table_data.get_headers(),
                                            marks=self._table_marks.get_marks(),
                                            graph_type=gt)
        except Exception as ex:
            QtWidgets.QMessageBox.about(self, "Ошибка выбора типа графика: ", str(ex))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
