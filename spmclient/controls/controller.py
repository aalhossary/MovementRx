from abc import ABCMeta, abstractmethod
from typing import Dict

from PyQt5.QtCore import QObject


class Controller(QObject):  # (metaclass=ABCMeta):
    def set_data(self, data: Dict, subject: str):
        raise NotImplementedError()

    def update_graphs(self, data: Dict = None, tasks: Dict = None):
        raise NotImplementedError()

    def analyse_all(self, analysis: str, alpha: float, ref_vs_mean: bool, ankle_x_only) -> None:
        """
        Analyse all panels (individual and compound)

        Args:
            analysis: Analysis name
            alpha: Alpha value
            ref_vs_mean: determines whether the whole sample will be compared to the reference or only its mean would
            be. This parameter is ignored if the user is doing PRE_VS_POST_PAIRED analysis.
            ankle_x_only: Whether the Ankle has data in the X axis only. This parameter should be removed in later
            versions when we use new reference data.
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
