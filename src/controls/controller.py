from abc import ABCMeta, abstractmethod
from typing import Dict


class Controller(metaclass=ABCMeta):
    def set_data(self, data: Dict, subject: str):
        raise NotImplementedError()

    def update_graphs(self, data: Dict = None, tasks: Dict = None):
        raise NotImplementedError()

    def analyse(self, analysis: str, alpha: float):
        raise NotImplementedError()
