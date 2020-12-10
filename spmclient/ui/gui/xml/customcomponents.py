from __future__ import annotations
from typing import cast, Optional

from PyQt5 import QtCore
from PyQt5.Qt import QLabel
from PyQt5.QtCore import QSize, QPointF, Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QRegion, QIcon, QPixmap, QColor, QPen, QPainter, QBitmap
from PyQt5.QtWidgets import QPushButton, QWidget, QSlider
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.axes._axes import Axes
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D


class AnalysisLabel(QLabel):

    def __init__(self, parent=None, *args, **kwargs):
        super(AnalysisLabel, self).__init__(parent=parent, *args, **kwargs)

        self.analysis_name = ''
        self.selected_widget_name = ''

    def get_analysis_name(self):
        return self.__analysis_name

    def get_selected_widget_name(self):
        return self.__selected_widget_name

    @pyqtSlot(str)
    def set_analysis_name(self, value):
        self.__analysis_name = value
        self.update_text()

    @pyqtSlot(str)
    def set_selected_widget_name(self, value):
        self.__selected_widget_name = value
        self.update_text()

    def del_analysis_name(self):
        del self.__analysis_name

    def del_selected_widget_name(self):
        del self.__selected_widget_name

    analysis_name = property(get_analysis_name, set_analysis_name, del_analysis_name, "analysis_name's docstring")
    selected_widget_name = property(get_selected_widget_name, set_selected_widget_name, del_selected_widget_name,
                                    "selected_widget_name's docstring")

    def update_text(self):
        text = ['<html><head/><body>']
        try:
            if self.analysis_name:
                text.append(f'<p><span style=" font-weight:600;">{self.analysis_name}</span></p>')
            #         except AttributeError:
            #             pass
            #         try:
            if self.selected_widget_name:
                text.append(f'<p><span style=" font-weight:600;">{self.selected_widget_name}{{t}}</span></p>')
        except AttributeError:
            pass
        text.append(
            '<p><span style=" font-weight:600;">Colorbar{T</span><span style=" font-weight:600; vertical-align:super;">2</span><span style=" font-weight:600;">}</span>')
        text.append('</p></body></html>')

        self.setText(''.join(text))


class Scaler:
    def scale(self, index_in_cycle: int) -> Optional[int]:
        pass


class MomentsScaler(Scaler):
    """A [0, 60] to [0, 100] scale adaptor."""
    def scale(self, index_in_cycle: int) -> Optional[int]:
        if 0 <= index_in_cycle <= 60:
            return int(index_in_cycle * 100 / 60)
        else:
            return None


class KinematicsScaler(Scaler):
    """A [0, 100] to [0, 100] scale adaptor."""
    def scale(self, index_in_cycle: int) -> Optional[int]:
        if 0 <= index_in_cycle <= 100:
            return index_in_cycle
        else:
            return None


class MplCanvas(QWidget):  # FigureCanvasQTAgg):

    def __init__(self, parent=None, *args, **kwargs):
        # def __init__(self, *args):
        #     super(QWidget, self).__init__(*args)
        #     super(FigureCanvasQTAgg, self).__init__(self.figure)

        QWidget.__init__(self, parent=parent)
        # plt.rcParams['figure.constrained_layout.use'] = True
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        # ax = self.figure.add_subplot(111)
        gridspec = self.figure.add_gridspec(nrows=1, ncols=1, top=0.99, bottom=0.01, right=0.99)
        ax = self.figure.add_subplot(gridspec[0, 0])
        self.ax: Axes = cast(Axes, ax)
        self.ax.xaxis.set_visible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.moving_line: Optional[Line2D] = None

    def animate_line(self, scaler: Scaler, index_in_cycle:int, color: str):
        scaled = scaler.scale(index_in_cycle)
        if scaled is None:
            if self.moving_line:
                self.moving_line.remove()
                self.moving_line = None
        else:
            if self.moving_line is None:
                self.moving_line = self.ax.axvline(x=scaled, linewidth=4, color=color, ls='-', lw=1.5)
            else:
                self.moving_line.set_xdata([scaled, scaled])
                self.canvas.draw()


class HeatMapMplCanvas(MplCanvas):
    def __init__(self, parent=None, *args, **kwargs):
        MplCanvas.__init__(self, parent=parent, *args, **kwargs)
        self.ax.get_yaxis().set_visible(False)
        self.ax.get_gridspec().update(right=0.0)
        self.canvas.draw()
        self.update()
        # TODO make sure the update geometry works. Till now, I just hide the Y Axis


class LegendMplCanvas(MplCanvas):
    def update_legend(self):
        # TODO use it to draw the legend later
        pass


class RoundCirclePushButton(QPushButton):

    _unchecked_icon = None
    _checked_icon = None
    _empty_icon = None

    def __init__(self, __args):
        super(RoundCirclePushButton, self).__init__(__args)
        # super(RoundCirclePushPushButton, self).__init__()  #, __args)
        # unchecked_icon, checked_icon, empty_icon = self.__class__.get_icons()
        self.__class__.get_icons()

        self.setMinimumSize(100, 100)
        self.setMaximumSize(100, 100)
        self.setStyleSheet('background-color:transparent;')
        # self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)  # For Translucent Window
        # TODO Try to clear QWidget::DrawWindowBackground if you call/ override render()
        # self.setIcon(self.ring_icon)
        self.setIcon(self.__class__._empty_icon)
        self.setIconSize(QSize(100, 100))
        r4 = QRegion(0 + 5, 0 + 5, 100 - (5 * 2), 100 - (5 * 2), type=QRegion.Ellipse)
        self.setMask(r4)
        self.setCheckable(True)
        # self.clicked.connect(clicked)
        self.clicked['bool'].connect(self.setChecked)
        self.setMouseTracking(True)

    # def render(self, target: QtGui.QPaintDevice, targetOffset: QtCore.QPoint = ..., sourceRegion: QtGui.QRegion = ...,
    #            flags: typing.Union['QWidget.RenderFlags', 'QWidget.RenderFlag'] = ...) -> None:
    #     flags = flags & ~ QWidget.DrawWindowBackground
    #     super(RoundCirclePushButton, self).render(target, targetOffset, sourceRegion, flags)

    @classmethod
    def get_icons(cls):
        if not cls._unchecked_icon:
            unchecked_pixmap = cls.create_ring_pixmap(ring_color='yellow')
            checked_pixmap = cls.create_ring_pixmap(ring_color='green')

            cls._unchecked_icon = QIcon(unchecked_pixmap)
            cls._checked_icon = QIcon(checked_pixmap)
            # TODO is there a better way to do this?
            empty_map = QPixmap(unchecked_pixmap.size())
            empty_mask = QBitmap(empty_map)
            empty_mask.clear()
            empty_map.setMask(empty_mask)
            cls._empty_icon = QIcon(empty_map)

        return cls._unchecked_icon, cls._checked_icon, cls._empty_icon

    @staticmethod
    def create_ring_pixmap(ring_color) -> QPixmap:
        ring_map = QPixmap(101, 101)
        ring_map.fill(QColor('red'))  # Any dummy color just to see
        color = QColor(ring_color)
        pen_thickness = 10
        pen = QPen(color)
        pen.setWidth(pen_thickness)
        painter = QPainter(ring_map)
        # painter.begin(ring_map)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(50, 50), 100 / 2 - pen_thickness, 100 / 2 - pen_thickness)
        mask = ring_map.createMaskFromColor(color, mode=Qt.MaskOutColor)
        painter.end()
        ring_map.setMask(mask)
        return ring_map

    def enterEvent(self, _: QtCore.QEvent) -> None:
        # print("Enter", a0.type())
        if self.isChecked():
            self.setIcon(self._checked_icon)
        else:
            self.setIcon(self._unchecked_icon)

    def leaveEvent(self, _: QtCore.QEvent) -> None:
        # print("leave", a0.type())
        if self.isChecked():
            self.setIcon(self._checked_icon)
        else:
            self.setIcon(self._empty_icon)

    def setChecked(self, checked: bool) -> None:
        super(RoundCirclePushButton, self).setChecked(checked)

        print("changing icon state to Checked =", checked)
        if checked:
            self.setIcon(self._checked_icon)
        else:
            self.setIcon(self._unchecked_icon)
        # TODO do the show / hide effect


class MyQSlider(QSlider):
    """
    Logical_XXX fields are for what I send to the slider, while minimum, maximum, and value are what users see.
    """

    logical_value = 0

    ratio = 1
    handle_on = True

#     def setLogicalRange(self, min: int, max: int) -> None:
#         self.logical_minimum = min
#         self.logical_maximum = max
#         self.ratio = (self.maximum() - self.minimum()) / (max - min)

#     def translate(self, logical_val: int) -> int:
#         return int((logical_val - self.logical_minimum) * self.ratio + self.minimum())

    def logicalValue(self) -> int:
        return self.logical_value

    def setLogicalValue(self, scaler: Scaler, val: int, side: str) -> None:
        self.logical_value = val

        scaled = scaler.scale(val)
        if scaled is None:
            print(f'{side}\t{val}\t{scaled}\t1')
            if self.handle_on:
                self.setStyleSheet(
                    "QSlider::groove:horizontal {\n"
                    "    border: 1px solid #a0a0a0; /*  off;*/\n"
                    "    background-color: off;\n"
                    "    height: 3px; /* 0px;*/\n"
                    "    margin: 0px 0px;\n"
                    "}\n"
                    "QSlider::handle off;"
                )
                self.handle_on = False
        else:
            self.setValue(scaled)
            # TODO simplify this IF THEN ELSE structure
            if self.handle_on:
                print(f'{side}\t{val}\t{scaled}\t21')
                self.setStyleSheet(
                    "QSlider::groove:horizontal {\n"
                    "    border: 1px solid #a0a0a0; /*  off;*/\n"
                    "    background-color: off;\n"
                    "    height: 3px; /* 0px;*/\n"
                    "    margin: 0px 0px;\n"
                    "}\n"
                    "QSlider::handle {\n"
                    "    background: off;\n"
                    "    border: off;\n"
                    "    width: 40px;\n"
                    "}\n"
                    "QSlider::handle:horizontal {\n"
                    "    margin: -40px 0px;\n"
                    f"    image: url(\":/walker{side[0]}/res/StepImages/{side}/{val // 5}.png\")\n"
                    "}")
            else:
                print(f'{side}\t{val}\t{scaled}\t22')
                self.setStyleSheet(
                    "QSlider::groove:horizontal {\n"
                    "    border: 1px solid #a0a0a0; /*  off;*/\n"
                    "    background-color: off;\n"
                    "    height: 3px; /* 0px;*/\n"
                    "    margin: 0px 0px;\n"
                    "}\n"
                    "QSlider::handle {\n"
                    "    background: off;\n"
                    "    border: off;\n"
                    "    width: 40px;\n"
                    "}\n"
                    "QSlider::handle:horizontal {\n"
                    "    margin: -40px 0px;\n"
                    f"    image: url(\":/walker{side[0]}/res/StepImages/{side}/{val // 5}.png\")\n"
                    "}")
            self.handle_on = True
        
