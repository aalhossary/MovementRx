from __future__ import annotations

import sys
from typing import Dict, Tuple

from PyQt5.QtWidgets import QApplication
import spm1d

import numpy as np
from spmclient import consts
import spmclient
from spmclient.controls.analysis_type_qdialogue import AnalysisTypeQDialogue
from spmclient.controls.controller import Controller
from spmclient.controls.gait_analysis_window import GaitAnalysisWindow
from spmclient.models.data_manager import DataManager
from spmclient.ui.displaymanager import DisplayManager
from spmclient.ui.gui.DisplayFormat import DisplayFormat


class App(Controller):

    _instance: spmclient.app.App = None
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
        TTEST_2 = 'ttest2'
        TTEST_PAIRED = 'ttest_paired'
        HOTELLINGS_2 = 'hotellings2'
        HOTELLINGS_PAIRED = 'hotellings_paired'
        # switch on the test type
        # The test_params are a list of triplets in the form of [(ya, yb, format)]
        # The test names are a list of the form [2D test, 3D test]
        if analysis == consts.PRE_VS_REF:
            test_params = [(consts.SUBJECT_REF, consts.SUBJECT_B4, consts.SUBJECT_B4)]
            test_names = [TTEST_2, HOTELLINGS_2]
        elif analysis == consts.POST_VS_REF:
            test_params = [(consts.SUBJECT_REF, consts.SUBJECT_AFTER, consts.SUBJECT_AFTER)]
            test_names = [TTEST_2, HOTELLINGS_2]
        elif analysis == consts.PRE_AND_POST_VS_REF:
            test_params = [(consts.SUBJECT_REF, consts.SUBJECT_B4, consts.SUBJECT_B4),
                           (consts.SUBJECT_REF, consts.SUBJECT_AFTER, consts.SUBJECT_AFTER)]
            test_names = [TTEST_2, HOTELLINGS_2]
        elif analysis == consts.PRE_VS_POST_PAIRED:
            test_params = [(consts.SUBJECT_B4, consts.SUBJECT_AFTER, consts.SUBJECT_REF)]
            test_names = [TTEST_PAIRED, HOTELLINGS_PAIRED]
        elif analysis == consts.PRE_VS_POST_TWO_SAMPLE:
            test_params = [(consts.SUBJECT_B4, consts.SUBJECT_AFTER, consts.SUBJECT_REF)]
            test_names = [TTEST_2, HOTELLINGS_2]
        else:
            raise RuntimeError(f'Unknown analysis type ({analysis})!')

        # self._display_manager.analysis_started()
        detailed_analysis_data = dict()
        # do the detailed test
        for _, meas in enumerate(consts.measurement_folder):
            measurement_detailed_dict = detailed_analysis_data.setdefault(meas, dict())
            for _, s in enumerate(consts.side):
                side_detailed_dict = measurement_detailed_dict.setdefault(s, dict())
                for _, j in enumerate(consts.joint):
                    joint_detailed_dict = side_detailed_dict.setdefault(j, dict())
                    for i_d, d in enumerate(consts.dim):
                        # dimension_detailed_dict = joint_detailed_dict.setdefault(d, dict())
                        temp_display_data_list = []
                        temp_display_fmat_list = []
                        for current_round in test_params:
                            subject_a, subject_b, display_subject = current_round
                            task_ya: Dict = {
                                consts.MEASUREMENT: meas,
                                consts.SUBJECT: subject_a,
                                consts.SIDE: s,
                                consts.JOINT: j,
                                consts.DIMENSION: d
                            }
                            data_ya = DataManager.get_multiples_from_data(path=task_ya)
                            task_yb: Dict = {
                                consts.MEASUREMENT: meas,
                                consts.SUBJECT: subject_b,
                                consts.SIDE: s,
                                consts.JOINT: j,
                                consts.DIMENSION: d
                            }
                            data_yb = DataManager.get_multiples_from_data(path=task_yb)
                            if data_ya is not None and data_yb is not None:
                                spm_t = do_spm_test(data_ya, data_yb, test_names[0])
                                spmi_t, _ = infer_z(spm_t, alpha)
                                temp_display_data_list.append(spmi_t)
                                temp_display_fmat_list.append(DisplayFormat(subject=display_subject, side=s))
                            # set the results in the DataManager, along with its DisplayFormat
                            joint_detailed_dict[d] = (temp_display_data_list, temp_display_fmat_list)
        DataManager.set_analysis_data(detailed_analysis_data)

        # do the compact test
        compact_analysis_data = dict()
        for _, meas in enumerate(consts.measurement_folder):
            measurement_compact_dict = compact_analysis_data.setdefault(meas, dict())
            for _, s in enumerate(consts.side):
                side_compact_dict = measurement_compact_dict.setdefault(s, dict())
                for _, j in enumerate(consts.joint):
                    # joint_compact_dict = side_compact_dict.setdefault(j, dict())
                    temp_display_data_list = []
                    temp_display_fmat_list = []
                    for current_round in test_params:
                        subject_a, subject_b, display_subject = current_round[0], current_round[1], current_round[2]
                        # get the data of X,Y,Z and consider them as ya then yb respectively
                        data_ya, data_yb = None, None
                        for i_d, d in enumerate(consts.dim):
                            task_ya: Dict = {
                                consts.MEASUREMENT: meas,
                                consts.SUBJECT: subject_a,
                                consts.SIDE: s,
                                consts.JOINT: j,
                                consts.DIMENSION: d
                            }
                            temp_joint_dimension_multiple = DataManager.get_multiples_from_data(path=task_ya)
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
                            temp_joint_dimension_multiple = DataManager.get_multiples_from_data(path=task_yb)
                            if temp_joint_dimension_multiple is None:
                                continue
                            if i_d == 0:
                                data_yb = np.ndarray(shape=(*temp_joint_dimension_multiple.shape, 3))
                            data_yb[:, :, i_d] = temp_joint_dimension_multiple

                        if data_ya is not None and data_yb is not None:
                            spm_t = do_spm_test(data_ya, data_yb, test_names[1])
                            spmi_t, _ = infer_z(spm_t, alpha)
                            temp_display_data_list.append(spmi_t)
                            temp_display_fmat_list.append(DisplayFormat(subject=display_subject, side=s))
                    # set the results in the DataManager, along with its DisplayFormat
                    side_compact_dict[j] = (temp_display_data_list, temp_display_fmat_list)

        DataManager.set_analysis_data_compact(compact_analysis_data)
        self._display_manager.analysis_done()

        self._display_manager.show_analysis_result()

    def delete_data(self):
        self.delete_analysis()
        DataManager.clear_data()
        self._display_manager.show_raw_data()

    def delete_analysis(self):
        DataManager.clear_analysis_results()
        self._display_manager.show_analysis_result()

    def update_graphs(self, data: Dict = None, tasks: Dict = None):
        # TODO implement
        pass

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


def do_spm_test(ya: np.ndarray, yb: np.ndarray, test_name: str) -> spm1d.stats._spm.SPM_T:
    # if ya.ndim == 2 and yb.ndim == 2:
    #     spm_t = spm1d.stats.ttest2(ya, yb)
    # elif ya.ndim == 3 and yb.ndim == 3:
    #     spm_t = spm1d.stats.hotellings2(ya, yb)
    # else:
    #     raise RuntimeError(f'I do not know how to deal with array dimensions ({ya.shape}), ({yb.shape})')
    test = eval('spm1d.stats.' + test_name)
    spm_t = test(ya, yb)
    return spm_t


def infer_z(spm_t, alpha) -> Tuple[spm1d.stats._spm.SPMi_T, np.array]:
    spmi_t = spm_t.inference(alpha)
    return spmi_t, (spmi_t.z / spmi_t.zstar)


if __name__ == '__main__':
    App().main()
