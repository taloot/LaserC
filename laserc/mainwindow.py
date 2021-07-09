from qtpyvcp.widgets.form_widgets.main_window import VCPMainWindow

from PyQt5 import Qt
from PyQt5.QtCore import QIODevice, QFile, QTextStream, QByteArray, pyqtSlot, QTimer
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QBoxLayout
from PyQt5.QtGui import QDoubleValidator, QIntValidator

from pyqtgraph import PlotWidget, plot, PlotItem
import pyqtgraph as pg
from myDialog import MyDialog

from functools import partial

from qtpyvcp.utilities import logger
LOG = logger.getLogger('qtpyvcp.' + __name__)

import os
import sys
import unicodedata
import hal
import math
import time
from subprocess import Popen,PIPE

lasercomp = hal.component('lasercomp')

#hal interface pins
lasercomp.newpin('laserc_arc_on_bit', hal.HAL_BIT, hal.HAL_IN)
lasercomp.newpin('laserc_plasmac_status', hal.HAL_S32, hal.HAL_IN)
lasercomp.newpin('laserc_o2_regulator_pwm', hal.HAL_FLOAT, hal.HAL_OUT)
lasercomp.newpin('laserc_n2_switch_bit', hal.HAL_BIT, hal.HAL_OUT)
lasercomp.newpin('laserc_headcooling_switch_bit', hal.HAL_BIT, hal.HAL_OUT)
lasercomp.newpin('laserc_pwm_pwmgen', hal.HAL_FLOAT, hal.HAL_OUT)
lasercomp.newpin('float_switch', hal.HAL_BIT, hal.HAL_OUT)
# lasercomp.newpin('laserc_pwr_pwmgen', hal.HAL_FLOAT, hal.HAL_OUT)
lasercomp.newpin('laserc_pwr_freq', hal.HAL_FLOAT, hal.HAL_OUT)
lasercomp.newpin('laserc_ok_bit', hal.HAL_BIT, hal.HAL_OUT)
lasercomp.newpin('laserc_focus', hal.HAL_S32, hal.HAL_OUT)
lasercomp.newpin('laserc_velocity_x', hal.HAL_FLOAT, hal.HAL_IN)
lasercomp.newpin('laserc_velocity_y', hal.HAL_FLOAT, hal.HAL_IN)
lasercomp.newpin('laserc_232pwr_output', hal.HAL_FLOAT, hal.HAL_OUT)


lasercomp.newpin('laserc_start_set', hal.HAL_BIT, hal.HAL_OUT)
lasercomp.newpin('laserc_en_set', hal.HAL_BIT, hal.HAL_OUT)

lasercomp.newpin('laserc_cut_speed', hal.HAL_FLOAT, hal.HAL_OUT)
lasercomp.newpin('laserc_cut_height', hal.HAL_FLOAT, hal.HAL_IN)
lasercomp.newpin('laserc_pierce_delay', hal.HAL_FLOAT, hal.HAL_IN)
lasercomp.newpin('laserc_pierce_height', hal.HAL_FLOAT, hal.HAL_IN)
lasercomp.newpin('laserc_o2h_pressure', hal.HAL_FLOAT, hal.HAL_IN)
lasercomp.newpin('laserc_o2l_pressure', hal.HAL_FLOAT, hal.HAL_IN)
lasercomp.newpin('laserc_n2_pressure', hal.HAL_FLOAT, hal.HAL_IN)
lasercomp.newpin('laserc_en_status', hal.HAL_BIT, hal.HAL_IN)
lasercomp.newpin('laserc_pwm_status', hal.HAL_BIT, hal.HAL_IN)
lasercomp.newpin('encoder_velocity', hal.HAL_FLOAT, hal.HAL_IN)

# button start 
lasercomp.newpin('laserc_start_en_set', hal.HAL_BIT, hal.HAL_OUT)

#for test
lasercomp.newpin('laserc_velocity', hal.HAL_FLOAT, hal.HAL_OUT)

lasercomp.ready()

limit_velocity = 11500

class MyMainWindow(VCPMainWindow):
    """Main window class for the VCP."""
    def __init__(self, *args, **kwargs):
        super(MyMainWindow, self).__init__(*args, **kwargs)
        hal.connect('lasercomp.laserc_plasmac_status', 'plasmac:state')
        # hal.connect('lasercomp.laserc_cut_speed', 'plasmac:cut-feed-rate')
        # hal.connect('lasercomp.laserc_cut_height', 'plasmac:cut-height')
        # hal.connect('lasercomp.laserc_pierce_delay', 'plasmac:pierce-delay')
        # hal.connect('lasercomp.laserc_pierce_height', 'plasmac:pierce-height')
        # hal.connect('lasercomp.laserc_velocity_x','laserc:velocity_x')
        # hal.connect('lasercomp.laserc_velocity_y','laserc:velocity_y')
        # hal.connect('lasercomp.laserc_headcooling_switch_bit','lasercomp:laserc-headcooling-switch-bit')
        hal.connect('lasercomp.float_switch', 'plasmac:float-switch-out')
        hal.connect('lasercomp.encoder_velocity', 'encoder:velocity')
        hal.connect('lasercomp.laserc_o2_regulator_pwm','lasercomp:laserc-o2-regulator-pwm')
        hal.connect('lasercomp.laserc_pwm_pwmgen','lasercomp:laserc-pwr-pwmgen')
        # hal.connect('lasercomp.laserc_pwr_pwmgen','lasercomp:laserc-pwm24v-duty')
        hal.connect('lasercomp.laserc_pwr_freq','lasercomp:laserc-pwm24v-freq')
        hal.connect('lasercomp.laserc_n2_switch_bit','lasercomp:laserc-n2-switch-bit')
        
        #---
        hal.connect('lasercomp.laserc_start_en_set','lasercomp:laser-start-en-status')
        ##
        hal.connect('lasercomp.laserc_start_set','laser232:laser-start-status')
        hal.connect('lasercomp.laserc_en_set','laser232:laser-en-status')
        
        #
        hal.set_p('axis.a.eoffset-scale', '1')
        hal.set_p('axis.a.eoffset-enable', 'True')
        hal.new_sig('lasercomp:focus', hal.HAL_S32)
        hal.connect('lasercomp.laserc_focus', 'lasercomp:focus')
        hal.connect('axis.a.eoffset-counts', 'lasercomp:focus')
        
        self.laserc_cutting_status = 0
        self.laserc_piercing_status = 0
        self.laserc_marking_status = 0
        self.laserc_probing_status = 0
        self.laserc_ok_bit_value = False
        self.laserc_start_status_value = False
        self.laserc_en_status_value = False
        self.laserc_pwm_status_value = False
        self.gas_puffing_status = False
        self.setting_started = False
        self.head_cooling_time = 0
        self.laserc_velocity_value = 0
        self.laser232_control_mode = 1
        self.laseron_status = False
        self.laser232_pwr = 0
        self.timer = QTimer(self)

        self.set_cut_speed()
        self.timer.stop()
        self.timer.start(16)
        self.laser232_state_change()
        self.setting_started = True

        self.timer.timeout.connect(self.monitor_refresh)
        self.Setup()

    def Setup(self):
        self.setWindowTitle("LaserC")
        self.configureCurveGraph()
        self.m_btn_open.clicked.connect(partial(self.openFile))
        self.m_btn_save.clicked.connect(partial(self.saveFile))
        self.m_btn_cut_curve.clicked.connect(partial(self.openCurveDialog))
        #self.m_btn_start.clicked.connect(partial(self.slotStart))
        #self.m_btn_stop.clicked.connect(partial(self.slotStop))
        self.m_btn_puff.clicked.connect(partial(self.slotPuff))
        self.m_spin_cut_cur_rate.valueChanged.connect(partial(self.slot_cut_cur_rate_changed))
        self.m_spin_pierce_cur_rate.valueChanged.connect(partial(self.slot_pierce_cur_rate_changed))
        self.m_slider_air_head_time.valueChanged.connect(partial(self.slot_air_head_time))
        self.m_slider_pufftime.valueChanged.connect(partial(self.slot_pufftime_changed))
        self.m_slider_laserpwr.valueChanged.connect(partial(self.slot_laserpwr_changed))
        self.m_btn_laserpwr.clicked.connect(partial(self.slot_laserpwr_apply))
        self.m_check_cut_pwr.clicked.connect(partial(self.slot_dyn_pwr))
        self.m_check_cut_freq.clicked.connect(partial(self.slot_dyn_freq))
        self.m_btn_laseron.clicked.connect(partial(self.slot_laseron))

        self.m_btn_laserstartstatus.clicked.connect(partial(self.slot_laserstartstatus))
        #self.m_btn_laserenstatus.clicked.connect(partial(self.slot_laserenstatus))
        #self.m_led_cuttingstatus.valueChanged.connect(partial(self.slot_led_cutting_changed))
        self.get_laserc_parameters()

        self.m_spin_cut_cur_rate.setValue(100)
        self.m_spin_pierce_cur_rate.setValue(100)

    def laser232_state_change(self):
        comport = '/dev/ttyUSB0'
        if os.path.exists(comport) and os.access(comport, os.W_OK | os.R_OK | os.X_OK):
            if not hal.component_exists('laser232'):
                Popen('halcmd loadusr -Wn laser232 /home/tal/laserc/laserc/laser232.py {}'.format(comport), stdout = PIPE, shell = True)
                self.m_label_workingstatus.setText('No Connect')
                self.m_label_workingstatus.setStyleSheet('color:red; font-size:20pt')
                # self.m_tab_monitor.setEnabled(False)
                if hal.component_exists('laser232'):
                    hal.set_p('laser232.enable', 'True')
                    self.m_label_workingstatus.setText('Normal')
                    self.m_label_workingstatus.setStyleSheet('color:green; font-size:20pt')
                    self.m_tab_monitor.setEnabled(True)
            else:
                hal.set_p('laser232.enable', 'True')
                self.m_label_workingstatus.setText('Normal')
                self.m_label_workingstatus.setStyleSheet('color:green; font-size:20pt')
                self.m_tab_monitor.setEnabled(True)
        else:
            if hal.component_exists('laser232'):
                hal.set_p('laser232.enable', 'False')
            self.m_label_workingstatus.setText('No Connect')
            self.m_label_workingstatus.setStyleSheet('color:red; font-size:20pt')
            # self.m_tab_monitor.setEnabled(False)


    def configureCurveGraph(self):
        self.m_chart = pg.PlotWidget()
        self.m_chart.setMouseEnabled(False, False)
        self.chart_layout = QBoxLayout(QBoxLayout.RightToLeft, self)
        self.chart_layout.addWidget(self.m_chart)
        self.m_widget_chart.setLayout(self.chart_layout)

        self.speed1 = [10, 80]
        self.power = [50, 80]
        self.speed2 = [40, 45]
        self.frequency = [20, 70]

        speed1_draw = [0]
        speed2_draw = [0]
        power_draw = [self.power[0]]
        frequency_draw = [self.frequency[0]]
        j = 0
        for i in self.speed1:
            speed1_draw.append(self.speed1[j])            
            speed2_draw.append(self.speed2[j])            
            frequency_draw.append(self.frequency[j])            
            power_draw.append(self.power[j])
            j+=1
        speed1_draw.append(100)
        speed2_draw.append(100)
        power_draw.append(self.power[-1])
        frequency_draw.append(self.frequency[-1])

        self.pierce_totalparam = [self.speed1, self.power, self.speed2, self.frequency]

        self.m_chart.setBackground('w')
        if self.m_check_cut_pwr.isChecked():
            self.draw_line(speed1_draw, power_draw, "power", 'b')
        if self.m_check_cut_freq.isChecked():
            self.draw_line(speed2_draw, frequency_draw, "frequency", 'g')

        styles = {'color':'r', 'font-size':'10px'}
        self.m_chart.setLabel('left', 'Power(%)', **styles)
        self.m_chart.setLabel('bottom', 'Speed(%)', **styles)
        self.m_chart.showGrid(x=True, y=True)

    def draw_line(self, x, y, plotname, color):
        pen = pg.mkPen(color=color)
        self.m_chart.plot(x, y, name=plotname, pen=pen)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file...", "/home", "Setting files (*.fsm)")
        if fileName == u'':
            return
        f = open(fileName, 'r')
        openstr = f.read()
        f.close()
        material = openstr.split('\n')[0]
        thickness = openstr.split('\n')[1]
        nozzle = openstr.split('\n')[2]
        self.m_spin_cut_speed.setValue(float(openstr.split('\n')[3]))
        self.m_spin_cut_height.setValue(float(openstr.split('\n')[4]))
        self.m_spin_cut_gas.setCurrentIndex(int(openstr.split('\n')[5]))
        self.m_spin_cut_pressure.setValue(float(openstr.split('\n')[6]))
        self.m_spin_cut_cur_rate.setValue(float(openstr.split('\n')[7]))
        self.m_spin_cut_pwr.setValue(float(openstr.split('\n')[8]))
        self.m_spin_cut_freq.setValue(float(openstr.split('\n')[9]))
        self.m_spin_cut_focus.setValue(float(openstr.split('\n')[10]))
        self.m_spin_pierce_delay.setValue(float(openstr.split('\n')[11]))
        self.m_spin_pierce_height.setValue(float(openstr.split('\n')[12]))
        self.m_spin_pierce_gas.setCurrentIndex(int(openstr.split('\n')[13]))
        self.m_spin_pierce_pressure.setValue(float(openstr.split('\n')[14]))
        self.m_spin_pierce_cur_rate.setValue(float(openstr.split('\n')[15]))
        self.m_spin_pierce_pwr.setValue(float(openstr.split('\n')[16]))
        self.m_spin_pierce_freq.setValue(float(openstr.split('\n')[17]))
        self.m_spin_pierce_focus.setValue(float(openstr.split('\n')[18]))

        self.speed1[0] = float(openstr.split('\n')[19])
        self.speed1[0] = float(openstr.split('\n')[20])
        self.power[0] = float(openstr.split('\n')[21])
        self.power[1] = float(openstr.split('\n')[22])
        self.speed2[0] = float(openstr.split('\n')[23])
        self.speed2[1] = float(openstr.split('\n')[24])
        self.frequency[0] = float(openstr.split('\n')[25])
        self.frequency[1] = float(openstr.split('\n')[26])

        self.m_combo_materials.setText(material.decode('utf-8'))
        self.m_combo_thickness.setText(thickness.decode('utf-8'))
        self.m_combo_nozzle.setText(nozzle.decode('utf-8'))

        


    def saveFile(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save file...", "/home", "Setting files (*.fsm)")
        if fileName == u'':
            return
        material = self.m_combo_materials.text()
        thickness = self.m_combo_thickness.text()
        nozzle = self.m_combo_nozzle.text()

        savestr = (material + "\n" + thickness + "\n" + nozzle + "\n" 
            + str(self.m_spin_cut_speed.value()) + "\n" 
            + str(self.m_spin_cut_height.value()) + "\n" 
            + str(self.m_spin_cut_gas.currentIndex()) + "\n" 
            + str(self.m_spin_cut_pressure.value()) + "\n" 
            + str(self.m_spin_cut_cur_rate.value()) + "\n" 
            + str(self.m_spin_cut_pwr.value()) + "\n" 
            + str(self.m_spin_cut_freq.value()) + "\n" 
            + str(self.m_spin_cut_focus.value()) + "\n" 
            + str(self.m_spin_pierce_delay.value()) + "\n" 
            + str(self.m_spin_pierce_height.value()) + "\n" 
            + str(self.m_spin_pierce_gas.currentIndex()) + "\n" 
            + str(self.m_spin_pierce_pressure.value()) + "\n" 
            + str(self.m_spin_pierce_cur_rate.value()) + "\n" 
            + str(self.m_spin_pierce_pwr.value()) + "\n" 
            + str(self.m_spin_pierce_freq.value()) + "\n" 
            + str(self.m_spin_pierce_focus.value()) + "\n" 
            + str(self.speed1[0]) + "\n" 
            + str(self.speed1[1]) + "\n" 
            + str(self.power[0]) + "\n" 
            + str(self.power[1]) + "\n" 
            + str(self.speed2[0]) + "\n" 
            + str(self.speed2[1]) + "\n" 
            + str(self.frequency[0]) + "\n" 
            + str(self.frequency[1]))
        f = open(fileName, 'w')
        f.write(savestr.encode('utf-8'))
        f.close()

    # def slotStart(self):
        
        

    # def slotStop(self):
    #     if hal.component_exists('laser232'):
    #         hal.set_p('laser232.enable', 'False')
    #     self.setting_started = False
    #     self.set_laserc_parameters(0)
    #     self.get_laserc_parameters()
    #     self.timer.stop()

    def openCurveDialog(self):
        sparam_part1 = self.m_spin_cut_speed.text()
        sparam_part2 = str(self.m_spin_cut_cur_pwr.value()*self.m_spin_cut_pwr.value()*0.01)
        sparam_part3 = self.m_spin_cut_freq.text()
        sparam = [sparam_part1, sparam_part2, sparam_part3]
        self.cut_totalparam = [self.speed1, self.power, self.speed2, self.frequency]
        self.p_dialog = MyDialog(self.cut_totalparam, sparam)
        self.p_dialog.return_ok.connect(partial(self.slot_return_p_dialog))
        self.p_dialog.exec_()

    def power_calc_curve(self, speed):
        if speed <= self.speed1[0]:
            return self.power[0]
        elif speed >= self.speed1[1]:
            return self.power[1]
        else:
            return (self.power[1]-self.power[0])/(self.speed1[1]-self.speed1[0])*(speed - self.speed1[0]) + self.power[0]
        
    def freq_calc_curve(self, speed):
        if speed <= self.speed2[0]:
            return self.frequency[0]
        elif speed >= self.speed2[1]:
            return self.speed2[1]
        else:
            return (self.frequency[1]-self.frequency[0])/(self.speed2[1]-self.speed2[0])*(speed  - self.speed2[0]) + self.frequency[0]

    @pyqtSlot(list, list, list, list)
    def slot_return_p_dialog(self, list1, list2, list3, list4):
        self.speed1 = list1
        self.power = list2
        self.speed2 = list3
        self.frequency = list4
        self.m_chart.clear()
        speed1_draw = [0]
        speed2_draw = [0]
        power_draw = [self.power[0]]
        frequency_draw = [self.frequency[0]]
        j = 0
        for i in self.speed1:
            speed1_draw.append(self.speed1[j])            
            speed2_draw.append(self.speed2[j])            
            frequency_draw.append(self.frequency[j])            
            power_draw.append(self.power[j])
            j+=1
        speed1_draw.append(100)
        speed2_draw.append(100)
        power_draw.append(self.power[-1])
        frequency_draw.append(self.frequency[-1])
        if self.m_check_cut_pwr.isChecked():
            self.draw_line(speed1_draw, power_draw, "power", 'r')
        if self.m_check_cut_freq.isChecked():
            self.draw_line(speed2_draw, frequency_draw, "frequency", 'b')
    
    def monitor_refresh(self):
        self.laser232_state_change()
        self.get_laserc_parameters()
        self.set_laserc_parameters(self.setting_started)
        # gas puff time slider
        if self.gas_puffing_status:
            if self.m_slider_pufftime.value() > 16:
                self.m_slider_pufftime.setValue(self.m_slider_pufftime.value()-16)
            else:
                self.m_slider_pufftime.setValue(0)
                self.gas_puffing_status = False

        # head cooling time
        if self.head_cooling_time > 16:
            self.head_cooling_time = self.head_cooling_time -16
        else:
            self.head_cooling_time = 0
        
        # for test
        lasercomp.laserc_velocity = self.laserc_velocity_value

    ###########################################
    # get parameters , show value and set led #
    ###########################################
    def get_plasmac_status(self):
        # get plasmac status
        self.laserc_cutting_status = (lasercomp.laserc_plasmac_status==11)
        self.laserc_piercing_status = ((lasercomp.laserc_plasmac_status>=7) and (lasercomp.laserc_plasmac_status<=10))
        self.laserc_marking_status = (lasercomp.laserc_plasmac_status==20)
        self.laserc_probing_status = ((lasercomp.laserc_plasmac_status==2) or (lasercomp.laserc_plasmac_status==19))
        # leds set for plasmac status
        self.m_led_cuttingstatus.setState(self.laserc_cutting_status)
        self.m_led_piercingstatus.setState(self.laserc_piercing_status)
        self.m_led_markingstatus.setState(self.laserc_marking_status)
        
    def get_cut_speed_height(self):
        # get cut speed and height
        self.m_spin_cut_height.setValue(lasercomp.laserc_cut_height)

    def get_pierce_delay_height(self):
        # get pierce dealy and height
        self.m_spin_pierce_delay.setValue(lasercomp.laserc_pierce_delay)
        self.m_spin_pierce_height.setValue(lasercomp.laserc_pierce_height)
    
    def get_gas_pressure_value(self):
        self.m_lcd_ohpressure.setValue(lasercomp.laserc_o2h_pressure)
        self.m_lcd_olpressure.setValue(lasercomp.laserc_o2l_pressure)
        self.m_lcd_npressure.setValue(lasercomp.laserc_n2_pressure)
    
    def get_laser232_parameters(self):
        if hal.component_exists('laser232'):
            self.laser232_control_mode = hal.get_value('laser232.laser_control_mode')
            if self.laser232_control_mode == 0 :
                self.m_label_operatingmode.setText('TEST')
                self.m_label_operatingmode.setStyleSheet('color:green; font-size:20pt')
            elif self.laser232_control_mode == 1 :
                self.m_label_operatingmode.setText('ROBOT')
                self.m_label_operatingmode.setStyleSheet('color:green; font-size:20pt')
            elif self.laser232_control_mode == 2 :
                self.m_label_operatingmode.setText('RS232')
                self.m_label_operatingmode.setStyleSheet('color:green; font-size:20pt')
            else:
                self.m_label_operatingmode.setText('OFF')
                self.m_label_operatingmode.setStyleSheet('color:red; font-size:20pt')

            self.m_lcd_emoduletemp.setValue(float(hal.get_value('laser232.electrical_part_temperature'))/100)
            self.m_lcd_emodulehum.setValue(float(hal.get_value('laser232.electrical_part_humidness'))/100)
            self.m_lcd_dboardvol1.setValue(float(hal.get_value('laser232.driver_board_voltage1'))*69.3/4096)
            self.m_lcd_dboardvol2.setValue(float(hal.get_value('laser232.driver_board_voltage2'))*69.3/4096)
            self.m_lcd_reflectiveda.setValue(float(hal.get_value('laser232.reflective_laser_daval'))*3.3/4096)
            self.m_lcd_tempsensor1.setValue(float(hal.get_value('laser232.temperature_sensor1')))
            self.m_lcd_tempsensor2.setValue(float(hal.get_value('laser232.temperature_sensor2')))
            self.m_lcd_tempsensor3.setValue(float(hal.get_value('laser232.temperature_sensor3')))
            self.m_label_currentpower.setText(str(hal.get_value('laser232.laser_power_read')) + '%')
            self.m_label_currentpower.setStyleSheet('color:red; font-size:20pt')
            self.m_label_date.setText(str(hal.get_value('laser232.machine_date_year')) +
                    '/' + str(hal.get_value('laser232.machine_date_month')) + 
                    '/' + str(hal.get_value('laser232.machine_date_day')) + '   '
                    + '{:02d}'.format(hal.get_value('laser232.machine_time_hour')) + 
                    ':' + '{:02d}'.format(hal.get_value('laser232.machine_time_minute')))
            self.laseron_status = hal.get_value('laser232.laser_on_off')
            
            #/*--- both 
            
            self.laserc_en_status_value = hal.get_value('laser232.laser_en_status')
            self.laserc_start_status_value = hal.get_value('laser232.laser_start_status')
            #self.laserc_en_status_value = hal.get_value('laser232.laser_start_en_both')
            #self.laserc_start_status_value = hal.get_value('laser232.laser_start_en_both')
            #---*/
            self.laserc_pwm_status_value = hal.get_value('laser232.laser_pwm_status')

            # leds set for laserc status
            self.m_led_laserstartstatus.setState(self.laserc_start_status_value)
            self.m_led_laserenstatus.setState(self.laserc_en_status_value)
            self.m_led_laserpwmstatus.setState(self.laserc_pwm_status_value)
            self.laserc_ok_bit_value = (self.laserc_start_status_value and self.laserc_en_status_value and self.laserc_pwm_status_value)
            self.m_led_laser_ok.setState(self.laserc_ok_bit_value)

            # button state
            if self.laser232_control_mode == 3 :
                self.m_btn_laserstartstatus.setEnabled(0)
                self.m_btn_laserenstatus.setEnabled(0)
            else:
                self.m_btn_laserstartstatus.setEnabled(1)
                self.m_btn_laserenstatus.setEnabled(1)
            
            self.m_btn_laseron.setEnabled(self.laserc_ok_bit_value)

            if self.laseron_status:
                self.m_btn_laseron.setText("Laser Off")
            else:
                self.m_btn_laseron.setText("Laser On")
            
            if self.laserc_start_status_value:
                self.m_btn_laserstartstatus.setText("Off")
            else:
                self.m_btn_laserstartstatus.setText("On")
            
            if self.laserc_en_status_value:
                self.m_btn_laserenstatus.setText("Off")
            else:
                self.m_btn_laserenstatus.setText("On")

    def get_laserc_parameters(self):
        self.get_plasmac_status()
        self.get_cut_speed_height()
        self.get_pierce_delay_height()
        self.get_gas_pressure_value()
        self.get_laser232_parameters()
        
    ##########################################
    # set parameters                         #
    ##########################################
    def set_gas_puffing_status(self, start_stop):
        if start_stop:
            if (self.m_slider_pufftime.value() != 0) and self.gas_puffing_status:
                self.gas_puffing_status = True
            else:
                self.gas_puffing_status = False
        else:
            self.gas_puffing_status = False

    # set Pin float-switch
    def set_float_switch_bit(self, start_stop):
        if start_stop:
            if self.laserc_probing_status:
                # if (lasercomp.encoder_velocity >= (self.m_spin_float_value.value()-self.m_spin_float_tolerance.value())) and (lasercomp.encoder_velocity <= (self.m_spin_float_value.value()+self.m_spin_float_tolerance.value())):
                if lasercomp.encoder_velocity <= (self.m_spin_float_value.value()+self.m_spin_float_tolerance.value()):
                    lasercomp.float_switch = True
                else:
                    lasercomp.float_switch = False
            else:
                lasercomp.float_switch = False
        else:
            lasercomp.float_switch = False

    # set Pin laserc_ok_bit
    def set_laserc_ok_bit(self, start_stop):
        if start_stop:
            lasercomp.laserc_ok_bit = self.laserc_ok_bit_value
        else:
            lasercomp.laserc_ok_bit = False

    # set Pin laserc_o2_regulator_pwm
    def set_o2_regulator_pwm(self, start_stop):
        if start_stop:
            if self.laserc_cutting_status:
                lasercomp.laserc_o2_regulator_pwm = (self.m_spin_cut_pressure.value()*100/7)+1000
                self.m_led_ohstatus.setState(0)
                self.m_led_olstatus.setState(1)
            elif self.laserc_piercing_status and (self.m_spin_pierce_gas.currentIndex() == 0):
                lasercomp.laserc_o2_regulator_pwm = (self.m_spin_pierce_pressure.value()*100/7)+1000
                self.m_led_ohstatus.setState(1)
                self.m_led_olstatus.setState(0)
            #for test
            elif self.gas_puffing_status and (self.m_combo_gastype.currentIndex() == 0):
                lasercomp.laserc_o2_regulator_pwm = 1400
                self.m_led_ohstatus.setState(1)
                self.m_led_olstatus.setState(0)
            elif self.gas_puffing_status and (self.m_combo_gastype.currentIndex() == 1):
                lasercomp.laserc_o2_regulator_pwm = 1200
                self.m_led_ohstatus.setState(0)
                self.m_led_olstatus.setState(1)
            else:
                lasercomp.laserc_o2_regulator_pwm = 1000
                self.m_led_ohstatus.setState(0)
                self.m_led_olstatus.setState(0)
        else:
            lasercomp.laserc_o2_regulator_pwm = 0
            self.m_led_ohstatus.setState(0)
            self.m_led_olstatus.setState(0)

    # set Pin laserc_n2_switch_bit
    def set_n2_switch_bit(self, start_stop):
        if start_stop:
            if self.laserc_piercing_status and (self.m_spin_pierce_gas.currentIndex() == 1):
                lasercomp.laserc_n2_switch_bit = True
                self.m_led_nstatus.setState(1)
            #for test
            elif self.gas_puffing_status and (self.m_combo_gastype.currentIndex() == 2):
                lasercomp.laserc_n2_switch_bit = True
                self.m_led_nstatus.setState(1)
            else:
                lasercomp.laserc_n2_switch_bit = False
                self.m_led_nstatus.setState(0)
        else:
            lasercomp.laserc_n2_switch_bit = False
            self.m_led_nstatus.setState(0)

    # set Pin laserc_headcooling_switch_bit
    def set_headcooling_switch_bit(self, start_stop):
        if start_stop:
            if self.laserc_cutting_status:
                self.head_cooling_time = self.m_slider_air_head_time.value()
                lasercomp.laserc_headcooling_switch_bit = False
            else:
                if (self.head_cooling_time != 0):
                    lasercomp.laserc_headcooling_switch_bit = True
                else:
                    lasercomp.laserc_headcooling_switch_bit = False
        else:
            if (self.head_cooling_time != 0):
                lasercomp.laserc_headcooling_switch_bit = True
            else:
                lasercomp.laserc_headcooling_switch_bit = False
    
    # set Pin laserc_pwm_pwmgen
    def set_pwm_pwmgen(self, start_stop):
        if start_stop & (self.m_combo_mode.currentIndex() == 1):
            if self.laserc_cutting_status:
                lasercomp.laserc_pwm_pwmgen = (self.m_spin_cut_cur_rate.value()*100/7)+1000
            elif self.laserc_piercing_status:
                lasercomp.laserc_pwm_pwmgen = (self.m_spin_pierce_cur_rate.value()*100/7)+1000
            else:
                lasercomp.laserc_pwm_pwmgen = 0
        else:
            lasercomp.laserc_pwm_pwmgen = 0
    
    # set Pin laser232.laser_power_set
    def set_laser232_power_set(self, start_stop):
        if hal.component_exists('laser232'):
            if start_stop & (self.m_combo_mode.currentIndex() == 0):
                if self.laserc_cutting_status:
                    hal.set_p('laser232.laser_power_set', str(self.m_spin_cut_cur_rate.value()))
                elif self.laserc_piercing_status:
                    hal.set_p('laser232.laser_power_set', str(self.m_spin_pierce_cur_rate.value()))
                else:
                    hal.set_p('laser232.laser_power_set', str(self.laser232_pwr))
            else:
                hal.set_p('laser232.laser_power_set', '0')
    
    # set Pin laserc_pwr_pwmgen
    def set_pwr_pwmgen(self, start_stop):
        if hal.component_exists('hostmot2'):
            if start_stop & (self.m_combo_mode.currentIndex() == 1):
                if self.laserc_cutting_status:
                    if self.m_check_cut_pwr.isChecked():
                        self.laserc_velocity_value = math.sqrt(math.pow(lasercomp.laserc_velocity_x, 2) + math.pow(lasercomp.laserc_velocity_y, 2))
                        # lasercomp.laserc_pwr_pwmgen = (self.m_spin_cut_pwr.value() * self.power_calc_curve(self.laserc_velocity_value/self.m_spin_cut_speed.value()*100)/100)/100
                        hal.set_p('hm2_7i92.0.pwmgen.02.scale', '%f' %((self.m_spin_cut_pwr.value() * self.power_calc_curve(self.laserc_velocity_value/self.m_spin_cut_speed.value()*100)/100)/100))
                    else:
                        # lasercomp.laserc_pwr_pwmgen = self.m_spin_cut_pwr.value()/100
                        hal.set_p('hm2_7i92.0.pwmgen.02.scale', '%f' %(self.m_spin_cut_pwr.value()/100))
                elif self.laserc_piercing_status:
                    # lasercomp.laserc_pwr_pwmgen = self.m_spin_pierce_pwr.value()/100
                    hal.set_p('hm2_7i92.0.pwmgen.02.scale', '%f' %(self.m_spin_pierce_pwr.value()/100))
                else:
                    # lasercomp.laserc_pwr_pwmgen = 0
                    hal.set_p('hm2_7i92.0.pwmgen.02.scale', '0')
            else:
                # lasercomp.laserc_pwr_pwmgen = 0
                hal.set_p('hm2_7i92.0.pwmgen.02.scale', '0')

    # set Pin laserc_pwr_freq
    def set_pwr_freq(self, start_stop):
        if start_stop:
            if self.laserc_cutting_status:
                if self.m_check_cut_freq.isChecked():
                    self.laserc_velocity_value = math.sqrt(math.pow(lasercomp.laserc_velocity_x, 2) + math.pow(lasercomp.laserc_velocity_y, 2))
                    lasercomp.laserc_pwr_freq = self.m_spin_cut_freq.value() * 1000 * self.freq_calc_curve(self.laserc_velocity_value/self.m_spin_cut_speed.value()*100)/100
                else:
                    lasercomp.laserc_pwr_freq = self.m_spin_cut_freq.value() * 1000
            elif self.laserc_piercing_status:
                lasercomp.laserc_pwr_freq = self.m_spin_pierce_freq.value() * 1000
            else:
                lasercomp.laserc_pwr_freq = 0
        else:
            lasercomp.laserc_pwr_freq = 0

    # set Pin laserc_focus
    def set_focus(self, start_stop):
        if start_stop:
            if self.laserc_cutting_status:
                lasercomp.laserc_focus = int(self.m_spin_cut_focus.value()/self.m_spin_cut_focus.singleStep())
            elif self.laserc_piercing_status:
                lasercomp.laserc_focus = int(self.m_spin_pierce_focus.value()/self.m_spin_cut_focus.singleStep())
            else:
                lasercomp.laserc_focus = int(self.m_spin_pierce_focus.value()/self.m_spin_cut_focus.singleStep())
        else:
            lasercomp.laserc_focus = 0
    
    # set Pin laserc_232pwr_output
    def set_232pwr_output(self, start_stop):
        if start_stop & (self.m_combo_mode.currentIndex() == 0):
            if self.laserc_cutting_status:
                if self.m_check_cut_pwr.isChecked():
                    self.laserc_velocity_value = math.sqrt(math.pow(lasercomp.laserc_velocity_x, 2) + math.pow(lasercomp.laserc_velocity_y, 2))
                    lasercomp.laserc_232pwr_output = self.m_spin_cut_pwr.value() * self.power_calc_curve(self.laserc_velocity_value/self.m_spin_cut_speed.value()*100)/100
                else:
                    lasercomp.laserc_232pwr_output = self.m_spin_cut_pwr.value()
            elif self.laserc_piercing_status:
                lasercomp.laserc_232pwr_output = self.m_spin_pierce_pwr.value()
            else:
                lasercomp.laserc_232pwr_output = 0
        else:
            lasercomp.laserc_232pwr_output = 0
    
    # set Pin laserc_cut_speed
    def set_cut_speed(self):
        lasercomp.laserc_cut_speed = self.m_spin_cut_speed.value()

    def set_laserc_parameters(self, start_stop):
        self.set_gas_puffing_status(start_stop)
        self.set_o2_regulator_pwm(start_stop)
        self.set_n2_switch_bit(start_stop)
        self.set_pwm_pwmgen(start_stop)
        self.set_laser232_power_set(start_stop)
        self.set_pwr_pwmgen(start_stop)
        self.set_pwr_freq(start_stop)
        self.set_focus(start_stop)
        self.set_headcooling_switch_bit(start_stop)
        self.set_232pwr_output(start_stop)
        self.set_laserc_ok_bit(start_stop)
        self.set_o2_regulator_pwm(start_stop)
        self.set_float_switch_bit(start_stop)
    
    ##########################################
    ##########################################

    def slot_cut_cur_rate_changed(self, arg):
        self.m_spin_cut_cur_pwr.setValue(arg * self.m_spin_powerrating.value() * 0.01)

    def slot_pierce_cur_rate_changed(self, arg):
        self.m_spin_pierce_cur_pwr.setValue(arg * self.m_spin_powerrating.value() * 0.01)

    def slot_air_head_time(self, arg):
        self.m_label_air_head_time.setText(str(arg) + '(ms)')

    def slot_pufftime_changed(self, arg):
        self.m_label_pufftime.setText(str(arg) + '(ms)')
    
    def slotPuff(self):
        if self.setting_started:
            if (self.m_slider_pufftime.value() != 0):
                self.gas_puffing_status = True
            else:
                self.gas_puffing_status = False
        else:
            self.gas_puffing_status = False

    def slot_dyn_pwr(self):
        self.m_chart.clear()
        speed1_draw = [0]
        speed2_draw = [0]
        power_draw = [self.power[0]]
        frequency_draw = [self.frequency[0]]
        j = 0
        for i in self.speed1:
            speed1_draw.append(self.speed1[j])            
            speed2_draw.append(self.speed2[j])            
            frequency_draw.append(self.frequency[j])            
            power_draw.append(self.power[j])
            j+=1
        speed1_draw.append(100)
        speed2_draw.append(100)
        power_draw.append(self.power[-1])
        frequency_draw.append(self.frequency[-1])
        if self.m_check_cut_pwr.isChecked():
            self.draw_line(speed1_draw, power_draw, "power", 'g')
            if self.m_check_cut_freq.isChecked():
                self.draw_line(speed2_draw, frequency_draw, "frequency", 'b')
        else:
            if self.m_check_cut_freq.isChecked():
                self.draw_line(speed2_draw, frequency_draw, "frequency", 'b')
            return
    def slot_dyn_freq(self):
        self.m_chart.clear()
        speed1_draw = [0]
        speed2_draw = [0]
        power_draw = [self.power[0]]
        frequency_draw = [self.frequency[0]]
        j = 0
        for i in self.speed1:
            speed1_draw.append(self.speed1[j])            
            speed2_draw.append(self.speed2[j])            
            frequency_draw.append(self.frequency[j])            
            power_draw.append(self.power[j])
            j+=1
        speed1_draw.append(100)
        speed2_draw.append(100)
        power_draw.append(self.power[-1])
        frequency_draw.append(self.frequency[-1])
        if self.m_check_cut_freq.isChecked():
            self.draw_line(speed2_draw, frequency_draw, "frequency", 'b')
            if self.m_check_cut_pwr.isChecked():
                self.draw_line(speed1_draw, power_draw, "power", 'g')
        else:
            if self.m_check_cut_pwr.isChecked():
                self.draw_line(speed1_draw, power_draw, "power", 'g')
            return
    def slot_laseron(self):
        if hal.component_exists('laser232'):
            if self.laseron_status:
                hal.set_p('laser232.laser_onoff_set','False')
            else:
                hal.set_p('laser232.laser_onoff_set','True')

    def slot_laserstartstatus(self):
            
            lasercomp.laserc_start_en_set = True
        #if self.laserc_start_status_value:
        #    lasercomp.laserc_start_set = False
        #else:
        #    lasercomp.laserc_start_set = True
    
    def slot_laserenstatus(self):
        if self.laserc_en_status_value:
            lasercomp.laserc_en_set = False
        else:
            lasercomp.laserc_en_set = True

    def slot_laserpwr_changed(self, arg):
        self.m_label_laserpwr.setText(str(arg) + '(%)')

    def slot_laserpwr_apply(self):
        if hal.component_exists('laser232'):
            self.laser232_pwr = self.m_slider_laserpwr.value()
