import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QApplication
from matplotlib import cm
from matplotlib.colors import Normalize

from spmclient.ui.gui.xml.ui_colormap_chooser import Ui_colorMapChooser
from spmclient.ui.gui.xml.customcomponents import Singleton


class ColorMapChooserMeta(Singleton, QDialog.__class__, Ui_colorMapChooser.__class__):
    pass

class ColorMapChooser(QDialog, Ui_colorMapChooser, metaclass = ColorMapChooserMeta):
    
    def __init__(self):
        super().__init__()
        self.cmap1 = None
        self.cmap2 = None
        self.norm1 = None
        self.norm2 = None
        self.setupUi(self)
        self.update_legend()

    def setupUi(self, colorMapChooser: Ui_colorMapChooser):
        super().setupUi(colorMapChooser)

    @QtCore.pyqtSlot()
    def update_legend(self):
        print('update called')
        ax1 = self.individual_colormap_legend.ax
        if ax1.get_geometry() == (1, 1, 1):
            ax1.change_geometry(1, 3, 2)
        ax1.clear()
        ax2 = self.three_components_colormap_legend.ax
        if ax2.get_geometry() == (1, 1, 1):
            ax2.change_geometry(1, 3, 2)
        ax2.clear()

        figure1 = self.individual_colormap_legend.figure
#         figure1.gca().set_axis_off()
        figure2 = self.three_components_colormap_legend.figure
#         figure2.gca().set_axis_off()

#         if ax1 is not figure1.gca():
#             print('=======', ax1, figure1.gca())

        num_levels1 = self.individ_num_levels_spinBox.value()
        num_levels2 = self.threecomp_num_levels_spinBox.value()
        cmap_name1 = self.individ_colormap_name_comboBox.currentText()
        cmap_name2 = self.threecomp_colormap_name_comboBox.currentText()
        self.cmap1 = cm.get_cmap(cmap_name1, num_levels1)
        self.cmap2 = cm.get_cmap(cmap_name2, num_levels2)
        under_color = (0.5, 0.5, 0.5)
        self.cmap1.set_under(color=under_color)
        self.cmap2.set_under(color=under_color)

        self.norm1 = Normalize(vmin=self.individ_min_value_spinbox.value(), vmax=self.individ_max_value_spinbox.value())
        self.norm2 = Normalize(vmin=self.threecomp_min_value_spinbox.value(), vmax=self.threecomp_max_value_spinbox.value())

        colorbar1 = figure1.colorbar(cm.ScalarMappable(norm=self.norm1, cmap=self.cmap1), cax=ax1, orientation="vertical",
                                   use_gridspec=True, fraction=1.0, shrink=1.0, extend='both',
                                   )
        colorbar2 = figure2.colorbar(cm.ScalarMappable(norm=self.norm2, cmap=self.cmap2), cax=ax2, orientation="vertical",
                                   use_gridspec=True, fraction=1.0, shrink=1.0, extend='both',
                                   )
        self.individual_colormap_legend.canvas.draw()
        self.three_components_colormap_legend.canvas.draw()

def main():
    app = QApplication(sys.argv)
    cmc = ColorMapChooser()
    cmc.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
