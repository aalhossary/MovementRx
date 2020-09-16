from typing import Dict


class DisplayManager:
    def data_loaded(self, data: Dict):
        raise NotImplementedError()

    def show_raw_data(self):
        raise NotImplementedError()

    def analysis_done(self):
        raise NotImplementedError()

    def show_analysis_result(self):
        raise NotImplementedError()
