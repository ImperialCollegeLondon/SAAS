
#!/usr/bin/env python

import h5py
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import pyqtProperty
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel, QLineEdit, QFormLayout, QFileDialog, QPushButton
from nso_to_hdf import *

class QIComboBox(QtWidgets.QComboBox):
    def __init__(self,parent=None):
        super(QIComboBox, self).__init__(parent)


class MagicWizard(QtWidgets.QWizard):
    def __init__(self, parent=None):
        super(MagicWizard, self).__init__(parent)
        self.addPage(PageInfo(self))
        self.addPage(Page1(self))
        self.addPage(Page2(self))
        self.setWindowTitle("SAAS - New Project Wizard")
        self.resize(640,480)
        
        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.onFinish) 
        
        # Filename variables #
        self.spectrum_hdr = ''
        self.spectrum_dat = ''
        self.linelist_file = ''
        self.level_file = ''
        self.calc_file = ''
        self.prev_idents_file = ''
        self.project_title = ''
        self.user = ''
        self.institute = ''         
           
    def onFinish(self):  # this could be where we do all of the hdf5 creation etc. That would be best as the file won't be created if the user presses the cancel button.
        print(self.user, self.project_title, self.institute)
        print(self.spectrum_hdr, self.spectrum_dat, self.linelist_file, self.level_file, self.prev_idents_file)


class PageInfo(QtWidgets.QWizardPage):
    def __init__(self,parent=None):
        """ 
        Basic information about the project and its creator
        """
        super(PageInfo, self).__init__(parent)
        self.setTitle('Project Information')
        self.setSubTitle('This wizard will help you create a hdf5 file for your branching fraction project\n')
        #self.heading = QLabel()
        self.title_label = QLabel()
        self.title = QLineEdit()
        self.user_label = QLabel()
        self.user = QLineEdit()
        self.inst_label = QLabel()
        self.institute = QLineEdit()
        # self.CreateHDF = QPushButton("Create HDF5 File")
        # self.CreateHDF.clicked.connect(self._create_hdf5)

        layout = QtWidgets.QFormLayout()
        #layout.addRow(self.heading)
        layout.addRow(self.title_label,self.title)
        layout.addRow(self.user_label,self.user)
        layout.addRow(self.inst_label,self.institute)
        # layout.addRow(self.CreateHDF)
        self.setLayout(layout)

    def initializePage(self):
        #self.heading.setText("This wizard will help you create a hdf5 file for your branching fraction project")
        self.title_label.setText("Enter a title for your project")
        self.user_label.setText("Enter your name ")
        self.inst_label.setText("Enter your institution and supervisor if student")
        
        next_button = self.wizard().button(QtWidgets.QWizard.NextButton)  # I think people will forget to clicke the "Create HDF" button, so I connected the function to the next button instead - we could connect it to the "finish" button and do all of this at the end?
        next_button.clicked.connect(self._create_hdf5)

    def _create_hdf5(self):
        # hdf_file = h5py.File(str(self.title.text()) + ".hdf5",'w')
        # spectrum_group = hdf_file.create_group("Spectra")
        print('TEST')  # just in for testing so I don't create the file over and over
        
        self.wizard().project_title = self.title.text()
        self.wizard().user = self.user.text()
        self.wizard().institute = self.institute.text()
        
        next_button = self.wizard().button(QtWidgets.QWizard.NextButton) 
        next_button.disconnect()   # otherwise the next button permantently connected to the _create_hdf function
        next_button.clicked.connect(self.wizard().next)  # reconnects to its original function


class Page1(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(Page1, self).__init__(parent)
        
        self.setTitle('File Selection')
        self.setSubTitle('Select files to add to the project. Files marked with * are required for project creation.')

        self.SpectrumFile = QPushButton("Add Spectrum*")
        self.LinesFile = QPushButton("Add Linelist*")
        self.LevelsFile = QPushButton("Add Levels file*")
        self.CalcsFile = QPushButton("Add Calculations*")
        self.IDFile = QPushButton("Add Previous Identifications")

        self.SpectrumFile.clicked.connect(self._add_spectrum)
        self.LinesFile.clicked.connect(self._add_linelist)
        self.LevelsFile.clicked.connect(self._add_levels)
        self.CalcsFile.clicked.connect(self._add_calcs)
        self.IDFile.clicked.connect(self._add_prev_idents)

        layout = QtWidgets.QVBoxLayout()
        #layout.addWidget(QLabel("Now add the files to the project"))
        layout.addWidget(self.SpectrumFile)
        layout.addWidget(self.LinesFile)
        layout.addWidget(self.LevelsFile)
        layout.addWidget(self.CalcsFile)
        layout.addWidget(self.IDFile)        
        self.setLayout(layout)
        
        self.tick_icon = QtGui.QIcon('tick-button.png')        
      
    def _add_spectrum(self): # should we make this simply look for a folder and then pull all of the .hdrs and .dats in that folder? 
               
        fname = QFileDialog.getOpenFileName(self, "Select Spectrum Header File", "", "Header Files (*.hdr);;All Files (*)")
        if fname:
#            print(spectrum[0])
            if fname[0][-4:] == ".hdr":
                self.hdr = read_header(fname[0])
                print("File %s contains %7d points from %10.4f to %10.4f" %
                     (fname[0], int(self.hdr["npo"]), float(self.hdr["wstart"]), float(self.hdr["wstop"])))


                datfile = fname[0][:-4] + ".dat"
                if exists(datfile):
                    self.spec = read_data(datfile)
                    print(len(self.spec)," data read")

                else:
                    print("No data file found corresponding to header.")       
                    
                self.wizard().spectrum_hdr = fname[0]   # pass back to main Wizard class
                self.wizard().spectrum_dat = datfile
                
                self.SpectrumFile.setIcon(self.tick_icon)  # add a tick to show the user it has been completed.
                
    
    def _add_linelist(self):             
        fname = QFileDialog.getOpenFileName(self, "Select Linelist File", "", "Header Files (*.txt);;All Files (*)")
        if fname:                
            self.wizard().linelist_file = fname[0]   
            self.LinesFile.setIcon(self.tick_icon) 
            
    def _add_levels(self):             
        fname = QFileDialog.getOpenFileName(self, "Select Levels File", "", "Header Files (*.lev);;All Files (*)")
        if fname:                
            self.wizard().level_file = fname[0]   
            self.LevelsFile.setIcon(self.tick_icon) 
            
    def _add_calcs(self):             
        fname = QFileDialog.getOpenFileName(self, "Select Calculations File", "", "Header Files (*.txt);;All Files (*)")
        if fname:                
            self.wizard().calc_file = fname[0]  
            self.CalcsFile.setIcon(self.tick_icon) 
            
    def _add_prev_idents(self):             
        fname = QFileDialog.getOpenFileName(self, "Select Previous Identifications File", "", "Header Files (*.txt);;All Files (*)")
        if fname:                
            self.wizard().prev_idents_file = fname[0]  
            self.IDFile.setIcon(self.tick_icon)  


class Page2(QtWidgets.QWizardPage):
    def __init__(self, parent=None):
        super(Page2, self).__init__(parent)
        self.label1 = QtWidgets.QLabel()
        self.label2 = QtWidgets.QLabel()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        self.setLayout(layout)

    def initializePage(self):
        self.label1.setText("Example text")
        self.label2.setText("Example text")


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    wizard = MagicWizard()
    wizard.show()
    sys.exit(app.exec_())