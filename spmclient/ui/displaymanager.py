from typing import Dict


class DisplayManager:
    def data_loaded(self, data: Dict):
        raise NotImplementedError()

    def show_raw_data(self):
        raise NotImplementedError()

    def analysis_done(self):
        raise NotImplementedError()

    def save_analysis_done(self):
        raise NotImplementedError()

    # def show_rmse(self, task_yb, rmse):
    #     raise NotImplementedError()
        
    def show_analysis_result(self, ankle_x_only: bool):
        raise NotImplementedError()
