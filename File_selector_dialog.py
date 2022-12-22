from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QTextEdit
from PyQt5 import uic
import sys
from nso_to_hdf import *


class UI(QMainWindow):
    def __init__(self):
        super(UI,self).__init__()
        uic.loadUi("File_selector.ui",self)

        self.actionOpen_File.triggered.connect(self.getfilename)
        self.actionCreate_HDF5_file.triggered.connect(self.create_hdf5)
        self.actionAdd_to_HDF5_file.triggered.connect(self.add_linelist_to_hdf5)
        self.actionAdd_levels_to_HDF5_file.triggered.connect(self.add_levels_to_hdf5)
        self.actionPlot.triggered.connect(self.plot)
        self.actionExit.triggered.connect(self.exit)

        self.show()

    def getfilename(self):
        self.fname = QFileDialog.getOpenFileName(self, "Open File", "", "Header Files (*.hdr);;All Files (*)")
        if self.fname:
#            print(fname[0])
            if self.fname[0][-4:] == ".hdr":
                self.hdr = read_header(self.fname[0])
                print("File %s contains %7d points from %10.4f to %10.4f" %
                     (self.fname[0], int(self.hdr["npo"]), float(self.hdr["wstart"]), float(self.hdr["wstop"])))


                datfile = self.fname[0][:-4] + ".dat"
                if exists(datfile):
                    self.spec = read_data(datfile)
                    print(len(self.spec)," data read")

                else:
                    print("No data file found corresponding to header.")

                    #                if i[-4:] == ".lin":


    def create_hdf5(self):
        write_hdf5(self.fname[0][0:-4],self.spec,self.hdr)

    def display_message(self):
        print("Display message clicked")

    def plot(self):
        print("Plot button clicked")
        plot_spectrum(self.spec,self.hdr)

    def add_linelist_to_hdf5(self):
        self.linfile = QFileDialog.getOpenFileName(self, "Open File", "", "linelists (*corr);;All Files (*)")
        add_intcorr(self.fname[0][0:-4],self.linfile[0])

    def add_levels_to_hdf5(self):
        self.levfile = QFileDialog.getOpenFileName(self,"Open File", "", "Levels (*.lev);;All Files (*)")
        add_levels("CrII_levs.hdf5",self.levfile)

    def exit(self):
        sys.exit()


app = QApplication(sys.argv)
UIWindow = UI()
app.exec_()
