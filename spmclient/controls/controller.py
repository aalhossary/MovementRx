from abc import ABCMeta, abstractmethod
from typing import Dict

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication


class Controller(QObject):  # (metaclass=ABCMeta):
    def set_data(self, data: Dict, subject: str):
        raise NotImplementedError()

    def update_graphs(self, data: Dict = None, tasks: Dict = None):
        raise NotImplementedError()

    def analyse(self, analysis: str, alpha: float, ankle_x_only):
        raise NotImplementedError()

    def delete_data(self):
        raise NotImplementedError()

    def delete_analysis(self):
        raise NotImplementedError()
