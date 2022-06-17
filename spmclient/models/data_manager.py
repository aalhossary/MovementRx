from __future__ import annotations

from builtins import classmethod
from typing import Dict, cast, Optional, Tuple

import numpy as np

from spm1d.stats._spm import SPMi_T
from spmclient import consts
from spmclient.ui.gui.DisplayFormat import DisplayFormat


class DataManager:

    _instance: DataManager = None
    # empty_dict = dict()
    _raw_data = dict()
    _analysis_data = dict()
    _analysis_data_compact = dict()
    _data_available_flags: Dict[str, bool] = dict()
    _analysis_available_flags: Dict[str, bool] = dict()

    def __new__(cls, *args, **kwargs):
        """Implement the Singleton design pattern."""
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls, *args, **kwargs)
            # initialize here any properties you like as well
            # cls._instance._raw_data = dict()
        return cls._instance

    @classmethod
    def set_data(cls, data_original_subject: Dict, subject: str):
        """merge or update self._raw_data according to the path"""
        data_renamed_subject = DataManager._rename_subject(data_original_subject, subject)

        DataManager.merge_subject(cls._raw_data, data_renamed_subject)
        cls._data_available_flags[subject] = True
        cls.update_all_ankle_dim_data_available()

    @classmethod
    def update_all_ankle_dim_data_available(cls):
        flag = True
        for subject in consts.subject:
            if cls.is_data_available(subject):
                path: Dict = {
                    consts.MEASUREMENT: consts.MEASUREMENT_MOMENTS,
                    consts.SUBJECT: subject,
                    consts.SIDE: consts.SIDE_LEFT,
                    consts.JOINT: consts.joint[2],
                    consts.DIMENSION: consts.dim[1]
                }
                multiples = cls._get_multiples(cls._raw_data, path=path)
                if multiples is not None:
                    flag &= len(multiples) > 0
        cls._data_available_flags['ALL_ANKLE_DIM'] = flag

    @classmethod
    def is_all_ankle_dim_data_available(cls) -> bool:
        """Check availability of all dimensions of ankle data of all available cases (default is True)."""
        return cls._data_available_flags.get('ALL_ANKLE_DIM', True)

    @classmethod
    def set_analysis_data(cls, analysis_data, analysis_name: str):
        cls._analysis_data = analysis_data
        cls._analysis_available_flags[analysis_name] = True

    @classmethod
    def set_analysis_data_compact(cls, analysis_data_compact, analysis_name: str):
        cls._analysis_data_compact = analysis_data_compact
        cls._analysis_available_flags[analysis_name] = True

    @classmethod
    def is_data_available(cls, subject: str) -> bool:
        """Check availability of data (and Handle errors)."""
        return cls._data_available_flags.get(subject, False)

    @classmethod
    def is_analysis_available(cls, subject: Optional[str] = None) -> bool:
        """Check availability of analysis (and Handle errors)."""
        if subject:  # check the availability of that specific subject
            return cls._analysis_available_flags.get(subject, False)
        else:  # is the analysis of any subject available
            return len(cls._analysis_available_flags) > 0

    @classmethod
    def get_average(cls, data: Dict, path: Dict = None) -> np.ndarray:
        # if not data:
        #     data = cls._raw_data
        data2d = DataManager._get_multiples(data, path)
        return np.average(data2d, axis=0)

    @classmethod
    def get_std(cls, data: Dict, path: Dict = None) -> np.ndarray:
        # if not data:
        #     data = cls._raw_data
        data2d = DataManager._get_multiples(data, path)
        return np.std(data2d, axis=0)

    @classmethod
    def get_multiples_from_data(cls, path: Dict = None, satisfy_missing_path_with_any: bool = False) \
            -> Optional[np.ndarray]:
        return cls._get_multiples(cls._raw_data, path, satisfy_missing_path_with_any)

    @classmethod
    def get_multiples_from_analysis_data(cls, path: Dict) -> Optional[Tuple[SPMi_T, DisplayFormat]]:  # -> Optional[np.ndarray]:
        return cls._get_multiples(cls._analysis_data, path, has_subject=False)

    @classmethod
    def get_multiples_from_analysis_data_compact(cls, path: Dict) -> Optional[Tuple[SPMi_T, DisplayFormat]]:
        return cls._get_multiples(cls._analysis_data_compact, path, has_subject=False, has_dimension=False)

    @classmethod
    def _get_multiples(cls, data: Dict = None, path: Dict = None, satisfy_missing_path_with_any: bool = False,
                       has_subject=True, has_dimension=True) -> Optional[np.ndarray]:
        # if not data:
        #     data = cls._raw_data
        try:
            measurement: str = path.get(consts.MEASUREMENT, None)
            if satisfy_missing_path_with_any and not measurement:
                measurement = next(iter(data.keys()))
            measurement_as_dict: Dict = data[measurement]

            if has_subject:  # TODO This way is bad. Change it
                subject: str = path.get(consts.SUBJECT, None)
                if satisfy_missing_path_with_any and not subject:
                    subject = next(iter(measurement_as_dict.keys()))
                subject_as_dict: Dict = measurement_as_dict[subject]
            else:
                subject_as_dict: Dict = measurement_as_dict

            side: str = path.get(consts.SIDE, None)
            if satisfy_missing_path_with_any and not side:
                side = next(iter(subject_as_dict.keys()))
            side_as_dict: Dict = subject_as_dict[side]

            joint_str: str = path.get(consts.JOINT, None)
            if satisfy_missing_path_with_any and not joint_str:
                joint_str = next(iter(side_as_dict.keys()))

            if has_dimension:
                joint_as_dict: Dict = side_as_dict[joint_str]
                dim_str: str = path.get(consts.DIMENSION, None)
                if satisfy_missing_path_with_any and not dim_str:
                    dim_str = next(iter(joint_as_dict.keys()))
                dimension: np.ndarray = joint_as_dict[dim_str]
                return dimension
            else:
                return side_as_dict[joint_str]

        except LookupError:  # KeyError:
            return None

    @staticmethod
    def merge_subject(all_data: Dict, additional_data: Dict):
        """Quick and Dirty method to merge _raw_data. Needs refactoring"""
        for measurement, new_measurement_dict in additional_data.items():
            all_data_measurement_dict = all_data.setdefault(measurement, dict())
            all_data_measurement_dict.update(new_measurement_dict)

    @staticmethod
    def _rename_subject(loaded_data, subject_new_name):
        data_renamed_subject = dict()
        for measurement, subjects_dict in loaded_data.items():
            subjects_dict = cast(Dict, subjects_dict)
            # subjects = subjects_dict.keys()
            if len(subjects_dict) > 1:
                raise RuntimeError("I don't know how to handle data with more than one subject (person)\n"
                                   f"measurement = {measurement}, subjects = {list(subjects_dict.keys())}")
            new_subject_dict = data_renamed_subject[measurement] = dict()
            new_subject_dict[subject_new_name] = next(iter(subjects_dict.values()))
        return data_renamed_subject

    @classmethod
    def clear_data(cls):
        cls._raw_data.clear()
        cls._data_available_flags.clear()

    @classmethod
    def clear_analysis_results(cls):
        cls._analysis_data.clear()
        cls._analysis_data_compact.clear()
        cls._analysis_available_flags.clear()
