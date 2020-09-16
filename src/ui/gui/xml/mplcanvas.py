import random
from typing import cast

from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import numpy as np

# class MplCanvas(FigureCanvasQTAgg):
#
#     def __init__(self, parent: QWidget, *args, **kwargs):
#     # def __init__(self, *args):
#     #     super(QWidget, self).__init__(*args)
#     #     super(FigureCanvasQTAgg, self).__init__(self.figure)
#
#         # QWidget.__init__(self, parent=parent)
#         self.figure = Figure()
#         FigureCanvasQTAgg.__init__(self, self.figure)
#
#         parent.xxxxxxxxxx
#         self.setLayout(layout)
#         self.ax = self.figure.add_subplot(111)
#         print("setup", self.figure, self.figure.axes, self.figure.subplots)
#         self.ax.plot(np.random.randn(10))
#         # self.canvas.draw()
#         # self.update()





class MplCanvas(QWidget):  # FigureCanvasQTAgg):

    # ax: plt.axes.Axes

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
        self.ax: matplotlib.axes.Axes = cast(Axes, ax)

        # print(self.figure, self.figure.axes)

        # self.ax.plot(np.random.randn(10))
        # self.canvas.draw()
        # self.update()
