import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QMimeData, Qt, QUrl, pyqtSignal, QObject


class TreeWidget(QtWidgets.QTreeWidget):
    dropped = pyqtSignal(str,str)
    def __init__(self, parent):
        super(TreeWidget, self).__init__(parent)
        #print("hello tree")
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.startPos = None





    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        super(TreeWidget, self).mousePressEvent(e)
        self.startPos = e.pos()


    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        super(TreeWidget, self).dragMoveEvent(event)
        if event.source() == self:
            #print("drag self")

            current_item = self.itemAt(self.startPos)
            name = current_item.text(0)
            id = current_item.whatsThis(0)
            url = [QUrl(id), QUrl(name)]
            event.mimeData().setUrls(url)
            #event.mimeData().setData()


    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        data = event.mimeData()
        if data.hasUrls():
            #print(data.urls())
            id = data.urls()[0].url()
            name = data.urls()[0].url()


        drop_pos = event.pos()
        drop_to_item = self.itemAt(drop_pos)
        if drop_to_item == None:
            drop_to_item_id = "root"
        else:
            drop_to_item_id = drop_to_item.whatsThis(0)

        self.dropped.emit(id,drop_to_item_id)













