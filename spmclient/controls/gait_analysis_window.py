from __future__ import annotations

from pathlib import Path
from typing import Dict, cast, List, Optional

from PyQt5 import QtGui
# from PyQt5.Qt import QRegExp
from PyQt5.QtCore import QObject, QTimer, QFile, QIODevice, QTextStream, QRegExp
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QStackedWidget, QAction, QActionGroup, \
    QButtonGroup, QAbstractButton, QWidget, QDialog, QComboBox, QWidgetAction, QMessageBox
from matplotlib import cm
from matplotlib.axes import Axes
from matplotlib.colors import Normalize
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
# print("going to import matplotlib.pyplot as plt")

import matplotlib.pyplot as plt
# print("going to import numpy")
import numpy as np
# print("going to import numpy")
import spm1d
# print("going to import spmclient modules")
from spmclient import consts
from spmclient.controls.colormap_chooser import ColorMapChooser
from spmclient.controls.controller import Controller
from spmclient.models.data_manager import DataManager
from spmclient.models.datasources.datagrapper import load_full_folder
from spmclient.ui.displaymanager import DisplayManager
from spmclient.ui.gui.DisplayFormat import DisplayFormat
from spmclient.ui.gui.xml.customcomponents import MplCanvas, KinematicsScaler, \
    MomentsScaler
from spmclient.ui.gui.xml.ui_about_dialogue import Ui_About
from spmclient.ui.gui.xml.ui_gait_analysis_window import Ui_ui_GaitAnalysisWindow
from spmclient.ui.gui.xml.ui_license_dialog import Ui_license_dialog


class GaitAnalysisWindow(QMainWindow, Ui_ui_GaitAnalysisWindow, DisplayManager):

    def __init__(self, params: Dict, controller: Controller):
        QMainWindow.__init__(self)
        Ui_ui_GaitAnalysisWindow.__init__(self)
        # print("finished calling Ui_ui_GaitAnalysisWindow init")
        self.controller = controller
        self.setupUi(self)
        # print("finished calling setupUi")

        self.data_ligand = dict()

        self.analyse_action_group = QActionGroup(self)
        self.analyse_action_group.setExclusive(False)
        self.analyse_action_group.addAction(self.actionPre_vs_Reference)
        self.analyse_action_group.addAction(self.actionPost_vs_Ref)
        self.analyse_action_group.addAction(self.actionPre_and_Post_Vs_Ref)
        self.analyse_action_group.addAction(self.actionPaired)
        self.analyse_action_group.addAction(self.actionTwo_Sample)
        self.analyse_action_group.triggered[QAction].connect(self.analyse)
        self.action_save_analysis.triggered.connect(self.save_analysis)

        self.measurement_action_group = QActionGroup(self)
        self.measurement_action_group.addAction(self.actionKinematics)
        self.measurement_action_group.addAction(self.actionMoments)
        self.measurement_action_group.setExclusive(True)
        self.actionKinematics.setChecked(params.get(consts.KINEMATICS_CHECKED, False))
        self.actionMoments.setChecked(params.get(consts.MOMENTS_CHECKED, False))
        self.measurement_action_group.triggered[QAction].connect(self.display_options_changed)
        self.set_scaler()

        self.sides_action_group = QActionGroup(self)
        self.sides_action_group.addAction(self.actionRight_Side)
        self.sides_action_group.addAction(self.actionLeft_Side)
        self.sides_action_group.setExclusive(False)
        self.actionRight_Side.setChecked(params.get(consts.RT_SIDE_CHECKED, False))
        self.actionLeft_Side.setChecked(params.get(consts.LT_SIDE_CHECKED, False))
        self.sides_action_group.triggered[QAction].connect(self.visible_sides_changed)

        self.show_hide_joint_button_group = QButtonGroup(self)
        self.show_hide_joint_button_group.setExclusive(False)  # Must be set before adding any buttons
        self.show_hide_joint_button_group.addButton(self.pushButton_0R)
        self.show_hide_joint_button_group.addButton(self.pushButton_1R)
        self.show_hide_joint_button_group.addButton(self.pushButton_2R)
        self.show_hide_joint_button_group.addButton(self.pushButton_0L)
        self.show_hide_joint_button_group.addButton(self.pushButton_1L)
        self.show_hide_joint_button_group.addButton(self.pushButton_2L)
        self.show_hide_joint_button_group.buttonClicked.connect(self.joint_button_clicked)

        self.action_color_Scale.triggered.connect(self.update_color_maps)
        self.action_about.triggered.connect(self.show_about)
        self.action_license.triggered.connect(self.show_license)

        self.current_action: Optional[QAction] = None
        self.alpha = params.get(consts.ALPHA)
        self.alpha_comboBox = QComboBox(self.menu_options)
        self.alpha_comboBox.setEditable(True)
        self.alpha_comboBox.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.alpha_comboBox.setObjectName("alpha_comboBox")
        self.alpha_comboBox.addItem("0.005")
        self.alpha_comboBox.addItem("0.01")
        self.alpha_comboBox.addItem("0.05")
        self.alpha_comboBox.addItem("0.1")
        self.alpha_comboBox.setCurrentIndex(2)
        self.alpha_comboBox.currentTextChanged.connect(self.alpha_updated)
        self.alpha_widget_action = QWidgetAction(self.menu_options)
        self.alpha_widget_action.setDefaultWidget(self.alpha_comboBox)
        self.menu_alpha.addAction(self.alpha_widget_action)

        self.action_specify_normal_standard.triggered.connect(self.load_reference)
        self.action_open_before_intervention_data.triggered.connect(self.load_before_intervention)
        self.action_open_post_intervention_data.triggered.connect(self.load_after_intervention)
        self.action_clear_all.triggered.connect(self.clear_all)
        self.action_clear_analysis.triggered.connect(self.clear_analysis)
        self.actionNextView.triggered.connect(self.show_next_view)

        plt.rcParams['figure.constrained_layout.use'] = True
        self.show_animation_triggered(False)
        self.action_show_animation.triggered[bool].connect(self.show_animation_triggered)

        self.set_analysis_visible(False)
        self.update_actions_enabled()

        self.show_study_name()

        self.animator_timer: QTimer = QTimer(self)
        self.animator_timer.setSingleShot(False)
        self.animator_timer.timeout.connect(self.advance_animation)
        self.action_animate.toggled[bool].connect(self.trigger_animation)

        for j in range(3):
            for s in consts.side:
                joint_canvas = self.get_target_canvas('joint', j, None, side=s)
                # Notice that the canvas is NOT a Widget
                joint_canvas.canvas.mpl_connect('button_press_event', self.vector_canvas_clicked)

        for s in consts.side:
            for j in range(3):
                for d in range(3):
                    spm1d_canvas = self.get_target_canvas('mose', j, d, side=s)
                    spm1d_canvas.set_heights((1, 2, 1))
        self.legend_heatmap_groupbox.setVisible(False)
        self.legend_dock_widget.hide()

    def show_animation_triggered(self, show: bool):
        self.gait_sliderR.setVisible(show)
        self.gait_sliderL.setVisible(show)
        self.update_actions_enabled()
        if not show:
            self.action_animate.setChecked(False)

    def set_analysis_visible(self, show: bool, ankle_x_only: bool = False):
        re = QRegExp('joint[012][RL]')
        qlist: List[QObject] = self.findChildren(MplCanvas, re)
        for widget in qlist:
            # print('set', widget.objectName(), 'visibility to', show)
            if show:
                if ankle_x_only:
                    widget.setVisible(widget.objectName()[-2] != '2')
                else:
                    widget.setVisible(True)
            else:
                widget.setVisible(False)

        re = QRegExp('stackedWidget[0-2][0-2][RL]')
        qlist: List[QObject] = self.findChildren(QStackedWidget, re)
        for widget in qlist:
            # print('set', widget.objectName(), 'visibility to', show)
            if show:
                if ankle_x_only:
                    if widget.objectName()[-3:-1] == '20':
                        widget.setVisible(True)
                    # else leave it unchanged.. This is useful when you show analysis on top of another analysis
            else:
                widget.setVisible(False)

    def joint_button_clicked(self, button: QAbstractButton):
        suffix = button.objectName()[-3:]
        widget = self.findChild(QWidget, 'widget'+suffix)
        widget.setVisible(button.isChecked())

    def vector_canvas_clicked(self, event):
        canvas = event.canvas
        vector_widget = canvas.parent()
        name = vector_widget.objectName()
        joint, side = name[-2], name[-1]
        re = QRegExp(f'stackedWidget{joint}[012]{side}')
        qlist: List[QObject] = self.findChildren(QStackedWidget, re)
        for widget in qlist:
            widget = cast(QStackedWidget, widget)
            widget.setVisible(not widget.isVisible())
        if qlist[0].isVisible():
            widget = cast(QWidget, vector_widget)
            widget.setToolTip("Click to collapse")
        else:
            widget = cast(QWidget, vector_widget)
            widget.setToolTip("Click to expand")

    def rt_side_checked(self):
        return self.actionRight_Side.isChecked()

    def lt_side_checked(self):
        return self.actionLeft_Side.isChecked()

    # TODO merge load_reference, load_before_intervention, load_after_intervention
    def load_reference(self):
        file_dialog = QFileDialog(self)
        # d = Path(__file__).parents[2] / 'res/refDataScaled'
        d = Path(__file__).parents[1] / 'res/refData'
        dir_name = file_dialog.getExistingDirectory(self, caption="Select reference data root folder", directory=str(d))
        if dir_name:
            self.controller.load_data(dir_name, consts.SUBJECT_REF)
            self.update_actions_enabled()

    def load_before_intervention(self):
        file_dialog = QFileDialog(self)
        # d = Path(__file__).parents[2] / 'res/cases/subj1_preResampled'
        d = Path(__file__).parents[1] / 'res/cases/subj1_pre'
        dir_name = file_dialog.getExistingDirectory(self, caption="Select folder of preintervension data", directory=str(d))
        if dir_name:
            self.controller.load_data(dir_name, consts.SUBJECT_B4)
            self.update_actions_enabled()

    # TODO Shouldn't we evacuate it and move its contents to App?
    def load_after_intervention(self):
        file_dialog = QFileDialog(self)
        # d = Path(__file__).parents[2] / 'res/cases/subj1_postResampled'
        d = Path(__file__).parents[1] / 'res/cases/subj1_post'
        dir_name = file_dialog.getExistingDirectory(self, caption="Select folder of postintervension data", directory=str(d))
        if dir_name:
            self.controller.load_data(dir_name, consts.SUBJECT_AFTER)
            self.update_actions_enabled()

    def data_loaded(self, data: Dict):
        # TODO tell that on status bar
        pass

    def add_line_to_ligand(self, current_task: Dict, data_format: DisplayFormat):
        title = f'{current_task[consts.SUBJECT]} {current_task[consts.SIDE]}'
        self.data_ligand[title] = Line2D([0], [0], linestyle=data_format.line_and_marks(), color=data_format.color(), label=title)

    def add_colorbar_to_legend(self, axes_image1, axes_image2):
        print(f'add_colorbar_to_legend({axes_image1}, {axes_image2})')

        cmc = ColorMapChooser()
        figure = self.legend_heatmap_panel.figure
        ax1 = self.legend_heatmap_panel.ax

        ax1.change_geometry(1, 5, 2)
        ax1.clear()

        if axes_image1:
            cmap1 = cmc.cmap1
            norm1 = cmc.norm1
            labels = ['Mild', 'Mod', 'Severe', 'Xtreme']
            for j, lab in enumerate(labels):
                ax1.text(0.9, norm1.vmin + ((2 * j + 1) / (2 * len(labels)) * (norm1.vmax - norm1.vmin)),
                         lab, ha='right', va='center_baseline')

            figure.colorbar(cm.ScalarMappable(norm=norm1, cmap=cmap1), orientation="vertical",
                            cax=ax1, use_gridspec=True, fraction=1.0, shrink=1.0, extend='both',
                            ticks=np.arange(norm1.vmax + 1),
                            # anchor = (0.0, 0.5), panchor = (0.0, 0.5), drawedges=True, pad=0.2
                            )
        else:
            ax1.axis("off")

        cmap2 = cmc.cmap2
        norm2 = cmc.norm2
        # figure = self.legend_heatmap_panel.figure

        for ax in figure.get_axes():
            if 'ax2' == ax.get_label():
                ax2 = ax
                break
        else:  # Loop else (no_break)
            ax2 = figure.add_subplot(1, 5, 4, label='ax2')  # Remember having a unique label.

        ax2.clear()
        #         ax.change_geometry(1, 5, 4)
        # figure.gca().set_axis_off()
        if axes_image2:
            figure.colorbar(cm.ScalarMappable(norm=norm2, cmap=cmap2), orientation="vertical",
                            cax=ax2, use_gridspec=True, fraction=1.0, shrink=1.0, extend='both',
                            ticks=np.arange(norm2.vmax + 1),
                            )
        else:
            ax2.axis("off")
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
        if action:
            self.current_action = action
        else:
            return

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

        ankle_x_only = not DataManager().is_all_ankle_dim_data_available()
        self.controller.analyse_all(analysis, self.alpha, ankle_x_only)

        self.label_analysis.analysis_name = action.toolTip()

    def save_analysis(self):
        file_dialog = QFileDialog(self)
        # d = Path(__file__).parents[1] / 'res/refData'
        dir_name = file_dialog.getExistingDirectory(self,
                        caption="Select folder to save analysis") #, directory=str(d))
        if dir_name:
            self.controller.save_analysis(self.current_action.objectName(), dir_name)

    def analysis_done(self):
        # TODO show that on status bar, and remove any waiting signs
        self.set_analysis_visible(True, ankle_x_only=not DataManager().is_all_ankle_dim_data_available())
        self.update_actions_enabled()

    def save_analysis_done(self):
        # TODO show that on status bar, and remove any waiting signs
        QMessageBox.information(self, "Saved", "analysis data saved successfully")

    def trigger_animation(self, triggered: bool):
        if triggered and self.action_show_animation.isChecked():
            self.animator_timer.start(1500)
            print("Timer started")
        else:
            self.animator_timer.stop()
            print("Timer stopped")

    def update_legend_selected_panel_name(self):
        names = ['Color Bar', 'SPM']
        self.label_analysis.set_selected_widget_name(names[self.stackedWidget00R.currentIndex()])

    def update_color_maps(self):
        cmc = ColorMapChooser()
        choice = cmc.exec()
        if choice:
            self.show_analysis_result()

    def alpha_updated(self, alpha: str):
        # self.alpha = float(self.alpha_comboBox.currentText())
        self.alpha = float(alpha)
        self.analyse(self.current_action)

    def show_about(self):
        about = QDialog(self)
        ui = Ui_About()
        ui.setupUi(about)
        about.exec()

    def show_license(self):
        txt = None
        fd = QFile(":/text/res/LICENSE")
        if fd.open(QIODevice.ReadOnly | QFile.Text):
            txt = QTextStream(fd).readAll()
            fd.close()

        license_dlg = QDialog(self)
        ui = Ui_license_dialog()
        ui.setupUi(license_dlg)
        if txt:
            ui.plainTextEdit.setPlainText(txt)
        else:
            ui.plainTextEdit.setPlainText("ERROR: Can't read the license file (GPL Ver. 3)!")

        license_dlg.exec()

    # def show_rmse(self, task_yb, rmse):
    #     pass

    def show_analysis_result(self, ankle_x_only: bool = False):
        analysis_legend_image1 = None
        analysis_legend_image2 = None

        self.set_scaler()

        cmc = ColorMapChooser()
        cmap1 = cmc.cmap1
        norm1 = cmc.norm1
        cmap2 = cmc.cmap2
        norm2 = cmc.norm2

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

                            analysis_legend_image1 = draw_heatmap(mose_canvas, temp_display_data, norm=norm1, cmap=cmap1)
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
                        analysis_legend_image2 = draw_heatmap(joint_canvas, temp_display_data, norm=norm2, cmap=cmap2)
                        # Add vertical line
                        if self.actionKinematics.isChecked():
                            joint_canvas.ax.axvline(x=60, linewidth=4, color='k', ls='--', lw=1.5)
                joint_canvas.canvas.draw()

        self.update_legend_selected_panel_name()
        self.add_colorbar_to_legend(analysis_legend_image1, analysis_legend_image2)
        self.legend_heatmap_groupbox.setVisible(True)
        self.action_animate.setEnabled(True)
        if self.action_show_animation.isChecked():
            self.action_animate.setChecked(True)

    # def set_ankle_x_only_visible(self, ankle_x_only: bool):
    #     reg = QRegExp('(stackedWidget[2][12][RL])|(joint2[RL])')
    #     q_list: List[QObject] = self.findChildren(QStackedWidget, reg)
    #     for widget in q_list:
    #         widget.setVisible(True)

    def set_scaler(self):
        if self.actionKinematics.isChecked():
            self.scaler = KinematicsScaler()
        else:
            self.scaler = MomentsScaler()

    def advance_animation(self):
        current_value = self.gait_sliderR.logicalValue()
        next_value_r = (current_value % 100) + 5  # * 2  # 5  # in the period [5, 100]
        next_value_l = ((next_value_r + 45) % 100) + 5  #  ((next_value_r - 5 + 50) % 100) + 5
        # print('Next values', next_value_r, '\t', next_value_l)
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
            self.label_study.setText('<html><head/><body><p><span style=" font-weight:600;">Kinematics</span> (% Stride deg)</p></body></html>')
        else:
            self.label_study.setText('<html><head/><body><p><span style=" font-weight:600;">Moments</span> (% Stance Nm/kg)</p></body></html>')

    def display_options_changed(self, action: QAction):
        # TODO This method needs redesign, checks, and maybe moved to controller
        print("Full Redraw requested")
        self.show_raw_data()
        self.show_analysis_result(ankle_x_only=not DataManager().is_all_ankle_dim_data_available())
        self.show_study_name()

    def visible_sides_changed(self, last_triggered_action: QAction):
        if not (self.actionRight_Side.isChecked() or self.actionLeft_Side.isChecked()):
            last_triggered_action.setChecked(True)
            # return
        icon_name_list = [':/images/res/']
        if self.rt_side_checked():
            icon_name_list.append('RT')
        if self.lt_side_checked():
            icon_name_list.append('LT')
        icon_name_list.append('_legSelected.png')
        self.skeletonlabel.setPixmap(QtGui.QPixmap(''.join(icon_name_list)))

        self.pushButton_0R.setVisible(self.rt_side_checked())
        self.pushButton_1R.setVisible(self.rt_side_checked())
        self.pushButton_2R.setVisible(self.rt_side_checked())
        self.pushButton_0L.setVisible(self.lt_side_checked())
        self.pushButton_1L.setVisible(self.lt_side_checked())
        self.pushButton_2L.setVisible(self.lt_side_checked())

    def show_next_view(self):
        reg = QRegExp('stackedWidget[012][012][RL]')
        qlist: List[QObject] = self.findChildren(QStackedWidget, reg)
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
        self.current_action = None
        self.set_analysis_visible(False)
        self.controller.delete_analysis()
        self.update_actions_enabled()
        self.legend_heatmap_groupbox.setVisible(False)

    def clear_all(self):
        print('clear_all')
        self.controller.delete_data()
        self.clear_analysis()
        # self.update_actions_enabled()

    def update_actions_enabled(self):
        ref_available = DataManager.is_data_available(consts.SUBJECT_REF)
        pre_available = DataManager.is_data_available(consts.SUBJECT_B4)
        post_available = DataManager.is_data_available(consts.SUBJECT_AFTER)

        self.actionPre_vs_Reference.setEnabled(ref_available and pre_available)
        self.actionPost_vs_Ref.setEnabled(ref_available and post_available)
        self.actionPre_and_Post_Vs_Ref.setEnabled(ref_available and pre_available and post_available)
        self.actionPaired.setEnabled(pre_available and post_available)
        self.actionTwo_Sample.setEnabled(pre_available and post_available)

        if not (ref_available or pre_available or post_available):
            self.action_animate.setChecked(False)
        self.action_animate.setEnabled(self.action_show_animation.isChecked() and (ref_available or pre_available or post_available))

        self.action_save_analysis.setEnabled(DataManager.is_analysis_available(None))


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
    ax.grid(False)
    if len(temp_list) == 2:
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Pre', 'Post'])
    ret = ax.imshow(z_array, interpolation='nearest', cmap=cmap, aspect='auto', norm=norm)

    ax.autoscale(enable=True, axis='both', tight=True)
    return ret

