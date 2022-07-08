from abc import ABCMeta, abstractmethod
from typing import Dict

from PyQt5.QtCore import QObject


class Controller(QObject):  # (metaclass=ABCMeta):
    def set_data(self, data: Dict, subject: str):  # TODO this method could be safely removed for the sake of load_data
        raise NotImplementedError()

    def update_graphs(self, data: Dict = None, tasks: Dict = None):
        raise NotImplementedError()

    def analyse_all(self, analysis: str, alpha: float, ref_vs_mean: bool, ankle_x_only) -> None:
        """
        initiates analysis of both available studies (kinematics and moments) on all available joints and joint
        dimensions.
        Args:
            analysis: Analysis name
            alpha: The alpha value (e.g. 0.05)
            ref_vs_mean: determines whether the whole sample will be compared to the reference or only its mean would
                be. This parameter is ignored if the user is doing PRE_VS_POST_PAIRED analysis, because in this case,
                the test is performed as REFERENCE VERSUS ALL SAMPLE by default.
            ankle_x_only: Whether the Ankle has data in the X axis only. This parameter should be removed in later
            versions when we use new data.

        Returns:
            None
        """
        raise NotImplementedError()

    def save_analysis(self, analysis_name: str, dir_name: str):
        raise NotImplementedError()

    def delete_data(self):
        raise NotImplementedError()

    def delete_analysis(self):
        raise NotImplementedError()

    def load_data(self, dir_name, subject_name:str):
        raise NotImplementedError()
