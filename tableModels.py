from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class levelTableModel(QtCore.QAbstractTableModel):
    """Model for the levels table view in the main window. Takes a Pandas dataframe and displays the data automatically."""
    def __init__(self, data):
        super(levelTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        """The data to be displayed. This is the levels dataframe"""
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            
            if isinstance(value, bytes):  # changes from byte string to utf-8 for display only ! could cast whole pandas column to utf-8 if needed
                value = value.decode('utf-8')
                        
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        """Custom header labels for the table columns"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                
                header_labels = ['Designation',  # custom labels for columns
                                 'Energy (cm-1)',
                                 'Energy Unc. (cm-1)',
                                 'J',
                                 'Lifetime (ns)',
                                 'Lifetime Unc. (ns)',
                                 'Parity',
                                 'Species']
                
                return str(header_labels[section])
        
            # if orientation == Qt.Vertical:  # row labels
            #     return str('')
            
    def sort(self, Ncol, order):
        """Sort table by given column number."""
        self.layoutAboutToBeChanged.emit()  # tells the view controller that the underlying data is about to be changed
        self._data = self._data.sort_values(list(self._data)[Ncol], ascending=order == Qt.AscendingOrder)  # list(self._data) gives a list of the dataFrame headers
        self.layoutChanged.emit()
            
            
class linesTableModel(QtCore.QAbstractTableModel):
    """Model for the lines table view in the main window. Takes a Pandas dataframe and displays the data automatically."""
    def __init__(self, data):
        super(linesTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        """The data to be displayed. This is the lines dataframe"""
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            
            if isinstance(value, bytes):  # changes from byte string to utf-8 for display only ! could cast whole pandas column to utf-8 if needed
                value = value.decode('utf-8')
                        
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        """Custom header labels for the table columns"""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                
                if section <= 7:  # the first 8 columns
                
                    header_labels = ['Intensity',
                                    'log(gf)',  # custom labels for columns
                                    'Lower Level',
                                    'Lower\nEnergy (cm-1)',                                 
                                    'Ritz\nWavenumber (cm-1)',
                                    'Upper Level', 
                                    'Upper\nEnergy (cm-1)', 
                                    'Obs. \nWavenumber (cm-1)']
                    
                    return str(header_labels[section])
                
                else:
                    return 'Test Header'
        
            # if orientation == Qt.Vertical:  # row labels
            #     return str('')
            
    def sort(self, Ncol, order):
        """Sort table by given column number."""
        self.layoutAboutToBeChanged.emit()  # tells the view controller that the underlying data is about to be changed
        self._data = self._data.sort_values(list(self._data)[Ncol], ascending=order == Qt.AscendingOrder)  # list(self._data) gives a list of the dataFrame headers
        self.layoutChanged.emit()
            