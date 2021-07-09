import sys
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QMessageBox, QBoxLayout, QTabWidget
from dialog import Ui_Dialog
from PyQt5 import QtWidgets, Qt
from functools import partial
from pyqtgraph import PlotWidget
from pyqtgraph.Point import *
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, QVariant, pyqtSlot
import unicodedata
from myROI import *

class MyDialog(QDialog, Ui_Dialog):
    return_ok = pyqtSignal(list, list, list, list)
    def __init__(self, list1, list2, parent=None):
        super(MyDialog, self).__init__(parent)
        self.setupUi(self)    

        self.speed1_data = list1[0]
        self.power_data = list1[1]
        self.speed2_data = list1[2]
        self.freq_data = list1[3]

        self.speed = list2[0]
        self.pwr= list2[1]
        self.freq = list2[2]

        self.p_column = len(self.power_data)
        self.f_column = len(self.freq_data)

        p_header_label = ('Speed(%)','Power(%)')
        self.p_table.setHorizontalHeaderLabels(p_header_label)
        f_header_label = ('Speed(%)','Frequency(%)')
        self.f_table.setHorizontalHeaderLabels(f_header_label)

        self.copy_flag = False
        
        # initialize power/speed table.
        self.p_table.verticalHeader().hide()
        self.p_table.setRowCount(2)
        

        self.tabWidget.setCurrentIndex(0)

        # initialize freq/speed table
        self.f_table.verticalHeader().hide()
        self.f_table.setRowCount(2)

        self.speed_item0p = QTableWidgetItem()
        self.speed_item1p = QTableWidgetItem()
        self.speed_item0q = QTableWidgetItem()
        self.speed_item1q = QTableWidgetItem()
        self.power_item0 = QTableWidgetItem()
        self.power_item1 = QTableWidgetItem()
        self.freq_item0 = QTableWidgetItem()
        self.freq_item1 = QTableWidgetItem()
        self.speed_item0p.setTextAlignment(0x0002)
        self.speed_item1p.setTextAlignment(0x0002)
        self.speed_item0q.setTextAlignment(0x0002)
        self.speed_item1q.setTextAlignment(0x0002)
        self.power_item0.setTextAlignment(0x0002)
        self.power_item1.setTextAlignment(0x0002)
        self.freq_item0.setTextAlignment(0x0002)
        self.freq_item1.setTextAlignment(0x0002)
        self.p_table.setItem(0,0,self.speed_item0p)
        self.p_table.setItem(1,0,self.speed_item1p)
        self.p_table.setItem(0,1,self.power_item0)
        self.p_table.setItem(1,1,self.power_item1)
        self.f_table.setItem(0,0,self.speed_item0q)
        self.f_table.setItem(1,0,self.speed_item1q)
        self.f_table.setItem(0,1,self.freq_item0)
        self.f_table.setItem(1,1,self.freq_item1)
        self.draw_p_table()
        self.draw_f_table()

        # signal/slot
        self.p_chbox.clicked.connect(partial(self.slot_pcheck))
        self.f_chbox.clicked.connect(partial(self.slot_fcheck))
        self.tabWidget.currentChanged.connect(partial(self.slot_currentIndex))

        self.p_table.cellActivated.connect(partial(self.slot_pcell))

        self.d_copy.clicked.connect(partial(self.slot_dcopy))
        self.d_ok.clicked.connect(partial(self.slot_dok))
        self.d_cancel.clicked.connect(partial(self.slot_dcancel))
        #self.p_table.cellChanged.connect(partial(self.redraw_power_graph))
        #self.f_table.cellChanged.connect(partial(self.redraw_freq_graph))
        
        self.draw_power_graph()
        self.draw_freq_graph()

    # draw power/speed table
    def draw_power_graph(self):
        self.p_plot = pg.PlotWidget(enableMenu=False, title="Power", movable=False)
        self.p_plot.setMouseEnabled(False, False)
        self.p_chart_layout = QBoxLayout(QBoxLayout.RightToLeft, self)
        self.p_chart_layout.addWidget(self.p_plot)
        self.p_chart_widget.setLayout(self.p_chart_layout)
        self.p_plot.setBackground('w')
        self.p_plot.showGrid(x=True, y=True)
        self.p_plot.setXRange(0, 100, padding=0)
        self.p_plot.setYRange(0, 100, padding=0)
        self.proi = PolyLineROI(zip(self.speed1_data, self.power_data))          

        self.proi.setPen(0,0,255)
        self.proi.cursor_move_signal.connect(partial(self.slot_p_cursor_move_signal))
        self.p_plot.addItem(self.proi)

    def draw_freq_graph(self):
        self.f_plot = pg.PlotWidget(enableMenu=False, title="Frequency", movable=False)
        self.f_plot.setMouseEnabled(False, False)
        self.f_chart_layout = QBoxLayout(QBoxLayout.RightToLeft, self)
        self.f_chart_layout.addWidget(self.f_plot)
        self.f_chart_widget.setLayout(self.f_chart_layout)
        self.f_plot.setBackground('w')
        self.f_plot.showGrid(x=True, y=True)
        self.f_plot.setXRange(0, 100, padding=0)
        self.f_plot.setYRange(0, 100, padding=0)
        
        self.froi = PolyLineROI(zip(self.speed2_data, self.freq_data))
        #self.froi.clearPoints()
        self.froi.setPen(255,0,0)
        self.froi.cursor_move_signal.connect(partial(self.slot_f_cursor_move_signal))
        self.f_plot.addItem(self.froi)

    def draw_p_table(self):
        #self.p_table.clearContents()
        self.speed_item0p.setText(str(self.speed1_data[0]))
        self.speed_item1p.setText(str(self.speed1_data[1]))
        self.power_item0.setText(str(self.power_data[0]))
        self.power_item1.setText(str(self.power_data[1]))

        # self.speed_item0p = QTableWidgetItem(str(self.speed1_data[0]))
        # self.speed_item0p.setTextAlignment(0x0002)
        # self.power_item0 = QTableWidgetItem(str(self.power_data[0]))
        # self.power_item0.setTextAlignment(0x0002)
        # self.p_table.setItem(0,0,self.speed_item0p)
        # self.p_table.setItem(0,1,self.power_item0)
        # self.speed_item1p = QTableWidgetItem(str(self.speed1_data[1]))
        # self.speed_item1p.setTextAlignment(0x0002)
        # self.power_item1 = QTableWidgetItem(str(self.power_data[1]))
        # self.power_item1.setTextAlignment(0x0002)
        # self.p_table.setItem(1,0,self.speed_item1p)
        # self.p_table.setItem(1,1,self.power_item1)
    # draw freq/speed table
    def draw_f_table(self):
        self.speed_item0q.setText(str(self.speed2_data[0]))
        self.speed_item1q.setText(str(self.speed2_data[1]))
        self.freq_item0.setText(str(self.freq_data[0]))
        self.freq_item1.setText(str(self.freq_data[1]))
        # self.f_table.clearContents()
        # self.speed_item0q = QTableWidgetItem(str(self.speed2_data[0]))
        # self.speed_item0q.setTextAlignment(0x0002)
        # self.freq_item0 = QTableWidgetItem(str(self.freq_data[0]))
        # self.freq_item0.setTextAlignment(0x0002)
        # self.f_table.setItem(0, 0, self.speed_item0q)
        # self.f_table.setItem(0, 1, self.freq_item0)
        # self.speed_item1q = QTableWidgetItem(str(self.speed2_data[1]))
        # self.speed_item1q.setTextAlignment(0x0002)
        # self.freq_item1 = QTableWidgetItem(str(self.freq_data[1]))
        # self.freq_item1.setTextAlignment(0x0002)
        # self.f_table.setItem(1, 0, self.speed_item1q)
        # self.f_table.setItem(1, 1, self.freq_item1)

    def slot_pcheck(self):
        if self.p_chbox.isChecked() == False:
            header_label = ('Speed(%)','Power(%)')
            self.p_table.setHorizontalHeaderLabels(header_label)
            self.draw_p_table()
        else:
            header_label = ('Speed(mm/s)','Power(W)')
            self.p_table.setHorizontalHeaderLabels(header_label)
            self.change_draw_p_table()

    def slot_fcheck(self):
        if self.f_chbox.isChecked() == False:
            header_label = ('Speed(%)','Frequency(%)')
            self.f_table.setHorizontalHeaderLabels(header_label)
            self.draw_f_table()
        else:
            header_label = ('Speed(mm/s)','Frequency(KHz)')
            self.f_table.setHorizontalHeaderLabels(header_label)
            self.change_draw_f_table()

    def change_draw_p_table(self):
        #self.p_table.clearContents()
        #self.speed_item0p = QTableWidgetItem(str(format(float(self.speed)*float(self.speed1_data[1])/100, '.2f')))
        #self.speed_item0p.setTextAlignment(0x0002)
        #self.power_item0 = QTableWidgetItem(str(format(float(self.pwr)*float(self.power_data[1])/100, '.2f')))
        #self.power_item0.setTextAlignment(0x0002)
        #self.p_table.setItem(0, 0, self.speed_item0p)
        #self.p_table.setItem(0, 1, self.power_item0)
        self.speed_item0p.setText(str(format(float(self.speed)*float(self.speed1_data[0])/100, '.2f')))
        self.speed_item1p.setText(str(format(float(self.speed)*float(self.speed1_data[1])/100, '.2f')))
        self.power_item0.setText(str(format(float(self.pwr)*float(self.power_data[0])/100, '.2f')))
        self.power_item1.setText(str(format(float(self.pwr)*float(self.power_data[1])/100, '.2f')))
        # self.speed_item1p = QTableWidgetItem(str(format(float(self.speed)*float(self.speed1_data[1])/100, '.2f')))
        # self.speed_item1p.setTextAlignment(0x0002)
        # self.power_item1 = QTableWidgetItem(str(format(float(self.pwr)*float(self.power_data[1])/100, '.2f')))
        # self.power_item1.setTextAlignment(0x0002)
        # self.p_table.setItem(1, 0, self.speed_item1p)
        # self.p_table.setItem(1, 1, self.power_item1)

    def change_draw_f_table(self):
        #self.f_table.clearContents()
        self.speed_item0q.setText(str(format(float(self.speed)*float(self.speed2_data[0])/100, '.2f')))
        self.speed_item1q.setText(str(format(float(self.speed)*float(self.speed2_data[1])/100, '.2f')))
        self.freq_item0.setText(str(format(float(self.freq)*float(self.freq_data[0])/100, '.2f')))
        self.freq_item1.setText(str(format(float(self.freq)*float(self.freq_data[1])/100, '.2f')))
        # self.speed_item0q = QTableWidgetItem(str(format(float(self.speed)*float(self.speed2_data[0])/100, '.2f')))
        # self.speed_item0q.setText(str(format(float(self.speed)*float(self.speed2_data[0])/100, '.2f')))
        # self.speed_item0q.setTextAlignment(0x0002)
        # self.freq_item0 = QTableWidgetItem(str(format(float(self.freq)*float(self.freq_data[0])/100, '.2f')))
        # self.freq_item0.setTextAlignment(0x0002)
        # self.f_table.setItem(0, 0, self.speed_item0q)
        # self.f_table.setItem(0, 1, self.freq_item0)
        # self.speed_item1q = QTableWidgetItem(str(format(float(self.speed)*float(self.speed2_data[1])/100, '.2f')))
        # self.speed_item1q.setTextAlignment(0x0002)
        # self.freq_item1 = QTableWidgetItem(str(format(float(self.freq)*float(self.freq_data[1])/100, '.2f')))
        # self.freq_item1.setTextAlignment(0x0002)
        # self.f_table.setItem(1, 0, self.speed_item1q)
        # self.f_table.setItem(1, 1, self.freq_item1)

    def slot_currentIndex(self, index):
        if index == 0:
            self.d_copy.setText("Copy to frequency")
        else:
            self.d_copy.setText("Copy to power")

    def slot_dcopy(self):
        if self.tabWidget.currentIndex() == 1:
            self.speed1_data = self.speed2_data
            self.power_data = self.freq_data
            self.slot_pcheck()
            self.redraw_power_graph()
        else:
            self.speed2_data = self.speed1_data
            self.freq_data = self.power_data
            self.slot_fcheck()
            self.redraw_freq_graph()

    def redraw_power_graph(self):
        #newPos1 = Point(float(self.speed_item0p.text()), float(self.power_item0.text()))
        newPos1 = Point(float(self.speed1_data[0]), float(self.power_data[0]))
        self.proi.mymovePoint(0, newPos1)
        #newPos2 = Point(float(self.speed_item1p.text()), float(self.power_item1.text()))
        newPos2 = Point(float(self.speed1_data[1]), float(self.power_data[1]))
        self.proi.mymovePoint(1, newPos2)
    def redraw_freq_graph(self):
        #newPos1 = Point(float(self.speed_item0q.data(0).replace(u'\N{MINUS SIGN}', '-')), float(self.freq_item0.data(0).replace(u'\N{MINUS SIGN}', '-')))
        newPos1 = Point(float(self.speed2_data[0]), float(self.freq_data[0]))
        self.froi.mymovePoint(0, newPos1)
        #newPos2 = Point(float(self.speed_item1q.data(0).replace(u'\N{MINUS SIGN}', '-')), float(self.freq_item1.data(0).replace(u'\N{MINUS SIGN}', '-')))
        newPos2 = Point(float(self.speed2_data[1]), float(self.freq_data[1]))
        self.froi.mymovePoint(1, newPos2)

    @pyqtSlot(list, list, list, list)            
    def slot_dok(self):     
        self.return_ok.emit(self.speed1_data, self.power_data, self.speed2_data, self.freq_data)
        self.close()
    def slot_dcancel(self):
        self.close()
    def slot_pcell(self,row, col):              
        self.p_cellData = self.p_table.item(row,col).text()       

    @pyqtSlot(int, float, float)
    def  slot_p_cursor_move_signal(self,index,x,y):
        if index == 0:
            ######  cut   #####
            self.speed1_data.pop(0)          
            self.speed1_data.insert(0,float(format(x,'.2f')))
            self.power_data.pop(0)
            self.power_data.insert(0,float(format(y,'.2f')))                   
        else:
            #######   cut   ########
            self.speed1_data.pop(1)          
            self.speed1_data.insert(1,float(format(x,'.2f')))
            self.power_data.pop(1)
            self.power_data.insert(1,float(format(y,'.2f')))
      
        self.slot_pcheck()

    @pyqtSlot(int, float, float)
    def  slot_f_cursor_move_signal(self,index,x,y): 
        if index == 0:
            ######  frequency   #####           
            self.speed2_data.pop(0)          
            self.speed2_data.insert(0,float(format(x,'.2f')))
            self.freq_data.pop(0)
            self.freq_data.insert(0,float(format(y,'.2f')))                    
        else:
            ######  frequency   #####
            self.speed2_data.pop(1)          
            self.speed2_data.insert(1,float(format(x,'.2f')))
            self.freq_data.pop(1)
            self.freq_data.insert(1,float(format(y,'.2f'))) 
      
        self.slot_fcheck()         
        