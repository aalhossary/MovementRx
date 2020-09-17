from typing import cast

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.axes._axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(QWidget):  # FigureCanvasQTAgg):

    def __init__(self, parent=None, *args, **kwargs):
        # def __init__(self, *args):
        #     super(QWidget, self).__init__(*args)
        #     super(FigureCanvasQTAgg, self).__init__(self.figure)

        QWidget.__init__(self, parent=parent)
        # plt.rcParams['figure.constrained_layout.use'] = True
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        ax = self.figure.add_subplot(111)
        self.ax: Axes = cast(Axes, ax)
