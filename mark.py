from PyQt6 import QtGui


class Mark:
    xmin = None
    xmax = None
    color = None

    @staticmethod
    def get_alpha():
        return 0.5

    def __init__(self, xmin, xmax, color: QtGui.QColor):
        if xmin > xmax:
            raise Exception("xmin > xmax")
        self.xmin = xmin
        self.xmax = xmax
        self.color = color