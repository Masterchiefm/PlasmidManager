

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QMimeData, Qt, QUrl
from PyQt5.QtGui import QDrag, QPixmap
from PyQt5.QtWidgets import QApplication


class TableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super(TableWidget, self).__init__(parent)
        #print("table loaded")
        self.setDragEnabled(True)
        self.startPos = self.pos()
        self.setAcceptDrops(True)


    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        #print("mouse pressed")
        self.setAcceptDrops(True)
        self.startPos = e.pos()
        super(TableWidget, self).mousePressEvent(e)


    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        super(TableWidget, self).dragMoveEvent(e)
        if e.source() == self:
            current_item = self.itemAt(self.startPos)
            name = current_item.text()
            id = current_item.whatsThis()
            url = [QUrl(id),QUrl(name)]
            e.mimeData().setUrls(url)
        else:
            #print("g")
            self.setAcceptDrops(False)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        return
