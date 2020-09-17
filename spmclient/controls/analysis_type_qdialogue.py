from typing import Dict

from PyQt5.QtWidgets import QDialog

from spmclient import consts
from spmclient.ui.gui.xml.ui_analysis_type_dialogue import Ui_Dialog


# from spmclient import consts
# class AnalysisTypeQDialogueMeta(QDialog, Ui_Analysis_type_qdialogue):
#     pass
class AnalysisTypeQDialogue(QDialog, Ui_Dialog):  #, ui_analysis_type_dialogue, metaclass=AnalysisTypeQDialogueMeta):

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)

    def _rt_side_checked(self):
        return self.rt_side_checkBox.isChecked()

    def _lt_side_checked(self):
        return self.lt_side_checkBox.isChecked()

    def get_params(self) -> Dict:
        params = dict()
        params[consts.RT_SIDE_CHECKED] = self._rt_side_checked()
        params[consts.LT_SIDE_CHECKED] = self._lt_side_checked()
        params[consts.KINEMATICS_CHECKED] = self.kinematics_radioButton.isChecked()
        params[consts.MOMENTS_CHECKED] = self.moments_radioButton.isChecked()
        params[consts.ALPHA] = float(self.alpha_comboBox.currentText())
        return params
