from __future__ import annotations

from pathlib import Path

from builtins import staticmethod
import sys
from typing import Dict, Tuple, Optional

from PyQt5.QtWidgets import QApplication

import numpy as np
import spm1d
from spm1d.stats._spm import SPM_T, SPMi_T
from spmclient import consts
from spmclient.controls.controller import Controller
from spmclient.controls.gait_analysis_window import GaitAnalysisWindow
from spmclient.models.data_manager import DataManager
from spmclient.models.datasources import datagrapper
from spmclient.ui.displaymanager import DisplayManager
from spmclient.ui.gui.DisplayFormat import DisplayFormat


TTEST_2 = 'ttest2'
TTEST = 'ttest'
TTEST_PAIRED = 'ttest_paired'
HOTELLINGS_2 = 'hotellings2'
HOTELLINGS = 'hotellings'
HOTELLINGS_PAIRED = 'hotellings_paired'


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

    def analyse_all(self, analysis: str, alpha: float, ref_vs_mean: bool, ankle_x_only: bool = False) -> None:
        # switch on the test type
        # The test_params are a list of triplets in the form of [(ya, yb, format)]
        # The test names are a list of the form [2D test, 3D test]
        if analysis == consts.PRE_VS_POST_PAIRED:
            test_params = [(consts.SUBJECT_B4, consts.SUBJECT_AFTER, consts.SUBJECT_REF)]
            test_names = [TTEST_PAIRED, HOTELLINGS_PAIRED]
        else:
            test_names = [TTEST, HOTELLINGS] if ref_vs_mean else [TTEST_2, HOTELLINGS_2]

            if analysis == consts.PRE_VS_REF:
                test_params = [(consts.SUBJECT_REF, consts.SUBJECT_B4, consts.SUBJECT_B4)]
            elif analysis == consts.POST_VS_REF:
                test_params = [(consts.SUBJECT_REF, consts.SUBJECT_AFTER, consts.SUBJECT_AFTER)]
            elif analysis == consts.PRE_AND_POST_VS_REF:
                test_params = [(consts.SUBJECT_REF, consts.SUBJECT_B4, consts.SUBJECT_B4),
                               (consts.SUBJECT_REF, consts.SUBJECT_AFTER, consts.SUBJECT_AFTER)]
            elif analysis == consts.PRE_VS_POST_TWO_SAMPLE:
                test_params = [(consts.SUBJECT_B4, consts.SUBJECT_AFTER, consts.SUBJECT_REF)]
            else:
                raise RuntimeError(f'Unknown analysis type ({analysis})!')

        # self._display_manager.analysis_started()
        detailed_analysis_data = dict()
        # do the detailed test
        for meas in consts.measurement_folder:
            measurement_detailed_dict = detailed_analysis_data.setdefault(meas, dict())
            for s in consts.side:
                side_detailed_dict = measurement_detailed_dict.setdefault(s, dict())
                for i_j, j in enumerate(consts.joint):
                    joint_detailed_dict = side_detailed_dict.setdefault(j, dict())
                    for i_d, d in enumerate(consts.dim):

                        if ankle_x_only and i_j == 2 and i_d:  # > 0:
                            continue

                        # dimension_detailed_dict = joint_detailed_dict.setdefault(d, dict())
                        temp_display_data_list = []
                        temp_display_fmat_list = []

                        for current_round in test_params:
                            subject_a, subject_b, display_subject = current_round
                            spmi_t = self.analyse(alpha, d, j, meas, s, subject_a, subject_b, test_names[0], ref_vs_mean)
                            if spmi_t is not None:
                                temp_display_data_list.append(spmi_t)
                                temp_display_fmat_list.append(DisplayFormat(subject=display_subject, side=s))

                        # set the results in the DataManager, along with its DisplayFormat
                        joint_detailed_dict[d] = (temp_display_data_list, temp_display_fmat_list)
        DataManager.set_analysis_data(detailed_analysis_data, analysis)

        # do the compact test
        compact_analysis_data: Dict[str, Dict] = dict()
        for _, meas in enumerate(consts.measurement_folder):
            measurement_compact_dict = compact_analysis_data.setdefault(meas, dict())
            for _, s in enumerate(consts.side):
                side_compact_dict = measurement_compact_dict.setdefault(s, dict())
                for i_j, j in enumerate(consts.joint):

                    if ankle_x_only and i_j == 2:
                        continue

                    # joint_compact_dict = side_compact_dict.setdefault(j, dict())
                    temp_display_data_list = []
                    temp_display_fmat_list = []

                    for current_round in test_params:
                        subject_a, subject_b, display_subject = current_round
                        spmi_t = self.analyse(alpha, None, j, meas, s, subject_a, subject_b, test_names[1], ref_vs_mean)
                        if spmi_t is not None:
                            temp_display_data_list.append(spmi_t)
                            temp_display_fmat_list.append(DisplayFormat(subject=display_subject, side=s))

                    # set the results in the DataManager, along with its DisplayFormat
                    side_compact_dict[j] = (temp_display_data_list, temp_display_fmat_list)

        DataManager.set_analysis_data_compact(compact_analysis_data, analysis)
        self._display_manager.analysis_done()

        self._display_manager.show_analysis_result(ankle_x_only=ankle_x_only)

    def analyse(self, alpha, d, j, meas, s, subject_a, subject_b, test_name, ref_vs_mean) -> Optional[SPMi_T]:
        data_ya, data_yb = None, None
        if d is not None:
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
        else:
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
            data_ya, data_yb, roi, _offset, tail = self._adjust_array_lengths(subject_a, meas, data_ya, data_yb)

            # if tail:
            #     rmse = DataManager.rmse(data_yb, data_ya)
            #     #  TODO manage the case of more than one RMSE value. use DataManager, etc.
            #     self._display_manager.show_rmse(task_yb, rmse)

            spm_t = App.do_spm_test(data_ya, data_yb, test_name, roi=roi, ref_vs_mean=ref_vs_mean)
            spmi_t, _ = App.infer_z(spm_t, alpha, scale_to_zstar=False)  # TODO add an option to scale or not
            return spmi_t
        return None

    def load_data(self, dir_name:str, subject_name):
        loaded_data = datagrapper.load_full_folder(dir_name, scale=True)
        self.set_data(loaded_data, subject_name)
        # TODO add something in DisplayManager to call update_actions_enabled()

    def save_analysis(self, analysis_name: str, dir_name: str):
        for meas in consts.measurement_folder:
            for s in consts.side:
                for i_j, j in enumerate(consts.joint):
                    task: Dict = {
                        consts.MEASUREMENT: meas,
                        consts.SIDE: s,
                        consts.JOINT: j,
                    }
                    # save analysis collective vector
                    stored_data = DataManager.get_multiples_from_analysis_data_compact(path=task)
                    if stored_data:
                        temp_display_data_list, temp_display_fmat_list = stored_data
                        datagrapper.save_analysis(data=temp_display_data_list, folder=Path(dir_name), task=task)
                    # Then save every dimension separately
                    for i_d, d in enumerate(consts.dim):
                        task[consts.DIMENSION] = d
                        dimension = DataManager.get_multiples_from_analysis_data(path=task)
                        if dimension:
                            temp_display_data_list, temp_display_fmat_list = dimension
                            #Note that they are two LISTS not two ITEMS
                            # draw each of the data / format pair on the canvas
                            # for t2i, fmt in zip(temp_display_data_list, temp_display_fmat_list):
                            #     pass

                            # DataManager.save_analysis(analysis_name)
                            datagrapper.save_analysis(data=temp_display_data_list, folder=Path(dir_name), task=task)
        self._display_manager.save_analysis_done()

    @staticmethod
    def _adjust_array_lengths(subject_a: str, meas: str, data_ya: np.ndarray, data_yb: np.ndarray) \
            -> Tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
        roi = np.array([True]*data_ya.shape[1])
        offset = 0  # To change later if needed
        tail = 0
        if subject_a == consts.SUBJECT_REF and meas == consts.MEASUREMENT_KINEMATICS:
            tail = data_ya.shape[1] - offset - data_yb.shape[1]
            if tail:
                roi[-tail:] = False

                tail_avr = np.average(data_ya[:, -tail:], axis=0)  # TODO to remove later if ROI is adjusted
                if data_yb.ndim == 2:
                    shape = (data_yb.shape[0], tail)
                elif data_yb.ndim == 3:
                    shape = (data_yb.shape[0], tail, 3)
                else:
                    raise RuntimeError(f'Can not deal with number of dimensions {data_yb.ndim}')
                temp_b_tail = np.empty(shape=shape)  # ones(shape=shape)
                temp_b_tail[:] = tail_avr[:]
                data_yb = np.concatenate((data_yb, temp_b_tail), axis=1)

                # data_ya = App.deflate(data_ya, roi)
        return data_ya, data_yb, roi, offset, tail

    @staticmethod
    def inflate(data: np.ndarray, roi: np.ndarray) -> np.ndarray:
        if not len(roi):
            return data
        segments = []
        prev_start = 0
        prev_state = roi[0]
        segments_arr = []
        for i in range(len(roi)):
            if roi[i] != prev_state:
                prev_state = roi[i]
                segments.append((prev_state, prev_start, i))
                prev_start = i
        segments.append((prev_state, prev_start, len(roi)))
        # now we have all segments
        for seg in segments:
            length = seg[2] - seg[1]
            shape = (data.shape[0], length) if data.ndim == 2 else (data.shape[0], length, data.shape[2])
            if seg[0]:
                segments_arr.append(data[:, length])
            else:
                segments_arr.append(np.zeros(shape, dtype=float))
        return np.concatenate(segments_arr, axis=1)

    @staticmethod
    def deflate(data_ya, roi: np.ndarray):
        return data_ya[:, roi]

    def delete_data(self):
        DataManager.clear_data()
        self.delete_analysis()
        self._display_manager.show_raw_data()

    def delete_analysis(self):
        DataManager.clear_analysis_results()
        self._display_manager.show_analysis_result()

    def update_graphs(self, data: Dict = None, tasks: Dict = None):
        # TODO implement
        pass

    def __init__(self):
        Controller.__init__(self, None)
        self.params: Optional[Dict] = None

    def get_default_params(self):
        params = dict()
        params[consts.RT_SIDE_CHECKED] = True
        params[consts.LT_SIDE_CHECKED] = True
        params[consts.KINEMATICS_CHECKED] = False
        params[consts.MOMENTS_CHECKED] = True
        params[consts.ALPHA] = 0.05
        return params

    def main(self):

        svi = sys.version_info
        if (svi.major, svi.minor) < (3, 8):
            print("\n"
                  "=======\n"
                  "Warning\n"
                  "=======\n"
                  "This paython version is less than 3.8!\n"
                  "Not all functions will run as expected. continue on your own responsibility.\n"
                  "Press ENTER to continue.")
            input()

        app = QApplication(sys.argv)
        # analysis_type_dialogue = AnalysisTypeQDialogue()
        # analysis_type_dialogue.setModal(True)

        self.params = self.get_default_params()
        print(self.params)

        gait_analysis_window = GaitAnalysisWindow(self.params, controller=self)
        gait_analysis_window.show()
        self._display_manager: DisplayManager = gait_analysis_window

        sys.exit(app.exec())

    @staticmethod
    def do_spm_test(ya: np.ndarray, yb: np.ndarray, test_name: str, roi: np.ndarray, ref_vs_mean: bool) \
            -> spm1d.stats._spm.SPM_T:
        # if ya.ndim == 2 and yb.ndim == 2:
        #     spm_t = spm1d.stats.ttest2(ya, yb)
        # elif ya.ndim == 3 and yb.ndim == 3:
        #     spm_t = spm1d.stats.hotellings2(ya, yb)
        # else:
        #     raise RuntimeError(f'I do not know how to deal with array dimensions ({ya.shape}), ({yb.shape})')

        test = eval('spm1d.stats.' + test_name)
        spm_t: Optional[SPM_T] = None
        if test_name in (HOTELLINGS_PAIRED, TTEST_PAIRED):
            spm_t = test(ya, yb, roi=roi)
        else:
            if ref_vs_mean:
                spm_t = test(ya, yb.mean(axis=0), roi=roi)
            else:
                spm_t = test(ya, yb, roi=roi)


        return spm_t

    @staticmethod
    def infer_z(spm_t, alpha, scale_to_zstar=False) -> Tuple[spm1d.stats._spm.SPMi_T, np.array]:  # TODO Review
        spmi_t = spm_t.inference(alpha)
        if scale_to_zstar:
            return spmi_t, (spmi_t.z / spmi_t.zstar)
        else:
            return spmi_t, (spmi_t.z)


if __name__ == '__main__':
    App().main()
