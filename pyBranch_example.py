import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from bisect import bisect_left, bisect_right
from lmfit.models import VoigtModel
import sys
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import Qt

matplotlib.use('QT5Agg')

wn_low = 19827.8
wn_high = 19828.3

with open('test.dat', 'rb') as dat_file:
    dat = np.fromfile(dat_file, np.float32)
   

with open('test.hdr', 'r') as hdr_file:
    hdr = hdr_file.readlines()
    
    wstart = float(hdr[12][10:30])
    wstop = float(hdr[13][10:30])
    delw = float(hdr[16][10:30])
 
wnum=list(np.arange(wstart, wstop, delw))   

left_pos = bisect_left(wnum, wn_low)
right_pos = bisect_right(wnum, wn_high)

yy = dat[left_pos: right_pos]
xx = wnum[left_pos: right_pos]


class LinePlot(FigureCanvasQTAgg):
    """Class for the matplotlib plots of individual lines"""
    
    right_clicked = QtCore.pyqtSignal()  # this is our custom signal that we will emit for the event manager to collect
    left_clicked = QtCore.pyqtSignal()
    
    def __init__(self, x, y, *args, **kwargs):
        fig = self._create_fig(x, y) 
        super().__init__(figure=fig, *args, **kwargs)    
        self.selected = False   
        fig.set_facecolor('#EFEFEF')
        # maybe could store all data here - make this object the line itself?
        
    def _create_voigt(self, x, y):
        mod = VoigtModel()
        return mod.fit(y, x=x, amplitude=700000000., center=19828.)
    
    def get_wn(self):
        return "ok here's the wn" 
    
    def get_selected(self):
        return self.selected

    def toggle_background(self):
        if not self.selected:
            self.ax1.set_facecolor('#b6d4f2')
            self.ax2.set_facecolor('#b6d4f2') 
            self.selected = True
        else:
            self.ax1.set_facecolor('white')
            self.ax2.set_facecolor('white') 
            self.selected = False    
        
        self.draw()  # needs to be self not fig as the self is the canvas itself
    
    def mousePressEvent(self, event):  # this is a default function of FigureCanvasQTAgg that we are extending
        button = event.button() 
        
        if button == 1:  # left mouse button clicked
            self.left_clicked.emit()
            self.toggle_background()
                
        elif button == 2:  # right mouse button clicked
            self.right_clicked.emit()
            
        return super().mousePressEvent(event)  # not needed but good practice to send the event up the chain
        
        
    def _create_fig(self, x, y):        
        result = self._create_voigt(x,y)
                
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]}, figsize=(2.5, 3.5))
        self.ax1.plot(wnum[left_pos: right_pos], dat[left_pos: right_pos])
        #ax1.set(ylabel="Relative intensity")
        self.ax1.ticklabel_format(useOffset=False)

        self.ax2.plot(wnum[left_pos: right_pos], dat[left_pos: right_pos] - result.best_fit)
        self.ax2.axhline(y=0.0, color='grey', linestyle='dashed', alpha=0.5)
        #ax2.set(xlabel="Wavenumber (cm-1)", ylabel="Relative intensity")
        return self.fig
        

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('mainwindow2.ui', self) 
        self.main_splitter.setSizes([300, 1000])
        self.right_splitter.setSizes([1000, 350])
        
        outer_layout = QtWidgets.QVBoxLayout()
        
        plot_positions = [[True, True, True, False, False], 
                          [True, True, False, True, False], 
                          [True, False, True, True, True],
                          [False, False, True, False, True]]  # dummy list to create grid of plots
                
        for i, row in enumerate(plot_positions):
            inner_layout = QtWidgets.QHBoxLayout()
            group_box = QtWidgets.QGroupBox(f'Spectrum {i}.asc')
            group_box.setStyleSheet('background-color: #EFEFEF')
                        
            for plot in row:               
                fig = LinePlot(xx, yy)
                fig.setFixedSize(250,350)
                fig.right_clicked.connect(self.right_clicked)  # now linked to the event handler of the object itself (the QtCore.pyqtSignal() 'right_clicked'). This then calls the function self.right_clicked 
                fig.left_clicked.connect(self.left_clicked)
                
                if plot:  # create the line plot
                    inner_layout.addWidget(fig)
                else:  # add a dummy blank space
                    placeholder = QtWidgets.QWidget()
                    placeholder.setFixedHeight(350)
                    placeholder.setFixedWidth(250)
                    inner_layout.addWidget(placeholder)

            inner_layout.setAlignment(Qt.AlignLeft)            
            group_box.setLayout(inner_layout)    
            outer_layout.addWidget(group_box)
        
        self.inner.setLayout(outer_layout)
        self.inner.setStyleSheet('background-color: #EFEFEF')
    
    def left_clicked(self):
        fig = self.sender()
        print("Plot selected:" + str(not fig.get_selected()))
        
    def right_clicked(self):
        print(self.main_splitter.sizes())
        print('right click')  
       
       
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())