from PyQt5.Qt import QLabel
from PyQt5.QtCore import pyqtSlot

class AnalysisLabel(QLabel):

    def __init__(self, parent=None, *args, **kwargs):
        super(AnalysisLabel, self).__init__(parent=parent, *args, **kwargs)
        
        self.analysis_name = ''
        self.selected_widget_name = ''

    def get_analysis_name(self):
        return self.__analysis_name


    def get_selected_widget_name(self):
        return self.__selected_widget_name

    @pyqtSlot(str)
    def set_analysis_name(self, value):
        self.__analysis_name = value
        self.update_text()

    @pyqtSlot(str)
    def set_selected_widget_name(self, value):
        self.__selected_widget_name = value
        self.update_text()


    def del_analysis_name(self):
        del self.__analysis_name


    def del_selected_widget_name(self):
        del self.__selected_widget_name

    analysis_name = property(get_analysis_name, set_analysis_name, del_analysis_name, "analysis_name's docstring")
    selected_widget_name = property(get_selected_widget_name, set_selected_widget_name, del_selected_widget_name, "selected_widget_name's docstring")
    
    def update_text(self):
        text = ['<html><head/><body>']
        try:
            if self.analysis_name:
                text.append(f'<p><span style=" font-weight:600;">{self.analysis_name}</span></p>')
#         except AttributeError:
#             pass
#         try:
            if self.selected_widget_name:
                text.append(f'<p><span style=" font-weight:600;">{self.selected_widget_name}{{t}}</span></p>')
        except AttributeError:
            pass
        text.append('<p><span style=" font-weight:600;">Colorbar{T</span><span style=" font-weight:600; vertical-align:super;">2</span><span style=" font-weight:600;">}</span>')
        text.append('</p></body></html>')
        
        self.setText(''.join(text))

