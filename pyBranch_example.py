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
import branchClasses as bc
import tableModels as tm
import pandas as pd
import tables as tb

matplotlib.use('QT5Agg')


class LinePlot(FigureCanvasQTAgg):
    """Class for the matplotlib plots of individual lines"""
    
    right_clicked = QtCore.pyqtSignal()  # this is our custom signal that we will emit for the event manager to collect
    left_clicked = QtCore.pyqtSignal()
    
    def __init__(self, plot_data, *args, **kwargs):
        fig = self._create_fig(plot_data) 
        super().__init__(figure=fig, *args, **kwargs)    
        self.selected = False   
        fig.set_facecolor('#EFEFEF')
   
    def _create_voigt(self, x, y):
        centre = x.median()
        amp = y.max()  # ! might want to change to get value at index of the median                       
        mod = VoigtModel()        
        return mod.fit(y, x=x, amplitude=amp, center=centre)
    
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
        
    
    def _create_fig(self, plot_data):  
        x = plot_data['wavenumber']
        y = plot_data['snr']

        result = self._create_voigt(x, y)
                
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]}, figsize=(2.5, 3.5))
        self.ax1.plot(x, y)
        #ax1.set(ylabel="Relative intensity")
        self.ax1.ticklabel_format(useOffset=False)

        self.ax2.plot(x, y - result.best_fit)
        self.ax2.axhline(y=0.0, color='grey', linestyle='dashed', alpha=0.5)
        #ax2.set(xlabel="Wavenumber (cm-1)", ylabel="Relative intensity")
        return self.fig
        

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('mainwindow2.ui', self) 
        self.main_splitter.setSizes([300, 1000])  # ! put these as percentage of window size
        self.right_splitter.setSizes([1000, 350]) # ! put these as percentage of window size
        
        self.fileh = tb.open_file('test.h5', 'r')             

        self.plot_data = self.get_plot_data()
        self.draw_line_plots()
        self.display_levels_table()
        self.display_files_tree()
    
    def draw_line_plots(self):
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
                # fig = LinePlot(xx, yy)
                fig = LinePlot(self.plot_data)
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
        
    def display_levels_table(self):
        """Displays the data in the levels dataframe to the levels table view in the main window"""
        data = pd.DataFrame(self.fileh.root.levels.levels.read())

        self.model = tm.levelTableModel(data)
        self.levelsTableView.setModel(self.model)
        
        # Set all of the correct flags and views
        self.levelsTableView.setSortingEnabled(True)
        self.levelsTableView.setAlternatingRowColors(True)
        self.levelsTableView.setSelectionBehavior(QtWidgets.QTableView.SelectRows)  # so a full row is selected when any cell is clicked
        self.levelsTableView.horizontalHeader().setStretchLastSection(True)
        stylesheet = "::section{background-color:rgb(166, 217, 245); border-radius:14px; font:bold}"  # here is where you set the table header style
        self.levelsTableView.horizontalHeader().setStyleSheet(stylesheet)
        self.levelsTableView.resizeColumnsToContents()
        
    def display_files_tree(self):
        """To Do: 
            add in all other fields. 
            Make a tick box for if the file has been intensity corrected.
            right click for context menu
            selection box for making a spectrum the refernce spectrum
        """

        self.filesTreeWidget.setColumnCount(2)
        self.filesTreeWidget.setHeaderLabels(["Spectrum", "File", 'Wavenumber Max', 'Wavenumber Min'])
                
        items = []
        for key, values in self.fileh.root.spectra._v_children.items():
            item = QtWidgets.QTreeWidgetItem([key])
            
            for value in values._v_children.values():
                child = QtWidgets.QTreeWidgetItem(['',value.title])           
                item.addChild(child)
                
            items.append(item)
            
        self.filesTreeWidget.insertTopLevelItems(0, items)
        
        for col in range(self.filesTreeWidget.columnCount()):  # ! link this to a signal so it auto resizes
            self.filesTreeWidget.resizeColumnToContents(col)
        
    
    def left_clicked(self):
        fig = self.sender()
        print("Plot selected:" + str(not fig.get_selected()))
        
    def right_clicked(self):
        print(self.main_splitter.sizes())
        print('right click')  
        
    def get_spectrum_data(self, spectrum, wn_low, wn_high):
        """Return the section of the specified spectrum between the upper and lower wavenumbers"""
        query_string = f'(wavenumber >= {wn_low}) & (wavenumber <= {wn_high})'  # remember the brackets around each query
        data = pd.DataFrame(spectrum.read_where(query_string))
        return data
        
    def get_plot_data(self):
        wn_low = 19827.8
        wn_high = 19828.3
        
        spec = self.fileh.root.spectra.test.spectrum        
        data = self.get_spectrum_data(spec, wn_low, wn_high)
        return data        
       
       
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())