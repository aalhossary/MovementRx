
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QPointF, Qt
from PyQt5.QtGui import QRegion, QIcon, QPixmap, QColor, QPen, QPainter, QBitmap
from PyQt5.QtWidgets import QPushButton


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
        # TODO Try to clear QWidget::DrawWindowBackground if you call render()
        # self.setIcon(self.ring_icon)
        self.setIcon(self.__class__._empty_icon)
        self.setIconSize(QSize(100, 100))
        r4 = QRegion(0 + 5, 0 + 5, 100 - (5 * 2), 100 - (5 * 2), type=QRegion.Ellipse)
        self.setMask(r4)
        self.setCheckable(True)
        # self.clicked.connect(clicked)
        self.clicked['bool'].connect(self.setChecked)
        self.setMouseTracking(True)


    @classmethod
    def get_icons(cls):
        if not cls._unchecked_icon:
            unchecked_pixmap = cls.create_ring_Pixmap(ring_color='yellow')
            checked_pixmap = cls.create_ring_Pixmap(ring_color='green')

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
    def create_ring_Pixmap(ring_color) -> QPixmap:
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
