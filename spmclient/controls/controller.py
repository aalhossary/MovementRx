from abc import ABCMeta, abstractmethod
from typing import Dict

from PyQt5.QtCore import QObject


class Controller(QObject):  # (metaclass=ABCMeta):
    def set_data(self, data: Dict, subject: str):
        raise NotImplementedError()

    def update_graphs(self, data: Dict = None, tasks: Dict = None):
        raise NotImplementedError()

    def analyse_all(self, analysis: str, alpha: float, ankle_x_only):
        raise NotImplementedError()

    def save_analysis(self, analysis_name: str, dir_name: str):
        raise NotImplementedError()

    def delete_data(self):
        raise NotImplementedError()

    def delete_analysis(self):
        raise NotImplementedError()

    def load_data(self, dir_name, subject_name:str):
        raise NotImplementedError()
