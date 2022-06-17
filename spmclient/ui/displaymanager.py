from typing import Dict


class DisplayManager:
    def show_raw_data(self):
        raise NotImplementedError()

    def show_analysis_result(self, ankle_x_only: bool = False):
        raise NotImplementedError()

    def data_loaded(self, data: Dict):
        raise NotImplementedError()

    def analysis_done(self):
        raise NotImplementedError()

    def save_analysis_done(self):
        raise NotImplementedError()

