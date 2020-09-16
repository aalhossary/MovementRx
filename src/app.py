from __future__ import annotations
import sys
from typing import Dict, cast, Tuple, List

from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QApplication

import spm1d
from src import consts
from src.controls.controller import Controller
from src.controls.analysis_type_qdialogue import AnalysisTypeQDialogue
from src.controls.gait_analysis_window import GaitAnalysisWindow
from src.models.data_manager import DataManager
from src.ui.displaymanager import DisplayManager
from src.ui.gui.DisplayFormat import DisplayFormat
from src.ui.gui.xml.mplcanvas import MplCanvas


class App(Controller):

    _instance: App = None
    _display_manager: DisplayManager = None

    def __new__(cls, *args, **kwargs):
        """Implement the Singleton design pattern."""
        if cls._instance is None:
            cls._instance = super(App, cls).__new__(cls, *args, **kwargs)
            # initialize here any properties you like as well
        return cls._instance

    def set_data(self, data: Dict, subject: str):
        DataManager().set_data(data, subject)
        self._display_manager.data_loaded(data)
        self._display_manager.show_raw_data()

    def analyse(self, analysis: str, alpha: float):
        # switch on the test type
        # The test_params are a list of triplets in the form of [(YA, YB, format)]
        if analysis == consts.PRE_VS_REF:
            test_params = [(consts.SUBJECT_REF, consts.SUBJECT_B4, consts.SUBJECT_B4)]
        elif analysis == consts.POST_VS_REF:
            test_params = [(consts.SUBJECT_REF, consts.SUBJECT_AFTER, consts.SUBJECT_AFTER)]
        elif analysis == consts.PRE_AND_POST_VS_REF:
            test_params = [(consts.SUBJECT_REF, consts.SUBJECT_B4, consts.SUBJECT_B4),
                           (consts.SUBJECT_REF, consts.SUBJECT_AFTER, consts.SUBJECT_AFTER)]
        elif analysis == consts.PRE_VS_POST_PAIRED:
            test_params = [(consts.SUBJECT_B4, consts.SUBJECT_AFTER, consts.SUBJECT_REF)]
            test_name = 'paired'
        elif analysis == consts.PRE_VS_POST_TWO_SAMPLE:
            test_params = [(consts.SUBJECT_B4, consts.SUBJECT_AFTER, consts.SUBJECT_REF)]
            test_name = 'Two_test'
        else:
            raise RuntimeError(f'Unknown analysis type ({analysis})!')

        # self._display_manager.analysis_started()
        detailed_analysis_data = dict()
        # do the detailed test
        for i_meas, meas in enumerate(consts.measurement_folder):
            measurement_detailed_dict = detailed_analysis_data.setdefault(meas, dict())
            for i_s, s in enumerate(consts.side):
                side_detailed_dict = measurement_detailed_dict.setdefault(s, dict())
                for i_j, j in enumerate(consts.joint):
                    joint_detailed_dict = side_detailed_dict.setdefault(j, dict())
                    for i_d, d in enumerate(consts.dim):
                        # dimension_detailed_dict = joint_detailed_dict.setdefault(d, dict())
                        temp_display_data_list = []
                        temp_display_fmat_list = []
                        for current_round in test_params:
                            subject_a, subject_b, display_subject = current_round[0], current_round[1], current_round[2]
                            task_ya: Dict = {
                                consts.MEASUREMENT: meas,
                                consts.SUBJECT: subject_a,
                                consts.SIDE: s,
                                consts.JOINT: j,
                                consts.DIMENSION: d
                            }
                            data_ya = DataManager.get_multiples(path=task_ya)
                            task_yb: Dict = {
                                consts.MEASUREMENT: meas,
                                consts.SUBJECT: subject_b,
                                consts.SIDE: s,
                                consts.JOINT: j,
                                consts.DIMENSION: d
                            }
                            data_yb = DataManager.get_multiples(path=task_yb)
                            if data_ya is not None and data_yb is not None:
                                t2 = do_spm_test(data_ya, data_yb)
                                t2i, lst = infer_z(t2, alpha)
                                # lst represents the infered array of deviation between postoperative and ref
                                # per joint in this dimension
                                # temp_display_data_list.append(lst)
                                temp_display_data_list.append(t2i)
                                temp_display_fmat_list.append(DisplayFormat(subject=display_subject, side=s))
                            # set the results in the DataManager, along with its DisplayFormat
                            joint_detailed_dict[d] = (temp_display_data_list, temp_display_fmat_list)
        DataManager.set_analysis_data(detailed_analysis_data)

        # do the compact test
        compact_analysis_data = dict()
        for i_meas, meas in enumerate(consts.measurement_folder):
            measurement_compact_dict = compact_analysis_data.setdefault(meas, dict())
            for i_s, s in enumerate(consts.side):
                side_compact_dict = measurement_compact_dict.setdefault(s, dict())
                for i_j, j in enumerate(consts.joint):
                    # joint_compact_dict = side_compact_dict.setdefault(j, dict())
                    temp_display_data_list = []
                    temp_display_fmat_list = []
                    for current_round in test_params:
                        subject_a, subject_b, display_subject = current_round[0], current_round[1], current_round[2]
                        # get the data of X,Y,Z and consider them as YA then YB respectively
                        data_ya, data_yb = None, None
                        for i_d, d in enumerate(consts.dim):
                            task_ya: Dict = {
                                consts.MEASUREMENT: meas,
                                consts.SUBJECT: subject_a,
                                consts.SIDE: s,
                                consts.JOINT: j,
                                consts.DIMENSION: d
                            }
                            temp_joint_dimension_multiple = DataManager.get_multiples(path=task_ya)
                            if temp_joint_dimension_multiple is None:
                                continue
                            if i_d == 0:
                                data_ya = np.ndarray(shape=(*temp_joint_dimension_multiple.shape, 3))
                            data_ya[:, :, i_d] = temp_joint_dimension_multiple

                            task_yb: Dict = {
                                consts.MEASUREMENT: meas,
                                consts.SUBJECT: subject_b,
                                consts.SIDE: s,
                                consts.JOINT: j,
                                consts.DIMENSION: d
                            }
                            temp_joint_dimension_multiple = DataManager.get_multiples(path=task_yb)
                            if temp_joint_dimension_multiple is None:
                                continue
                            if i_d == 0:
                                data_yb = np.ndarray(shape=(*temp_joint_dimension_multiple.shape, 3))
                            data_yb[:, :, i_d] = temp_joint_dimension_multiple

                        if data_ya is not None and data_yb is not None:
                            t2 = do_spm_test(data_ya, data_yb)
                            t2i, lst = infer_z(t2, alpha)
                            # temp_display_data_list.append(lst)
                            temp_display_data_list.append(t2i)
                            temp_display_fmat_list.append(DisplayFormat(subject=display_subject, side=s))
                    # set the results in the DataManager, along with its DisplayFormat
                    side_compact_dict[j] = (temp_display_data_list, temp_display_fmat_list)

        DataManager.set_analysis_data_compact(compact_analysis_data)
        self._display_manager.analysis_done()

        self._display_manager.show_analysis_result()

    def __init__(self):
        self.params: Dict = None

    def main(self):
        app = QApplication(sys.argv)
        analysis_type_dialogue = AnalysisTypeQDialogue()
        # analysis_type_dialogue.setModal(True)

        if analysis_type_dialogue.exec():
            self.params = analysis_type_dialogue.get_params()
            print(self.params)

            gait_analysis_window = GaitAnalysisWindow(self.params, controller=self)
            gait_analysis_window.show()
            self._display_manager = gait_analysis_window

        sys.exit(app.exec())


def do_spm_test(YA: np.ndarray, YB: np.ndarray) -> spm1d.stats._spm.SPM_T:
    if YA.ndim == 2 and YB.ndim == 2:
        # YA = YA[:, :, np.newaxis]
        # YB = YB[:, :, np.newaxis]
        spm_t = spm1d.stats.ttest2(YA, YB)
    elif YA.ndim == 3 and YB.ndim == 3:
        spm_t = spm1d.stats.hotellings2(YA, YB)
    else:
        raise RuntimeError(f'I do not know how to deal with array dimensions ({YA.shape}), ({YB.shape})')

    return spm_t


def infer_z(spm_t, alpha) -> Tuple[spm1d.stats._spm.SPMi_T, np.array]:
    spmi_t = spm_t.inference(alpha)
    return spmi_t, (spmi_t.z / spmi_t.zstar)


if __name__ == '__main__':
    App().main()
