import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QMimeData, Qt, QUrl, pyqtSignal, QObject, QPoint


class TreeWidget(QtWidgets.QTreeWidget):
    dropped = pyqtSignal(str,str)
    def __init__(self, parent):
        super(TreeWidget, self).__init__(parent)
        #print("hello tree")
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.startPos = self.pos()





    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        super(TreeWidget, self).mousePressEvent(e)
        self.startPos = e.pos()
        self.setAcceptDrops(True)


    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        super(TreeWidget, self).dragMoveEvent(event)
        width = self.width()
        height = self.height()
        #print(type(width))


        if event.source() == self:

            current_item = self.itemAt(self.startPos)

            name = current_item.text(0)
            id = current_item.whatsThis(0)
            #print(self.startPos.x())
            #current_item_pos_x = str(self.startPos.x())
            #current_item_pos_y = str(self.startPos.y())
            #index = current_item.
            #url = [QUrl(id), QUrl(name), QUrl(current_item_pos_x), QUrl(current_item_pos_y)]
            url = [QUrl(id), QUrl(name)]
            event.mimeData().setUrls(url)

            drop_to_item_pos = event.pos()
            #drop_to_item = self.itemAt(drop_to_item_pos)

            event.mimeData().setUrls(url)




    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        data = event.mimeData()

        if data.hasUrls():
            #print(data.urls())
            id = data.urls()[0].url()
            #print(id)
            name = data.urls()[1].url()


        drop_pos = event.pos()
        drop_to_item = self.itemAt(drop_pos)

        if drop_to_item == None:
            drop_to_item_id = "root"
        else:
            drop_to_item_id = drop_to_item.whatsThis(0)

        #if event.source() == self:
            #x = int(data.urls()[2].url())
            #y = int(data.urls()[3].url())
            #print("folder drag " + name)
            #drag_item_pos = QPoint(x, y)
            #drag_item = self.itemAt(drag_item_pos)

            #a = drag_item.takeChildren()
            #for i in a:
            #    print(i.text(0))

            #if drag_item == drop_to_item:
            #    event.ignore()
            #    self.setDragEnabled(False)
             #   return

        print("ts" + id +"   hhhh" +  drop_to_item_id)
        self.dropped.emit(id,drop_to_item_id)














