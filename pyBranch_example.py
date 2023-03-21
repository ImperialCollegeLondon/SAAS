import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from bisect import bisect_left, bisect_right
from lmfit.models import VoigtModel
import sys
from PyQt5 import QtCore, QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt
import branchClasses as bc
import tableModels as tm
import pandas as pd
import tables as tb
import ctypes

### Global settings ###
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID()  # lets windows know we are setting our own icon for the taskbar
matplotlib.use('QT5Agg')
#######################


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
        
        # Upper plot        
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, sharex=True, gridspec_kw={'height_ratios': [3, 1]}, figsize=(2.5, 3.5))
        self.ax1.plot(x, y)
        #ax1.set(ylabel="Relative intensity")
        self.ax1.ticklabel_format(useOffset=False)

        # Residual plot
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
        self.linesTabWidget.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.linesTableView.setSortingEnabled(True)
        self.linesTableView.setAlternatingRowColors(True)
        self.linesTableView.setSelectionBehavior(QtWidgets.QTableView.SelectRows)  # so a full row is selected when any cell is clicked
        # self.linesTableView.horizontalHeader().setStretchLastSection(True)
        stylesheet = "::section{background-color:rgb(166, 217, 245); border-radius:14px; font:bold}"  # here is where you set the table header style
        self.linesTableView.horizontalHeader().setStyleSheet(stylesheet)
        
        self.match_tolerance = 0.05  # matching tolerance between Ritz wavenumber and observed wavenumber in linelist
        
        self.fileh = tb.open_file('test.h5', 'r')  # open main hdf5 file        

        #self.plot_data = self.get_plot_data()
        self.matched_lines = pd.DataFrame(self.fileh.root.matched_lines.lines.read())
      
        #self.draw_line_plots()
        self.display_levels_table()
        self.display_files_tree()
        self.display_all_lines_table()
        self.linelists = self.get_linelists()
        self.merge_linelists()
        
    def onLevelSelected(self, selected, deselected):
        level = selected.indexes()[0].data()
        query_string = f"upper_desig == b'{level}'"  # b needed as the srings are stored as bytes in the datafram and hdf5
        self.level_lines = self.matched_lines.query(query_string)
        self.level_lines = self.level_lines.dropna(axis='columns', how='all')  # remove all columns with NaN i.e. spectra with no matching lines        
        
        if self.level_lines.size > 0:  # adds the log_gf column back in if it was removed in the dropna step TODO - see if there is a better way of doing this
            try:
                self.level_lines.insert(loc=1, column='log_gf', value=np.nan)
            except ValueError:
                pass       
        
        self.display_lines_table() 
        self.draw_line_plots()
        
    def draw_line_plots(self):
        
        if self.inner.layout() is not None:  # won't happen on initialisation
            QtWidgets.QWidget().setLayout(self.inner.layout())  # removes the layout attached to self.inner by changing the layouts parent to a temporary widget TODO check this doesn't slow the system down by having loads of layouts in the memory - there is a cleaner in PyQt that might be useful here
    
        plot_layout = QtWidgets.QVBoxLayout()
        
        # TODO may need to convert the df to a list/array to be able to get single rows? or do this on pandas only?
        
        for line in self.level_lines:
            line_layout = QtWidgets.QHBoxLayout()
            group_box = QtWidgets.QGroupBox(f'{self.level_lines[line]}')
            print('self.level_lines[line]: ', line)
            group_box.setStyleSheet('background-color: #EFEFEF')
            
            placeholder = QtWidgets.QWidget()
            placeholder.setFixedHeight(350)
            placeholder.setFixedWidth(250)
            line_layout.addWidget(placeholder)
    
            line_layout.setAlignment(Qt.AlignLeft)            
            group_box.setLayout(line_layout)    
            plot_layout.addWidget(group_box)
            
        self.inner.setLayout(plot_layout)
        self.inner.setStyleSheet('background-color: #EFEFEF')  
        
        # plot_positions = [[True, True, True, False, False], 
        #                   [True, True, False, True, False], 
        #                   [True, False, True, True, True],
        #                   [False, False, True, False, True]]  # dummy list to create grid of plots
                
        # for i, row in enumerate(plot_positions):
        #     inner_layout = QtWidgets.QHBoxLayout()
        #     group_box = QtWidgets.QGroupBox(f'Spectrum {i}.asc')
        #     group_box.setStyleSheet('background-color: #EFEFEF')
                        
        #     for plot in row:               
        #         # fig = LinePlot(xx, yy)
        #         fig = LinePlot(self.plot_data)
        #         fig.setFixedSize(250,350)
        #         fig.right_clicked.connect(self.right_clicked)  # now linked to the event handler of the object itself (the QtCore.pyqtSignal() 'right_clicked'). This then calls the function self.right_clicked 
        #         fig.left_clicked.connect(self.left_clicked)
                
        #         if plot:  # create the line plot
        #             inner_layout.addWidget(fig)
        #         else:  # add a dummy blank space
        #             placeholder = QtWidgets.QWidget()
        #             placeholder.setFixedHeight(350)
        #             placeholder.setFixedWidth(250)
        #             inner_layout.addWidget(placeholder)

        #     inner_layout.setAlignment(Qt.AlignLeft)            
        #     group_box.setLayout(inner_layout)    
        #     outer_layout.addWidget(group_box)
        
  
        
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
    
    def display_levels_table(self):
        """Displays the data in the levels dataframe to the levels table view in the main window"""
        data = pd.DataFrame(self.fileh.root.levels.levels.read())

        self.model = tm.levelTableModel(data)
        self.levelsTableView.setModel(self.model)
        self.levelsTableView.selectionModel().selectionChanged.connect(self.onLevelSelected)  # needs to be after the model for the table is set
        
        # Set all of the correct flags and views
        self.levelsTableView.setSortingEnabled(True)
        self.levelsTableView.setAlternatingRowColors(True)
        self.levelsTableView.setSelectionBehavior(QtWidgets.QTableView.SelectRows)  # so a full row is selected when any cell is clicked
        self.levelsTableView.setSelectionMode(QtWidgets.QTableView.SingleSelection)  # so only one row is selected at a time
        self.levelsTableView.horizontalHeader().setStretchLastSection(True)
        stylesheet = "::section{background-color:rgb(166, 217, 245); border-radius:14px; font:bold}"  # here is where you set the table header style
        self.levelsTableView.horizontalHeader().setStyleSheet(stylesheet)
        self.levelsTableView.resizeColumnsToContents()
        self.levelsTableView.selectRow(0)
        
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
            
    def display_all_lines_table(self):  
        # query_string = f'(wavenumber >= {wn_low}) & (wavenumber <= {wn_high})'  # ! do this on the fly! From a matched_lines part of the hdf5file
        # data = pd.DataFrame(self.fileh.root.XXX.read_where(query_string))

        model = tm.linesTableModel(self.matched_lines)
        self.allLinesTableView.setModel(model)
        
        # Set all of the correct flags and views
        self.allLinesTableView.setSortingEnabled(True)
        self.allLinesTableView.setAlternatingRowColors(True)
        self.allLinesTableView.setSelectionBehavior(QtWidgets.QTableView.SelectRows)  # so a full row is selected when any cell is clicked
        # self.allLinesTableView.horizontalHeader().setStretchLastSection(True)
        stylesheet = "::section{background-color:rgb(166, 217, 245); border-radius:14px; font:bold}"  # here is where you set the table header style
        self.allLinesTableView.horizontalHeader().setStyleSheet(stylesheet)
        self.allLinesTableView.resizeColumnsToContents()
        
    def display_lines_table(self): 
        """Displays all of the lines associated with a user selected upper level"""
        if self.level_lines.empty:  # if there are no lines from the upper level
            self.linesTableView.hide()
            
        else:  # display the lines from the upper level
            model = tm.linesTableModel(self.level_lines)
            self.linesTableView.setModel(model)

            self.linesTableView.resizeColumnsToContents()   
            # self.linesTableView.horizontalHeader().setStretchLastSection(True)
            self.linesTableView.show()
    
    def get_linelists(self): 
        """ Returns a dictionary containing all of the linelists associated with each spectrum (spectum name is used as the dict key)"""       
        spectra_names = self.fileh.root.spectra._v_groups.keys()        
               
        linelists = {}
        for spectrum_name in spectra_names:
            spectrum_group = self.fileh.get_node(self.fileh.root.spectra, spectrum_name)
            
            try:
                linelists[spectrum_name] = pd.DataFrame(spectrum_group.linelist.read())
            except:  # is there is no linelist associated with a spectrum
                print(f'{spectrum_group} has no linelist')    
        
        return linelists    
            
    def merge_linelists(self):
        
        self.matched_lines = self.matched_lines[self.matched_lines['ritz_wavenumber'].notna()]  # drop all rows without a ritz wavenumber i.e. that don;t have a matching enrgy level
        self.matched_lines = self.matched_lines.sort_values('ritz_wavenumber')

        for linelist in self.linelists:
            self.linelists[linelist] = self.linelists[linelist].add_suffix(f'__{linelist}')
            self.matched_lines = pd.merge_asof(self.matched_lines, self.linelists[linelist], left_on='ritz_wavenumber', right_on=f'wavenumber__{linelist}', tolerance=self.match_tolerance, direction='nearest')
    
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