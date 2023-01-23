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
        self.layoutAboutToBeChanged.emit()
        self._data = self._data.sort_values(list(self._data)[Ncol], ascending=order == Qt.AscendingOrder)  # list(self._data) gives a list of the dataFrame headers
        self.layoutChanged.emit()
            