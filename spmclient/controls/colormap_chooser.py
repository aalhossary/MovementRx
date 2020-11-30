import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QApplication
from matplotlib import cm
from matplotlib.colors import Normalize

from spmclient.ui.gui.xml.ui_colormap_chooser import Ui_colorMapChooser


class ColorMapChooser(QDialog, Ui_colorMapChooser):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.update_legend()

    def setupUi(self, colorMapChooser: Ui_colorMapChooser):
        super().setupUi(colorMapChooser)

    @QtCore.pyqtSlot()
    def update_legend(self):
        print('update called')
        ax = self.colormap_legend.ax
        if ax.get_geometry() == (1, 1, 1):
            ax.change_geometry(1, 3, 2)
        ax.clear()

        figure = self.colormap_legend.figure
        figure.gca().set_axis_off()
        if ax is not figure.gca():
            print('=======', ax, figure.gca())

        num_levels = self.num_levels_spinBox.value()
        cmap_name = self.colormap_name_comboBox.currentText()
        cmap = cm.get_cmap(cmap_name, num_levels)
        under_color = (0.5, 0.5, 0.5)
        cmap.set_under(color=under_color)

        norm = Normalize(vmin=self.min_value_spinbox.value(), vmax=self.max_value_spinbox.value())

        # colorbar = figure.colorbar(axes_image,
        #                            orientation="vertical",
        #                            cax=ax,
        #                            use_gridspec=True,
        #                            fraction=1.0, shrink=1.0,
        #                            ticks=np.arange(10) + 0.5,
        #                            )
        colorbar = figure.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation="vertical",
                                   use_gridspec=True, fraction=1.0, shrink=1.0,
                                   )
        self.colormap_legend.canvas.draw()

def main():
    app = QApplication(sys.argv)
    cmc = ColorMapChooser()
    cmc.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
