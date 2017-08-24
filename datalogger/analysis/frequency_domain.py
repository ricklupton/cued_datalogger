from datalogger.api.pyqtgraph_extensions import InteractivePlotWidget
from datalogger.api.toolbox import Toolbox
from datalogger.api.numpy_extensions import to_dB

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QComboBox,QCheckBox
from PyQt5.QtCore import pyqtSignal

import scipy.fftpack
import numpy as np
import pyqtgraph as pg

class FrequencyDomainWidget(InteractivePlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plot_types = ['Linear Magnitude',
                           'Log Magnitude',
                           'Phase',
                           'Real Part',
                           'Imaginary Part',
                           'Nyquist']
        self.current_plot_type = self.plot_types[0]
                
        self.current_plot = "spectrum"
        
        self.coherence_plot = False
    
    def set_selected_channels(self, selected_channels):
        """Update which channels are plotted"""
        # If no channel list is given
        if not selected_channels:
            self.channels = []
        else:
            self.channels = selected_channels
        
        self.update_plot()
    
    def set_plot_type(self, index):
        self.current_plot_type = self.plot_types[index]
        self.update_plot()
    
    def update_plot(self):
        self.clear()
        print("Plotting %s." % self.current_plot_type)
        for channel in self.channels:
            #if self.current_plot == "spectrum":
            data = channel.get_data(self.current_plot)
            if data.shape[0] == 0:
                print('No %s to plot' % self.current_plot)   
                continue
                
            # Plot
            if self.current_plot_type == 'Linear Magnitude':
                self.plot(channel.get_data("frequency"), 
                          np.abs(data),
                          pen=pg.mkPen(channel.colour))
                
            elif self.current_plot_type == 'Log Magnitude':
                self.plot(channel.get_data("frequency"),
                          to_dB(np.abs(data)),
                          pen=pg.mkPen(channel.colour))
                
            elif self.current_plot_type == 'Phase':
                self.plot(channel.get_data("frequency"), 
                          np.angle(data,deg=True),
                          pen=pg.mkPen(channel.colour))
                
            elif self.current_plot_type == 'Real Part':
                self.plot(channel.get_data("frequency"),
                          np.real(data),
                          pen=pg.mkPen(channel.colour))
                
            elif self.current_plot_type == 'Imaginary Part':
                self.plot(channel.get_data("frequency"), 
                          np.imag(data),
                          pen=pg.mkPen(channel.colour))
                
            elif self.current_plot_type == 'Nyquist':
                self.plot(np.real(data), 
                          np.imag(data),
                          pen=pg.mkPen(channel.colour))
                
            if self.current_plot == "TF" and self.coherence_plot:
                cor = channel.get_data("coherence")
                if cor.shape[0]:
                    self.plot(channel.get_data("frequency"),
                          cor,
                          pen=pg.mkPen('k'))
                pass

            
class FrequencyToolbox(Toolbox):
    """Toolbox containing the Frequency Domain controls"""
    sig_convert_to_TF = pyqtSignal()
    sig_convert_to_circle_fit = pyqtSignal()
    sig_plot_type_changed = pyqtSignal(int)
    sig_view_type_changed = pyqtSignal(str)
    sig_coherence_plot = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        
        self.init_ui()
    
    def init_ui(self):
        # # Plot options tab
        self.plot_options_tab = QWidget(self)
        plot_options_tab_layout = QVBoxLayout()
        self.view_type_combobox = QComboBox(self)
        self.view_type_combobox.addItems(['Fourier Transform','Transfer Function'])
        self.view_type_combobox.currentIndexChanged[str].connect(self.sig_view_type_changed.emit)
        plot_options_tab_layout.addWidget(self.view_type_combobox)
        self.coherence_plot_tickbox = QCheckBox('Plot Coherence',self)
        self.coherence_plot_tickbox.stateChanged.connect(self.sig_coherence_plot.emit)
        plot_options_tab_layout.addWidget(self.coherence_plot_tickbox)
        self.plot_type_combobox = QComboBox(self.plot_options_tab)
        self.plot_type_combobox.addItems(['Linear Magnitude',
                                          'Log Magnitude',
                                          'Phase',
                                          'Real Part',
                                          'Imaginary Part',
                                          'Nyquist'])
    
        self.plot_type_combobox.setCurrentIndex(0)
        self.plot_type_combobox.currentIndexChanged.connect(self.sig_plot_type_changed.emit)
        plot_options_tab_layout.addWidget(self.plot_type_combobox)
        
        self.plot_options_tab.setLayout(plot_options_tab_layout)
        
        self.addTab(self.plot_options_tab, "Plot Options")
        # # Conversion tab
        self.convert_tab = QWidget(self)
        convert_tab_layout = QVBoxLayout()
        
        self.view_tf_btn = QPushButton("Convert FFT to TF")
        self.convert_tab.setLayout(convert_tab_layout)
        self.view_tf_btn.clicked.connect(self.sig_convert_to_TF.emit)
        convert_tab_layout.addWidget(self.view_tf_btn)        
        
        self.circle_fit_btn = QPushButton("Convert to Circle Fit")
        self.circle_fit_btn.clicked.connect(self.sig_convert_to_circle_fit.emit)
        convert_tab_layout.addWidget(self.circle_fit_btn)

        self.addTab(self.convert_tab, "Conversion")
        
    def set_view_type(self,vtype):
        self.view_type_combobox.setCurrentText(vtype)
        
def compute_autospec(fft_data):
    return(fft_data * np.conjugate(fft_data))

def compute_crossspec(in_fft_data,out_fft_data):
    return(np.conjugate(in_fft_data) * out_fft_data)

def compute_transfer_function(autospec_in,autospec_out,crossspec):
   
    transfer_func = (autospec_out/crossspec)
    coherence = ((crossspec * np.conjugate(crossspec))/(autospec_in*autospec_out))
    print(coherence)
    return(transfer_func,np.real(coherence))
