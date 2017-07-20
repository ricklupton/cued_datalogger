# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 11:44:12 2017

@author: eyt21
"""
import sys,traceback
from PyQt5.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QMainWindow,
    QPushButton, QApplication, QMessageBox, QDesktopWidget,QTabWidget,QTabBar)
#from PyQt5.QtGui import QIcon,QFont
from PyQt5.QtCore import QCoreApplication,QTimer

import numpy as np
from numpy.fft import rfft, rfftfreq

import pyqtgraph as pg
import pyqtgraph.exporters

import liveplotUI as lpUI
from wintabwidgets import data_tab_widget
from sonogram.matplotlib.sonogram import SonogramWidget
from cwt.cwt import CWTWidget

from channel import DataSet, Channel, ChannelSet

# For the exporter to work, need to change iteritem to item in pyqtgraph
class DataWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window parameter
        self.setGeometry(200,500,1000,500)
        self.setWindowTitle('DataWindow')

        # Construct UI        
        self.initUI()
        
        # Initialise the channels
        self.init_channels()
        
        # Center and show window
        self.center()
        self.setFocus()
        self.show()
     #------------- App construction methods--------------------------------     
    def initUI(self):
        # Set up the main widget to contain all Widgets
        self.main_widget = QWidget()
        # Set up the main layout
        vbox = QVBoxLayout(self.main_widget)
        
        # Set up the button to open the LivePlotting Window
        self.liveplot = None
        self.liveplotbtn = QPushButton('Open Oscilloscope',self.main_widget)
        self.liveplotbtn.resize(self.liveplotbtn.sizeHint())
        self.liveplotbtn.pressed.connect(self.toggle_liveplot)
        vbox.addWidget(self.liveplotbtn)
        
        # Set up the button to plot the FFT
        self.fft_btn = QPushButton("Calculate FFT", self.main_widget)
        self.fft_btn.pressed.connect(self.plot_fft)
        vbox.addWidget(self.fft_btn)
        
        # Set up the button to plot the sonogram
        self.sonogram_btn = QPushButton("Calculate sonogram", self.main_widget)
        self.sonogram_btn.pressed.connect(self.plot_sonogram)  
        vbox.addWidget(self.sonogram_btn)
        
        # Set up the button to plot the CWT
        self.cwt_btn = QPushButton("Calculate CWT", self.main_widget)
        self.cwt_btn.pressed.connect(self.plot_cwt)  
        vbox.addWidget(self.cwt_btn)
        
        #Set up the tabs container for recorded data
        self.data_tabs = QTabWidget(self)
        self.data_tabs.setMovable(True)
        self.data_tabs.setTabsClosable (False)
        #self.data_tabs.setTabPosition(0)
        vbox.addWidget(self.data_tabs)
        
        # Add tab containing a plot widget
        self.data_tabs.addTab(data_tab_widget(self), "Time Series")
        self.data_tabs.addTab(data_tab_widget(self), "Frequency domain")

        
        #Set the main widget as central widget
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
    
    # Center the window
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def init_channels(self):
        """Initialise the channels"""
        # Create the channel set
        self.cs = ChannelSet()
        # Set up the datasets in the channels
        t = DataSet(id_='t')
        y = DataSet(id_='y')
        f = DataSet(id_='f')
        s = DataSet(id_='s')
        # Add one input channel
        self.cs.add_channel(Channel(0, name="Input 0", datasets=[t,y,f,s]))
            
    #------------- UI callback methods--------------------------------       
    def toggle_liveplot(self):
        if not self.liveplot:
            #try:
            self.liveplot = lpUI.LiveplotApp(self)
            self.liveplot.show()
            self.liveplotbtn.setText('Close Oscilloscope')
		
		# Plot when data received
            self.liveplot.dataSaved.connect(self.plot_time_series)
            
        else:
            self.liveplot.close()
            self.liveplot = None
            self.liveplotbtn.setText('Open Oscilloscope')
    
    def plot_time_series(self):
        # Switch to time series tab
        self.data_tabs.setCurrentIndex(0)
        t = self.cs.chans[0].data('t')
        y = self.cs.chans[0].data('y')
        # Plot data
        self.data_tabs.currentWidget().canvasplot.plot(x=t, y=y, clear=True, pen='b')
        '''
        try:    
            exporter = pg.exporters.MatplotlibExporter(self.data_tabs.currentWidget().canvasplot)
            exporter.export('testingmpl')
        except Exception as e:
            print(e)
            t,v,tb = sys.exc_info()
            print(t)
            print(v)
            print(traceback.format_tb(tb))'''
                
        
    def plot_sonogram(self):
        signal = self.cs.chans[0].data('y')
        t = self.cs.chans[0].data('t')
        self.data_tabs.addTab(SonogramWidget(signal, t, parent=self), "Sonogram")
        # Switch to sonogram tab
        self.data_tabs.setCurrentIndex(2)
    
    def plot_cwt(self):
        signal = self.cs.chans[0].data('y')
        t = self.cs.chans[0].data('t')
        self.data_tabs.addTab(CWTWidget(signal, t, parent=self), "CWT")
        # Switch to sonogram tab
        self.data_tabs.setCurrentIndex(3)
        
    def plot_fft(self):
        # Switch to frequency domain tab
        self.data_tabs.setCurrentIndex(1)
        
        y = self.cs.chans[0].data('y')

        # Calculate FT and associated frequencies
        ft = np.abs(np.real(rfft(y)))
        freqs = np.real(rfftfreq(y.size, 1/4096))
        
        # Store in datasets
        self.cs.chans[0].set_data('f', freqs)
        self.cs.chans[0].set_data('s', ft)

        # Plot data
        self.data_tabs.currentWidget().canvasplot.plot(x=freqs, y=ft, clear=True, pen='g')
        
    #----------------Overrding methods------------------------------------
    # The method to call when the mainWindow is being close       
    def closeEvent(self,event):
        self.activateWindow()
        reply = QMessageBox.question(self,'Message',
        'Are you sure you want to quit?', QMessageBox.Yes|
        QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.liveplot:
                self.liveplot.close()
            event.accept()
        else:
            event.ignore()
        
if __name__ == '__main__':
    app = 0 
    app = QApplication(sys.argv)
    w = DataWindow()
    sys.exit(app.exec_())
