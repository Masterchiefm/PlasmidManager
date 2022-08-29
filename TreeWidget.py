import typing

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QMimeData, Qt, QUrl, pyqtSignal, QObject, QPoint


class TreeWidget(QtWidgets.QTreeWidget):
    dropped = pyqtSignal(list,str)
    errorGot = pyqtSignal(str)
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
        self.setDragEnabled(True)


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
            url = [QUrl(id)]
            event.mimeData().setUrls(url)

            drop_to_item_pos = event.pos()
            #drop_to_item = self.itemAt(drop_to_item_pos)

            event.mimeData().setUrls(url)
            if id == None:
                event.ignore()
                self.setDragEnabled(False)




    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        data = event.mimeData()

        #if data.hasUrls():
        id_urls = data.urls()


        # 获取要扔到的目的地item
        drop_pos = event.pos()
        drop_to_item = self.itemAt(drop_pos)

        # 判断是否扔到根目录，是，设id为root，不是，就设为目的地id
        if drop_to_item == None:
            drop_to_item_id = "root"
        else:
            drop_to_item_id = drop_to_item.whatsThis(0)


        # 生成返回的id号
        ids = []
        for id_url in id_urls:
            id = id_url.url()
            if id:
                ids.append(id)


        self.dropped.emit(ids, drop_to_item_id)


















