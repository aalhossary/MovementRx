# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui_colormap_chooser.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_colorMapPicker(object):
    def setupUi(self, colorMapPicker):
        colorMapPicker.setObjectName("colorMapPicker")
        colorMapPicker.resize(437, 300)
        self.gridLayout = QtWidgets.QGridLayout(colorMapPicker)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox = QtWidgets.QCheckBox(colorMapPicker)
        self.checkBox.setEnabled(False)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(colorMapPicker)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.spinBox = QtWidgets.QSpinBox(colorMapPicker)
        self.spinBox.setMinimum(3)
        self.spinBox.setMaximum(20)
        self.spinBox.setProperty("value", 4)
        self.spinBox.setObjectName("spinBox")
        self.verticalLayout.addWidget(self.spinBox)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem1)
        self.label_2 = QtWidgets.QLabel(colorMapPicker)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.comboBox = QtWidgets.QComboBox(colorMapPicker)
        self.comboBox.setCurrentText("Jet")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.verticalLayout.addWidget(self.comboBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(colorMapPicker)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(colorMapPicker)
        self.comboBox.setCurrentIndex(0)
        self.buttonBox.accepted.connect(colorMapPicker.accept)
        self.buttonBox.rejected.connect(colorMapPicker.reject)
        QtCore.QMetaObject.connectSlotsByName(colorMapPicker)

    def retranslateUi(self, colorMapPicker):
        _translate = QtCore.QCoreApplication.translate
        colorMapPicker.setWindowTitle(_translate("colorMapPicker", "Colormap Options"))
        self.checkBox.setText(_translate("colorMapPicker", "Different colors for positive and negative values"))
        self.label.setText(_translate("colorMapPicker", "Number of levels"))
        self.label_2.setText(_translate("colorMapPicker", "Colormap Name"))
        self.comboBox.setItemText(0, _translate("colorMapPicker", "Jet"))
        self.comboBox.setItemText(1, _translate("colorMapPicker", "Coolhot"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    colorMapPicker = QtWidgets.QDialog()
    ui = Ui_colorMapPicker()
    ui.setupUi(colorMapPicker)
    colorMapPicker.show()
    sys.exit(app.exec_())

