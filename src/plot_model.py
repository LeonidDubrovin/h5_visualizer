import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.widgets import RectangleSelector, SpanSelector
from matplotlib.backend_bases import MouseButton

from pan_and_zoom import PanAndZoom
from mark import Mark


# GraphTypes = Enum('Scatter', 'Plot')
class GraphTypes(Enum):
    scatter = 'Scatter'
    plot = 'Plot'


class MyPlot:
    _canvas = None
    _static_ax = None
    _current_xmin = None
    _current_xmax = None

    _span_marks_list = []

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

    def add_span_mark(self, mark: Mark):
        span = self._static_ax.axvspan(xmin=mark.xmin, xmax=mark.xmax, facecolor=mark.color.name(), alpha=mark.color.alphaF())
        self._span_marks_list.append(span)

    def remove_span_marks(self):
        for span in self._span_marks_list:
            span.remove()
        self._span_marks_list.clear()

    def draw_plot(self, data: np.array, headers: dict, marks, graph_type: GraphTypes):
        self._static_ax.cla()

        if len(data.shape) == 2:
            cols = data.shape[1]
            for i in range(1, cols):
                if graph_type == GraphTypes.scatter:
                    self._static_ax.scatter(data[:, 0], data[:, i], label=headers[i])
                elif graph_type == GraphTypes.plot:
                    self._static_ax.plot(data[:, 0], data[:, i], label=headers[i])
                else:
                    raise Exception("Unknown graph type: ", graph_type.value)

        self._static_ax.grid(True, color="grey", linewidth="0.4", linestyle="-.")
        self._static_ax.legend()
        if headers:
            plt.xlabel(headers[0])

        toggle_selector = self.get_selector(self._static_ax)
        plt.connect('key_press_event', toggle_selector)

        for mark in marks:
            self.add_span_mark(mark)

        self._canvas.draw()

    def update_plot(self, marks):
        self.remove_span_marks()

        for mark in marks:
            self.add_span_mark(mark)

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