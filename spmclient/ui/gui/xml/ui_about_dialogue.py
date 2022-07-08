# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_about_dialogue.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(705, 539)
        self.gridLayout = QtWidgets.QGridLayout(About)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(About)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(About)
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap(":/logos/res/logos/ntu logo.png"))
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(About)
        self.label_7.setMaximumSize(QtCore.QSize(400, 200))
        self.label_7.setText("")
        self.label_7.setPixmap(QtGui.QPixmap(":/logos/res/logos/astar-logo.png"))
        self.label_7.setScaledContents(False)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 1, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(About)
        self.label_9.setText("")
        self.label_9.setPixmap(QtGui.QPixmap(":/logos/res/logos/NHG-Logo_NoBg.png"))
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 2, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(About)
        self.label_5.setPixmap(QtGui.QPixmap(":/logos/res/logos/Kyoto Uni logo.png"))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 1, 1, 1)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "Dialog"))
        self.label.setText(_translate("About", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">MovementRx 0.4.1</span></p><p align=\"center\"><span style=\" font-size:10pt;\">Developped in </span><a href=\"http://rris.ntu.edu.sg/\"><span style=\" font-size:10pt; text-decoration: underline; color:#0000ff;\">Rehabilitation Research Institute of Singapore (RRIS)</span></a></p><p align=\"center\"><span style=\" font-size:10pt;\">Application credit goes to</span></p></body></html>"))

from spmclient import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    About = QtWidgets.QDialog()
    ui = Ui_About()
    ui.setupUi(About)
    About.show()
    sys.exit(app.exec_())

