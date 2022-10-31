import sys
from typing import cast

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QApplication
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.colors import Normalize
from matplotlib.figure import Figure

from spmclient.ui.gui.xml.ui_colormap_chooser import Ui_colorMapChooser
from spmclient.ui.gui.xml.customcomponents import Singleton, LegendMplCanvas


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

    @staticmethod
    def prepare_figure(colormap_legend: LegendMplCanvas):
        figure = colormap_legend.figure
        ax = colormap_legend.ax
        if ax.get_subplotspec().get_geometry() == (1, 1, 0, 0):
            figure = cast(Figure, ax.figure)
            figure.clear()
            axs = figure.subplots(1, 3)
            for i in [0, 2]:
                axi = cast(Axes, axs[i])
                axi.set_visible(False)
            ax = cast(Axes, axs[1])
            figure.ax = ax
        ax.clear()
        return figure, ax

    @QtCore.pyqtSlot()
    def update_legend(self):
        print('update called')
        figure1, ax1 = ColorMapChooser.prepare_figure(self.individual_colormap_legend)
        figure2, ax2 = ColorMapChooser.prepare_figure(self.three_components_colormap_legend)

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

        # print(ax1.get_subplotspec(), figure1.bbox, ax1.get_subplotspec().get_position(figure=figure1))
        colorbar1 = figure1.colorbar(cm.ScalarMappable(norm=self.norm1, cmap=self.cmap1),
                                     cax=ax1, orientation="vertical",
                                     fraction=1.0, shrink=1.0,
                                     extend='both', extendfrac='auto',pad=0.0)
        colorbar2 = figure2.colorbar(cm.ScalarMappable(norm=self.norm2, cmap=self.cmap2),
                                     cax=ax2, orientation="vertical",
                                     fraction=1.0, shrink=1.0,
                                     extend='both', extendfrac='auto',pad=0.0)
        self.individual_colormap_legend.canvas.draw()
        self.three_components_colormap_legend.canvas.draw()

    @QtCore.pyqtSlot('bool')
    def toggle_same_as_individual_components(self, selected: bool):
        print(f'toggle_same_as_individual_components toggled {selected}')
        if selected:
            self.individ_colormap_name_comboBox.currentIndexChanged['int'].connect(
                self.threecomp_colormap_name_comboBox.setCurrentIndex)
            self.individ_num_levels_spinBox.valueChanged['int'].connect(self.threecomp_num_levels_spinBox.setValue)
            self.individ_colormap_name_comboBox.currentIndexChanged['int'].emit(self.individ_colormap_name_comboBox.currentIndex())
            self.individ_num_levels_spinBox.valueChanged['int'].emit(self.individ_num_levels_spinBox.value())

        else:
            self.individ_colormap_name_comboBox.currentIndexChanged['int'].disconnect(
                self.threecomp_colormap_name_comboBox.setCurrentIndex)
            self.individ_num_levels_spinBox.valueChanged['int'].disconnect(self.threecomp_num_levels_spinBox.setValue)


def main():
    app = QApplication(sys.argv)
    cmc = ColorMapChooser()
    cmc.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
