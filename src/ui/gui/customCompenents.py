from PyQt5.QtCore import QSize, QPointF, Qt
from PyQt5.QtGui import QRegion, QIcon, QPixmap, QColor, QPen, QPainter
from PyQt5.QtWidgets import QPushButton

class RoundCirclePushPushButton(QPushButton):
    def __init__(self):  #, __args):
        super(RoundCirclePushPushButton, self).__init__()  #, __args)

        map1 = QPixmap(101, 101)
        map1.fill(QColor('red'))  # Any dummy color
        color = QColor('blue')
        pen_thickness = 10
        pen = QPen(color)
        pen.setWidth(pen_thickness)
        painter = QPainter(map1)
        # painter.begin(map1)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(50, 50), 100 / 2 - pen_thickness, 100 / 2 - pen_thickness)
        mask = map1.createMaskFromColor(color, mode=Qt.MaskOutColor)
        painter.end()
        map1.setMask(mask)

        self.setMinimumSize(100, 100)
        self.setMaximumSize(100, 100)
        self.setStyleSheet('background-color:transparent;')
        # self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)  # For Translucent Window
        # TODO Try to clear QWidget::DrawWindowBackground if you call render()
        self.setIcon(QIcon(map1))
        self.setIconSize(QSize(100, 100))
        r4 = QRegion(0 + 5, 0 + 5, 100 - (5 * 2), 100 - (5 * 2), type=QRegion.Ellipse)
        self.setMask(r4)
        # self.clicked.connect(clicked)


