from __future__ import annotations

from pathlib import Path
from typing import Dict, cast, List, Optional

import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtGui
from PyQt5.Qt import QRegExp
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QStackedWidget, QAction, QActionGroup, \
    QButtonGroup, QAbstractButton, QWidget
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.colors import Normalize
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D

import spm1d
from spmclient import consts
from spmclient.controls.controller import Controller
from spmclient.models.data_manager import DataManager
from spmclient.models.datasources.datagrapper import load_full_folder
from spmclient.ui.displaymanager import DisplayManager
from spmclient.ui.gui.DisplayFormat import DisplayFormat
from spmclient.ui.gui.xml.customcomponents import MplCanvas, KinematicsScaler,\
    MomentsScaler
from spmclient.ui.gui.xml.ui_gait_analysis_window import Ui_ui_GaitAnalysisWindow


class GaitAnalysisWindow(QMainWindow, Ui_ui_GaitAnalysisWindow, DisplayManager):

    def __init__(self, params: Dict, controller: Controller):
        QMainWindow.__init__(self)
        Ui_ui_GaitAnalysisWindow.__init__(self)
        self.controller = controller
        self.setupUi(self)

        self.data_ligand = dict()

        self.analyse_action_group = QActionGroup(self)
        self.analyse_action_group.setExclusive(False)
        self.analyse_action_group.addAction(self.actionPre_vs_Reference)
        self.analyse_action_group.addAction(self.actionPost_vs_Ref)
        self.analyse_action_group.addAction(self.actionPre_and_Post_Vs_Ref)
        self.analyse_action_group.addAction(self.actionPaired)
        self.analyse_action_group.addAction(self.actionTwo_Sample)
        self.analyse_action_group.triggered[QAction].connect(self.analyse)

        self.measurement_action_group = QActionGroup(self)
        self.measurement_action_group.addAction(self.actionKinematics)
        self.measurement_action_group.addAction(self.actionMoments)
        self.measurement_action_group.setExclusive(True)
        self.actionKinematics.setChecked(params.get(consts.KINEMATICS_CHECKED, False))
        self.actionMoments.setChecked(params.get(consts.MOMENTS_CHECKED, False))
        self.measurement_action_group.triggered[QAction].connect(self.display_options_changed)

        self.sides_action_group = QActionGroup(self)
        self.sides_action_group.addAction(self.actionRight_Side)
        self.sides_action_group.addAction(self.actionLeft_Side)
        self.sides_action_group.setExclusive(False)
        self.actionRight_Side.setChecked(params.get(consts.RT_SIDE_CHECKED, False))
        self.actionLeft_Side.setChecked(params.get(consts.LT_SIDE_CHECKED, False))
        self.sides_action_group.triggered[QAction].connect(self.visible_sides_changed)
        
        self.show_hide_joint_button_group = QButtonGroup(self)
        self.show_hide_joint_button_group.setExclusive(False) #  Must be set before adding any buttons
        self.show_hide_joint_button_group.addButton(self.pushButton_0R)
        self.show_hide_joint_button_group.addButton(self.pushButton_1R)
        self.show_hide_joint_button_group.addButton(self.pushButton_2R)
        self.show_hide_joint_button_group.addButton(self.pushButton_0L)
        self.show_hide_joint_button_group.addButton(self.pushButton_1L)
        self.show_hide_joint_button_group.addButton(self.pushButton_2L)
        self.show_hide_joint_button_group.buttonClicked.connect(self.joint_button_clicked)

        

        self.alpha = params.get(consts.ALPHA)
        self.ankle_x_only = True

        self.action_specify_normal_standard.triggered.connect(self.load_reference)
        self.action_open_before_intervension.triggered.connect(self.load_before_intervention)
        self.action_open_after_surgery_data.triggered.connect(self.load_after_intervention)
        self.action_clear_all.triggered.connect(self.clear_all)
        self.action_clear_analysis.triggered.connect(self.clear_analysis)
        self.actionNextView.triggered.connect(self.show_next_view)

        plt.rcParams['figure.constrained_layout.use'] = True
        
        self.set_analysis_visible(False)
        
        self.show_study_name()
        self.animator_timer: Optional[QTimer] = None

    def set_analysis_visible(self, show: bool):
        re = QRegExp('joint[012][RL]')
        qlist: List[QObject] = self.findChildren(MplCanvas, re)
        for widget in qlist:
            # print('set', widget.objectName(), 'visibility to', show)
            # TODO Simplify this expression
            if not show:
                widget.setVisible(show)
            else:
                if self.ankle_x_only and widget.objectName()[-2] != '2':  # not in ('2'):
                    widget.setVisible(show)
        
        re = QRegExp('stackedWidget[012][012][RL]')
        qlist: List[QObject] = self.findChildren(QStackedWidget, re)
        for widget in qlist:
            # print('set', widget.objectName(), 'visibility to', show)
            if not show:
                widget.setVisible(show)
            else:
                if self.ankle_x_only and widget.objectName()[-3:-1] not in ('21', '22'):
                    widget.setVisible(show)

    def joint_button_clicked(self, button: QAbstractButton):
        suffix = button.objectName()[-3:]
        widget = self.findChild(QWidget, 'widget'+suffix)
        widget.setVisible(button.isChecked())
        
    def rt_side_checked(self):
        return self.actionRight_Side.isChecked()

    def lt_side_checked(self):
        return self.actionLeft_Side.isChecked()

    # TODO merge load_reference, load_before_intervention, load_after_intervention
    def load_reference(self):
        file_dialog = QFileDialog(self)
        d = Path(__file__).parents[2] / 'res/refDataScaled'
        dir_name = file_dialog.getExistingDirectory(self, caption="Select reference data root folder", directory=str(d))
        loaded_data = load_full_folder(dir_name)
        self.controller.set_data(loaded_data, consts.SUBJECT_REF)

    def load_before_intervention(self):
        file_dialog = QFileDialog(self)
        d = Path(__file__).parents[2] / 'res/cases/subj1_preResampled'
        dir_name = file_dialog.getExistingDirectory(self, caption="Select folder of preintervension data", directory=str(d))
        loaded_data = load_full_folder(dir_name, scale=True)
        self.controller.set_data(loaded_data, consts.SUBJECT_B4)

    def load_after_intervention(self):
        file_dialog = QFileDialog(self)
        d = Path(__file__).parents[2] / 'res/cases/subj1_postResampled'
        dir_name = file_dialog.getExistingDirectory(self, caption="Select folder of postintervension data", directory=str(d))
        loaded_data = load_full_folder(dir_name, scale=True)
        self.controller.set_data(loaded_data, consts.SUBJECT_AFTER)

    def data_loaded(self, data: Dict):
        # TODO tell that on status bar
        pass

    def add_line_to_ligand(self, current_task: Dict, data_format: DisplayFormat):
        title = f'{current_task[consts.SUBJECT]} {current_task[consts.SIDE]}'
        self.data_ligand[title] = Line2D([0], [0], linestyle=data_format.line_and_marks(), color=data_format.color(), label=title)

    def add_colorbar_to_legend(self, axes_image):
        print(f'add_colorbar_to_legend({axes_image})')
        ax = self.legend_heatmap_panel.ax
        
        print("current geometry =", ax.get_geometry())
        if ax.get_geometry() == (1, 1, 1):
            ax.change_geometry(1, 3, 2)

        ax.clear()
        
        figure = self.legend_heatmap_panel.figure
        figure.gca().set_axis_off()
        if ax is not figure.gca():
            print('=======', ax, figure.gca())

        if axes_image:
            print('Add legend')
#             print(figure.axes)
            colorbar = figure.colorbar(axes_image,
                                               orientation="vertical",
                                               cax=ax,
                                               use_gridspec=True,
                                               fraction=1.0, shrink=1.0,
                                               # anchor = (0.0, 0.5), panchor = (0.0, 0.5),
                                               ticks=np.arange(10) + 0.5, 
                                               # drawedges=True,
                                               # pad=0.2
                                        )
# #             print(figure.axes)
# #             colorbar.ax.set_yticklabels(['low', '', '', '', 'mid', '', '', '', 'High', ''])
#             colorbar.ax.set_yticklabels(['low', 'mid', 'High'])
# #             colorbar.ax.get_yaxis().set_ticks([])
            for j, lab in enumerate(['No effect', '', '', 'Min', '', '', 'Moderate', '', '', '', 'High',]):
                # colorbar.ax.text(.5, (4 * j + 2) / 4.0, lab, ha='center', va='center')
                colorbar.ax.text(2.5, ((2.9 * j) / 11) + 1.15, lab, ha='center', va='center')
        self.legend_heatmap_panel.canvas.draw()

    def show_raw_data(self):
        self.data_ligand.clear()
        # We can bypass all this section and start with the nested for loops directly
        measurements_to_update = consts.measurement_folder

        subjects_to_update = []
        if DataManager.is_data_available(consts.SUBJECT_REF):
            subjects_to_update.append(consts.SUBJECT_REF)
        if DataManager.is_data_available(consts.SUBJECT_B4):
            subjects_to_update.append(consts.SUBJECT_B4)
        if DataManager.is_data_available(consts.SUBJECT_AFTER):
            subjects_to_update.append(consts.SUBJECT_AFTER)

        sides_to_update = consts.side
        tasks = {
            consts.MEASUREMENT: measurements_to_update,
            consts.SUBJECT: subjects_to_update,
            consts.SIDE: sides_to_update,
            consts.JOINT: consts.joint,
            consts.DIMENSION: consts.dim
        }

        # Draw the raw data
        for meas in tasks[consts.MEASUREMENT]:
            if meas == consts.MEASUREMENT_KINEMATICS and not self.actionKinematics.isChecked():
                continue
            if meas == consts.MEASUREMENT_MOMENTS and not self.actionMoments.isChecked():
                continue
            for s in tasks[consts.SIDE]:
                for i_j, j in enumerate(tasks[consts.JOINT]):
                    for i_d, d in enumerate(tasks[consts.DIMENSION]):
                        data_canvas = self.get_target_canvas('data', i_j, i_d, side=s)
                        # clear it first
                        # data_canvas.figure.clear()
                        data_canvas.ax.clear()
                        for subj in tasks[consts.SUBJECT]:
                            data_format = DisplayFormat(subj, s)
                            current_task: Dict = {
                                consts.MEASUREMENT: meas,
                                consts.SUBJECT: subj,
                                consts.SIDE: s,
                                consts.JOINT: j,
                                consts.DIMENSION: d
                            }
                            current_data = DataManager.get_multiples_from_data(path=current_task)
                            if current_data is not None and len(current_data):
                                ax: Axes = cast(Axes, data_canvas.ax)
                                draw_mean_std(current_data, ax, data_format)
                                self.add_line_to_ligand(current_task, data_format)
                                # add vertical line in data
                                if self.actionKinematics.isChecked():
                                    data_canvas.ax.axvline(x=60, linewidth=4, color='k', ls='--', lw=1.5)
                        data_canvas.moving_line = None
                        data_canvas.canvas.draw()
                        ax = self.legend_data_panel.ax
                        ax.legend(handles=self.data_ligand.values(), frameon=False, loc='center')
                        ax.set_axis_off()
                        self.legend_data_panel.canvas.draw()

    def analyse(self, action: QAction):
        print(action.text())
        analysis = ''
        if action == self.actionPre_vs_Reference:
            analysis = consts.PRE_VS_REF
        elif action == self.actionPost_vs_Ref:
            analysis = consts.POST_VS_REF
        elif action == self.actionPre_and_Post_Vs_Ref:
            analysis = consts.PRE_AND_POST_VS_REF
        elif action == self.actionPaired:  # Pre Vs. Post
            analysis = consts.PRE_VS_POST_PAIRED
        elif action == self.actionTwo_Sample:  # Pre Vs. Post
            analysis = consts.PRE_VS_POST_TWO_SAMPLE

        self.controller.analyse(analysis, self.alpha, ankle_x_only=True)
        
        self.label_analysis.analysis_name = action.toolTip()

    def analysis_done(self):
        # TODO show that on status bar, and remove any waiting signs
        self.set_analysis_visible(True)

    def update_legend_selected_panel_name(self):
        names = ['Color Bar', 'SPM']
        self.label_analysis.set_selected_widget_name(names[self.stackedWidget00R.currentIndex()])

    def show_rmse(self, task_yb, rmse):
        pass
    
    def show_analysis_result(self, ankle_x_only=False):
        analysis_legend_image = None

        if self.actionKinematics.isChecked():
            self.scaler = KinematicsScaler()
        else:
            self.scaler = MomentsScaler()

        # first show the detailed analysis
        for s in consts.side:
            for i_j, j in enumerate(consts.joint):
                for i_d, d in enumerate(consts.dim):
                    
                    if ankle_x_only and i_j == 2 and i_d:  # > 0:
                        continue
                    
                    # get the canvases
                    spm_canvas = self.get_target_canvas('spm1d', i_j, i_d, side=s)
                    mose_canvas = self.get_target_canvas('mose', i_j, i_d, side=s)
                    # clear them first
                    spm_canvas.ax.clear()
                    mose_canvas.ax.clear()

                    for meas in consts.measurement_folder:
                        # filter
                        if meas == consts.MEASUREMENT_KINEMATICS and not self.actionKinematics.isChecked():
                            continue
                        if meas == consts.MEASUREMENT_MOMENTS and not self.actionMoments.isChecked():
                            continue
                        current_task: Dict = {
                            consts.MEASUREMENT: meas,
                            consts.SIDE: s,
                            consts.JOINT: j,
                            consts.DIMENSION: d
                        }
                        dimension = DataManager.get_multiples_from_analysis_data(path=current_task)
                        if dimension:
                            temp_display_data_list, temp_display_fmat_list = dimension
    
                            # draw each of the data / format pair on the canvas
                            for t2i, fmt in zip(temp_display_data_list, temp_display_fmat_list):
                                draw_inference_plot(spm_canvas, t2i, data_format=fmt)

                            temp_display_data = []
                            for t2i, fmt in zip(temp_display_data_list, temp_display_fmat_list):
                                cast(spm1d.stats._spm.SPMi_T, t2i)
                                z_values = t2i.z / t2i.zstar
                                temp_display_data.append(z_values)
                            analysis_legend_image = draw_heatmap(mose_canvas, temp_display_data)
                            spm_canvas.moving_line = None
                            mose_canvas.moving_line = None

                            # Add vertical line
                            if self.actionKinematics.isChecked():
                                spm_canvas.ax.axvline(x=60, linewidth=4, color='k', ls='--', lw=1.5)
                                mose_canvas.ax.axvline(x=60, linewidth=4, color='k', ls='--', lw=1.5)
                        spm_canvas.canvas.draw()
                        mose_canvas.canvas.draw()

        # Then show the compact analysis
        for s in consts.side:
            for i_j, j in enumerate(consts.joint):
                
                if ankle_x_only and i_j == 2:
                    continue
                
                # get the canvas
                joint_canvas = self.get_target_canvas('joint', i_j, None, side=s)
                # clear it first
                joint_canvas.ax.clear()
                joint_canvas.moving_line = None

                for meas in consts.measurement_folder:
                    # filter
                    if meas == consts.MEASUREMENT_KINEMATICS and not self.actionKinematics.isChecked():
                        continue
                    if meas == consts.MEASUREMENT_MOMENTS and not self.actionMoments.isChecked():
                        continue
                    current_task: Dict = {
                        consts.MEASUREMENT: meas,
                        consts.SIDE: s,
                        consts.JOINT: j,
                    }
                    dimension = DataManager.get_multiples_from_analysis_data_compact(path=current_task)
                    if dimension:
                        temp_display_data_list, temp_display_fmat_list = dimension
                        # draw each of the data / format pair on the canvas
                        temp_display_data = []
                        for t2i, fmt in zip(temp_display_data_list, temp_display_fmat_list):
                            cast(spm1d.stats._spm.SPMi_T, t2i)
                            z_values = t2i.z / t2i.zstar
                            temp_display_data.append(z_values)
                        analysis_legend_image = draw_heatmap(joint_canvas, temp_display_data)
                        # Add vertical line
                        if self.actionKinematics.isChecked():
                            joint_canvas.ax.axvline(x=60, linewidth=4, color='k', ls='--', lw=1.5)
                joint_canvas.canvas.draw()
                
        self.update_legend_selected_panel_name()
        self.add_colorbar_to_legend(analysis_legend_image)
        self.legend_heatmap_groupbox.setVisible(True)

        if self.animator_timer is None:
            self.animator_timer = QTimer(self)
            self.animator_timer.setSingleShot(False)
            self.animator_timer.timeout.connect(self.advance_animation)
        self.animator_timer.start(1500)

    def advance_animation(self):
        current_value = self.gait_sliderR.logicalValue()
        next_value_r = (current_value % 100) + 5  # * 2  # 5  # in the period [5, 100]
        next_value_l = ((next_value_r + 45) % 100) + 5  #  ((next_value_r - 5 + 50) % 100) + 5

        print('Next values', next_value_r, '\t', next_value_l)

        self.gait_sliderR.setLogicalValue(self.scaler, next_value_r, 'Right')
        self.gait_sliderL.setLogicalValue(self.scaler, next_value_l, 'Left')

        for s in consts.side:
            if s == consts.SIDE_LEFT:
                c = 'r'
                x = next_value_l
            else:
                c = 'b'
                x = next_value_r
            for i_j, _ in enumerate(consts.joint):
                # joint canvas
                self.advance_animation_line(None, i_j, s, x, c, 'joint')

                for i_d, _ in enumerate(consts.dim):
                    self.advance_animation_line(i_d, i_j, s, x, c, 'data')
                    self.advance_animation_line(i_d, i_j, s, x, c, 'spm1d')
                    self.advance_animation_line(i_d, i_j, s, x, c, 'mose')

    def advance_animation_line(self, i_d: Optional[int], i_j: int, s: str, x: int, color: str, canvas_type: str):
        mpl_canvas = self.get_target_canvas(canvas_type, i_j, i_d, side=s)
        mpl_canvas.animate_line(self.scaler, x, color)

    def show_study_name(self):
        if self.actionKinematics.isChecked():
            self.label_study.setText('<html><head/><body><p><span style=" font-weight:600;">Kinematics</span> (deg)</p></body></html>')
        else:
            self.label_study.setText('<html><head/><body><p><span style=" font-weight:600;">Moments</span> (Nm/kg)</p></body></html>')

    def display_options_changed(self, action: QAction):
        # TODO This method needs redesign, checks, and maybe moved to controller
        print("Full Redraw requested")
        self.show_raw_data()
        self.show_analysis_result(ankle_x_only=True)
        self.show_study_name()

    def visible_sides_changed(self):
        icon_name_list = [':/images/res/']
        if self.rt_side_checked():
            icon_name_list.append('RT')
        if self.lt_side_checked():
            icon_name_list.append('LT')
        icon_name_list.append('_legSelected.png')
        # self.skeletonlabel.setPixmap(QtGui.QPixmap(":/images/res/RTLT_legSelected.png"))
        self.skeletonlabel.setPixmap(QtGui.QPixmap(''.join(icon_name_list)))

        self.pushButton_0R.setVisible(self.rt_side_checked())
        self.pushButton_1R.setVisible(self.rt_side_checked())
        self.pushButton_2R.setVisible(self.rt_side_checked())
        self.pushButton_0L.setVisible(self.lt_side_checked())
        self.pushButton_1L.setVisible(self.lt_side_checked())
        self.pushButton_2L.setVisible(self.lt_side_checked())

    def show_next_view(self):
        re = QRegExp('stackedWidget[012][012][RL]')
        qlist: List[QObject] = self.findChildren(QStackedWidget, re)
        for widget in qlist:
            widget = cast(QStackedWidget, widget)

            index = widget.currentIndex()
            index += 1
            if index >= widget.count():
                index = 0
            widget.setCurrentIndex(index)
        self.update_legend_selected_panel_name()

    def get_target_canvas(self, canvas_type: str, i_j: int, i_d: Optional[int], side: str) -> MplCanvas:
        if i_d is None:
            mose_canvas = self.findChild(MplCanvas, name=f'{canvas_type}{i_j}{side}')
        else:
            # names are datacanvas00R, mosecanvas01R and spm1dcavcas01R
            mose_canvas = self.findChild(MplCanvas, name=f'{canvas_type}canvas{i_j}{i_d}{side}')
        mose_canvas = cast(MplCanvas, mose_canvas)
        return mose_canvas

    def clear_analysis(self):
        print('clear_analysis')
        self.set_analysis_visible(False)
        self.controller.delete_analysis()
        if self.animator_timer:
            self.animator_timer.stop()

    def clear_all(self):
        print('clear_all')
        self.controller.delete_data()


def draw_mean_std(current_data, ax: Axes, display_format: DisplayFormat):
    current_data_mean = current_data.mean(axis=0)
    err = current_data.std(axis=0)
    print(current_data.shape, current_data_mean.shape, err.shape)
    x = list(range(len(current_data_mean)))
    ax.plot(x, current_data_mean, display_format.line_and_marks(),
            # label=f'{consts.joint[joint]}_{consts.dim[dim]}',
            color=display_format.color())
    y1 = current_data_mean + err
    y2 = current_data_mean - err
    ax.fill_between(x, y1, y2, alpha=0.2, color=display_format.color())
#     print(current_data_mean.shape, ax.lines)
    ax.autoscale(enable=True, axis='both', tight=True)
    # ax.tight_layout()  # AttributeError: 'AxesSubplot' object has no attribute 'tight_layout'


def draw_inference_plot(spm_canvas: MplCanvas, t2i: spm1d.stats._spm.SPMi_T, data_format: DisplayFormat = None):
    ax = spm_canvas.ax
    if data_format:
        t2i.plot(ax=ax, color=data_format.color(), linestyle=data_format.line(), marker=data_format.marks())
        # t2i.plot(ax=ax, color=data_format.color())
    else:
        t2i.plot(ax=ax)
#     spm_canvas.canvas.draw()


def draw_heatmap(target_canvas: MplCanvas, temp_list: List, norm: Normalize=None, cmap: cm=None) -> AxesImage:
    z_array = np.array(temp_list)
    z_array = np.abs(z_array)
    ax: Axes = cast(Axes, target_canvas.ax)
    if cmap is None:
        cmap = cm.get_cmap('coolwarm', 11)  # colormap name and number of quantization levels
        # cmap = cm.get_cmap('jet', 11)  # colormap name and number of quantization levels
        under_color = (0.5, 0.5, 0.5)
        cmap.set_under(color=under_color)
    # norm = colors.BoundaryNorm(np.linspace(0, 10, 11), cmap.N)
    if norm is None:
        norm = Normalize(vmin=1, vmax=4)
    ax.grid(False)
    if len(temp_list) == 2:
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Pre', 'Post'])
    ret = ax.imshow(z_array, interpolation='nearest', cmap=cmap, aspect='auto', norm=norm)

    # colorbar = ax.figure.colorbar(im, ax=ax, orientation="horizontal",
    #                           ticks=[0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5],
    #                           pad=0.2)  # set where to put the tick marks
    ax.autoscale(enable=True, axis='both', tight=True)
    #     target_canvas.canvas.draw()
    return ret

