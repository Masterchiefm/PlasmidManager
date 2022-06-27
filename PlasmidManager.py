import sys


import dataBase
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import pandas as pd
import os
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QFileDialog

from GUI import Ui_MainWindow


class MyMainWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWin, self).__init__(parent)
        self.table = dataBase.TABLE()
        try:
            self.table.readJson("data.json")
        except:
            self.table.writeJson()
            self.table.readJson("data.json")
        self.setupUi(self)
        self.tableWidget.setSortingEnabled(True)
        self.showTable()



        #self.pushButton_AutoAdd.clicked.connect(self.autoFill)
        self.pushButton_add.clicked.connect(self.add)
        self.pushButton_WriteTable.clicked.connect(self.saveTable)
        self.textEdit_recognitionArea.textChanged.connect(self.autoFill)
        self.textEdit_recognitionArea2.textChanged.connect(self.autoFill2)
        self.pushButton_clear.clicked.connect(self.clear)
        self.pushButton_Open.clicked.connect(self.openFile)
        self.pushButton_del.clicked.connect(self.delSeleted)
        self.pushButton_search.clicked.connect(self.search)
        self.pushButton_filter.clicked.connect(self.statusFilter)
        self.pushButton_edit.clicked.connect(self.edit)
        self.pushButton_clear_2.clicked.connect(self.clear)
        self.pushButton_ImportTable.clicked.connect(self.importSheet)
        self.pushButton_share.clicked.connect(self.share)
        #self.pushButton_addPath.clicked.connect(self.autoFillPath)
        self.pushButton_openPath.clicked.connect(self.openPath)



        self.tableWidget.currentCellChanged.connect(self.showSelection)
        #self.tableWidget.itemSelectionChanged.connect(self.changeSelectedTable)
        #self.tableWidget.itemChanged.connect(self.changeSelectedTable)
        self.tableWidget.itemSelectionChanged.connect(self.saveChange)
        self.textEdit_recognitionArea2.setStyleSheet("background:gray")

        self.selectedData = ''
        self.selectedRow = 0
        self.selectedCol = 0
        self.oldID = ""



    def saveChange(self):
        try:
            index = self.tableWidget.selectionModel().currentIndex()
            row = int(index.row())
            column = int(index.column())

            # print(str(row)+str(column)+"changed")
            id = self.tableWidget.item(row, 7).text()

            #print("\n\n #####" + id + " selected")
            data = self.tableWidget.item(row,column).text()
            oldData = self.selectedData
            #print("oldData is " + self.selectedData)
            #print("selected " + data)
            nowData = self.tableWidget.item(self.selectedRow,self.selectedCol).text()
            #print("之前选的data现在是 " + nowData)


            self.selectedData = data
            #print(self.selectedData)
            if nowData != oldData:
                lable = {
                    0: "abbr",
                    1: "name",
                    2: "status",
                    4: "tag",
                    3: "info",
                    5: "path",
                    6: "id"
                }
                if self.oldID != "":
                    self.table.table[self.oldID][lable[column]] = nowData
                    self.table.writeJson()
                    #print("changed")

            self.selectedRow = row
            self.selectedCol = column
            self.oldID = id




        except Exception as e:
            print(e)





    def autoFillPath(self):
        #print("dddd")
        file = self.textEdit_recognitionArea.toPlainText()
        filePath = file.replace("file:///","")
        fileAbsPaths = []
        if os.path.isdir(filePath):
            files = os.listdir(filePath)
            parentPath = filePath
            if "/" in parentPath[-1]:
                pass
            else:
                parentPath = parentPath + "/"

            combine = lambda str2: parentPath + str2

            fileAbsPaths = list(map(combine,files))
        else:
            fileAbsPaths.append(filePath)

        #print(fileAbsPaths)
        files = []
        for f in fileAbsPaths:
            if ".dna" in f.lower():
                files.append(f)
            elif ".gb" in f.lower():
                files.append(f)
        status = self.comboBox.currentText()
        tags = self.lineEdit_tag.text().replace("，", ",")

        #self.lineEdit_name.setText(name)
        #self.lineEdit_path.setText(filePath)
        #
        for f in files:
            name = f.split("/")[-1]
            plasmid = dataBase.PLASMID()
            plasmid.info["name"] = name
            plasmid.info["abbr"] = ""
            plasmid.info["tag"] = tags
            plasmid.info["info"] = ""
            plasmid.info["path"] = f
            plasmid.info["status"] = status
            if plasmid.info["name"] == "":
                pass
            else:
                self.table.addItem(plasmid)

        self.table.writeJson()
        self.showTable()
        self.clear()

    def autoFill(self):
        file = self.textEdit_recognitionArea.toPlainText()
        filePath = file.replace("file:///", "")
        name = file.split("/")[-1]
        self.lineEdit_name.setText(name)
        self.lineEdit_path.setText(filePath)


    def autoFill2(self):
        file = self.textEdit_recognitionArea2.toPlainText()
        path = file.replace("file:///", "")
        self.lineEdit_selectedPath.setText(path)


    def add(self):
        file = self.textEdit_recognitionArea.toPlainText()
        filePath = file.replace("file:///", "")
        if os.path.isdir(filePath):
            self.autoFillPath()
            return 0


        plasmid = dataBase.PLASMID()
        plasmid.info["name"] = self.lineEdit_name.text()
        plasmid.info["abbr"] = self.lineEdit_abbr.text()
        tags = self.lineEdit_tag.text().replace("，",",")
        plasmid.info["tag"] = tags
        plasmid.info["info"] = self.lineEdit_info.text()
        plasmid.info["path"] = self.lineEdit_path.text()
        plasmid.info["status"] = self.comboBox.currentText()
        if plasmid.info["name"] == "":
            pass
        else:
            self.table.addItem(plasmid)
            self.table.writeJson()
        #print(self.table.table)
        self.showTable()
        self.clear()

    def clear(self):
        self.lineEdit_tag.clear()
        self.lineEdit_path.clear()
        self.lineEdit_name.clear()
        self.lineEdit_abbr.clear()
        self.lineEdit_info.clear()
        self.textEdit_recognitionArea.clear()
        self.textEdit_recognitionArea2.clear()


    def showTable(self):
        #t0 = time.perf_counter()
        sheet = self.table.toTable()
        index = 0
        self.tableWidget.hide()
        self.tableWidget.setRowCount(len(sheet.index))
        brushR = QtGui.QBrush(QtGui.QColor(200, 86, 75))
        brushR.setStyle(QtCore.Qt.SolidPattern)

        brushG = QtGui.QBrush(QtGui.QColor(110,200,82))
        brushG.setStyle(QtCore.Qt.SolidPattern)

        brushY = QtGui.QBrush(QtGui.QColor(255, 0, 255))
        brushY.setStyle(QtCore.Qt.SolidPattern)

        brushB = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brushB.setStyle(QtCore.Qt.SolidPattern)

        for id in sheet.index:





            #print(id)
            name = QTableWidgetItem(sheet.loc[id,"name"])

            data = dict(sheet.loc[id])


            self.tableWidget.setItem(index,0,QTableWidgetItem(data["abbr"]))
            status = data["status"]
            statusItem = QTableWidgetItem(status)
            importedTime = QTableWidgetItem(data["time"])

            if "完成" in status:
                pass
            elif "测" in status:
                statusItem.setForeground(brushR)
            elif "未构建" in status:
                statusItem.setForeground(brushG)
            elif "失败" in status:
                statusItem.setForeground(brushY)
            else:
                statusItem.setForeground(brushB)
            #T0 = time.perf_counter()
            self.tableWidget.setItem(index, 2, statusItem)
            #T1 = time.perf_counter()
            self.tableWidget.setItem(index, 4, QTableWidgetItem(data["tag"]))
            self.tableWidget.setItem(index, 3, QTableWidgetItem(data["info"]))
            pathItem = QTableWidgetItem(data["path"])
            if os.path.exists(data["path"]):
                pass
            else:
                pathItem.setForeground(brushR)
                name.setForeground(brushR)

            self.tableWidget.setItem(index, 1, name)
            self.tableWidget.setItem(index, 5, pathItem)

            self.tableWidget.setItem(index, 7, QTableWidgetItem(id))
            self.tableWidget.setItem(index,6,importedTime)
            index = index + 1

            #dT = float(T1 - T0)
            #print("循环内用时" + str(dT))
        self.tableWidget.resizeColumnToContents(0)
        self.tableWidget.resizeColumnToContents(1)
        self.tableWidget.resizeColumnToContents(2)
        self.tableWidget.resizeColumnToContents(3)
        self.tableWidget.resizeColumnToContents(6)
        #t#1 = time.perf_counter()
        #dt = float(t1 - t0)
        self.tableWidget.show()
        #print("总时"+str(dt))

    def saveTable(self):
        path,fileType= QFileDialog.getSaveFileName(self,"path","","excel(*.xlsx)")
        #print(path)
        self.table.writeTable(path)




    def openFile(self):
        try:
            index = self.tableWidget.selectionModel().currentIndex()
            row = index.row()
            path = self.tableWidget.item(row, 5).text()
            if path == "":
                QMessageBox.about(self,"找不到文件","路径未设置，请修改路径")
            else:
                os.startfile(path)
        except Exception as e:
            QMessageBox.about(self,"找不到文件",str(e)+"\n 请再次确认并修改文件路径!")


    def openPath(self):
        try:
            index = self.tableWidget.selectionModel().currentIndex()
            row = index.row()
            filePath = self.tableWidget.item(row, 5).text()
            if filePath == "":
                QMessageBox.about(self, "找不到目录", "路径未设置，请修改路径")
            else:
                parentPath = os.path.dirname(filePath)
                os.startfile(parentPath)
        except Exception as e:
            QMessageBox.about(self, "找不到目录", str(e) + "\n 请再次确认并修改文件路径!")

    def delSeleted(self):
        try:
            index = self.tableWidget.selectionModel().currentIndex()
            row = index.row()
            id = self.tableWidget.item(row, 7).text()
            self.table.table.pop(id)
            self.table.writeJson()
        except Exception as e:
            print(e)
            #pass
        self.showTable()

    def showArrangedTable(self,sheet):
        sheet = sheet
        #index = 0
        self.tableWidget.setRowCount(len(sheet.index))
        for id in sheet.index:
            # print(id)
            name = QTableWidgetItem(sheet.loc[id, "name"])
            index = sheet.index.get_loc(id)
            self.tableWidget.setItem(index, 1, name)

            self.tableWidget.setItem(index, 0, QTableWidgetItem(sheet.loc[id, "abbr"]))
            # tag = sheet.loc[id,"tag"]

            status = sheet.loc[id, "status"]
            statusItem = QTableWidgetItem(status)

            if "完成" in status:
                pass

            elif "测" in status:
                brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                statusItem.setForeground(brush)

            elif "未构建" in status:
                brush = QtGui.QBrush(QtGui.QColor(0, 255, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                statusItem.setForeground(brush)
            else:
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                statusItem.setForeground(brush)

            self.tableWidget.setItem(index, 2, statusItem)

            self.tableWidget.setItem(index, 4, QTableWidgetItem(sheet.loc[id, "tag"]))
            self.tableWidget.setItem(index, 3, QTableWidgetItem(sheet.loc[id, "info"]))
            self.tableWidget.setItem(index, 5, QTableWidgetItem(sheet.loc[id, "path"]))
            self.tableWidget.setItem(index,6,QTableWidgetItem(sheet.loc[id,"time"]))

            self.tableWidget.setItem(index, 7, QTableWidgetItem(id))
            #index = index + 1
        self.tableWidget.resizeColumnToContents(0)
        self.tableWidget.resizeColumnToContents(1)
        self.tableWidget.resizeColumnToContents(2)
        self.tableWidget.resizeColumnToContents(3)

    def search(self):
        text = self.lineEdit_search.text()
        #print(text)
        if text == "":
            return 0

        sheet = self.table.toTable()
        text = text.lower()

        newSheet = pd.DataFrame(columns=sheet.columns)
        f = lambda a, b: a in b
        for id in sheet.index:
            name = sheet.loc[id,"name"]
            abbr = sheet.loc[id,"abbr"]
            status = sheet.loc[id,"status"]
            info = sheet.loc[id,"info"]
            tag = sheet.loc[id,"tag"]
            path = sheet.loc[id,"path"]

            option = self.comboBox_search.currentText()
            if option == "全局":
                combinedInfo = (abbr + name + status + info + tag + path).lower()
            elif option == "名称":
                combinedInfo = name.lower()
            elif option == "标签":
                combinedInfo = tag.lower()

            elif option == "简写":
                combinedInfo = abbr.lower()

            elif option == "备注":
                combinedInfo = info.lower()
            else:
                combinedInfo = (abbr + name + status + info + tag + path).lower()


            if text in combinedInfo:
                newSheet.loc[id] = sheet.loc[id]

        self.showArrangedTable(newSheet)

    def statusFilter(self):
        text = self.comboBox_status.currentText()
        #print(text)
        if text == "":
            return 0
        elif text == "显示全部":
            self.showTable()
            return 0

        sheet = self.table.toTable()
        text = text.lower()

        newSheet = sheet.loc[sheet["status"] == text]
        self.showArrangedTable(newSheet)

    def showSelection(self):
        try:
            index = self.tableWidget.selectionModel().currentIndex()
            row = index.row()
            column = index.column()
            #print(str(row)+str(column)+"changed")
            #id = self.tableWidget.item(row,6).text()
            #print(id)

            lable = {
                0:"abbr",
                1:"name",
                2:"status",
                4:"tag",
                3:"info",
                5:"path",
                7:"id"
            }

            self.lineEdit_selectedName.setText(self.tableWidget.item(row,1).text())
            self.lineEdit_selectedAbbr.setText(self.tableWidget.item(row,0).text())
            self.lineEdit_selectedInfo.setText(self.tableWidget.item(row,3).text())
            self.lineEdit_selectedTag.setText(self.tableWidget.item(row,4).text())
            self.comboBox_selectedStatus.setCurrentText(self.tableWidget.item(row,2).text())
            self.lineEdit_selectedID.setText(self.tableWidget.item(row,7).text())
            self.lineEdit_selectedPath.setText(self.tableWidget.item(row,5).text())


        except Exception as e:
            #print(e)
            pass

    def edit(self):
        id = self.lineEdit_selectedID.text()
        name =self.lineEdit_selectedName.text()
        abbr = self.lineEdit_selectedAbbr.text()
        status = self.comboBox_selectedStatus.currentText()
        tag = self.lineEdit_selectedTag.text()
        info = self.lineEdit_selectedInfo.text()
        path = self.lineEdit_selectedPath.text()
        self.table.table[id]["name"] = name
        self.table.table[id]["abbr"] = abbr
        self.table.table[id]["status"] = status
        self.table.table[id]["tag"] = tag
        self.table.table[id]["info"] = info
        self.table.table[id]["path"] = path
        self.table.writeJson()
        self.showTable()
        QMessageBox.about(self,"修改","完成！")


    def importSheet(self):
        try:
            path, fileType = QFileDialog.getOpenFileName(self,"path","","excel(*.xlsx)")
            #print(path)
            sheet = pd.read_excel(path)
        except:
            return 0


        try:
            #t0 = int(time.time_ns())
            for i in sheet.index:
                plasmid = dataBase.PLASMID()
                plasmid.info["name"] = str(sheet.loc[i,"name"])
                abbr = str(sheet.loc[i,"abbr"])
                if abbr == "nan":
                    plasmid.info["abbr"] = ""
                else:
                    plasmid.info["abbr"] = str(sheet.loc[i,"abbr"])

                tags = str(sheet.loc[i,"tag"]).replace("，",",")
                if tags == "nan":
                    plasmid.info["tag"] = ""
                else:
                    plasmid.info["tag"] = tags

                info = str(sheet.loc[i,"info"])
                if info == "nan":
                    plasmid.info["info"] = ""
                else:
                    plasmid.info["info"] = info

                plasmid.info["path"] = str(sheet.loc[i,"path"])
                plasmid.info["status"] = str(sheet.loc[i,"status"])

                #t1 = int(time.time_ns())
                #while (t1 == t0):
                    #t1 = int(time.time_ns())

                self.table.addItem(plasmid)
            self.table.writeJson()
            self.showTable()
        except:
            QMessageBox.about(self,"错误","不支持该表格形式，请确保表格内有对应列")


    def share(self):
        items = self.tableWidget.selectedItems()
        sheet = self.table.toTable()
        newSheet = pd.DataFrame(columns=sheet.columns)
        #print(newSheet)
        selectedRows = []
        for i in items:
            row = i.row()

            if row in selectedRows:
                pass
            else:
                selectedRows.append(row)

        for i in selectedRows:
            row = i
            id = self.tableWidget.item(row,7).text()
            newSheet.loc[id,"abbr"] = self.tableWidget.item(row,0).text()
            newSheet.loc[id,'name'] =self.tableWidget.item(row,1).text()
            newSheet.loc[id,'status'] = self.tableWidget.item(row, 2).text()
            newSheet.loc[id,'info'] = self.tableWidget.item(row, 3).text()
            newSheet.loc[id,'tag'] = self.tableWidget.item(row, 4).text()
            newSheet.loc[id,'path'] = self.tableWidget.item(row, 5).text()
            newSheet.loc[id,'name'] = self.tableWidget.item(row, 1).text()
        try:
            path,fileType= QFileDialog.getSaveFileName(self,"path","","excel(*.xlsx)")
            newSheet.to_excel(path)
        except:
            pass








if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyMainWin()
    win.show()
    sys.exit(app.exec_())