# PlasmidManager
# By M.Q. at Shanghai
# 2022.06.29
# dependence：
# PyQt5,qt-tools,requests

# GUI显示相关模块
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from GUI import Ui_MainWindow

# 系统进程管理相关
from subprocess import getstatusoutput
from requests import get
from json import loads
import os
import sys

# 数据处理相关
import pandas as pd
import dataBase




class MyMainWin(QMainWindow, Ui_MainWindow):


    def __init__(self, parent=None):
        """质粒管理工具"""
        self.version = "1.2.3"

        super(MyMainWin, self).__init__(parent)

        #读取/初始化数据库
        self.table = dataBase.TABLE()
        try:
            self.table.readJson("data.json")
        except:
            self.table.writeJson()
            self.table.readJson("data.json")
        self.setupUi(self)
        self.tableWidget.setSortingEnabled(True)
        self.showArrangedTable(self.table.toTable())

        self.setWindowTitle("项目构建管理-v" + self.version)  #根据版本号改应用标题
        self.pushButton_add.clicked.connect(self.add)   #添加项目
        self.pushButton_WriteTable.clicked.connect(self.saveTable)      #将所有数据导出为excel表格
        self.textEdit_recognitionArea.textChanged.connect(self.autoFill)    #自动识别区1，用于添加
        self.textEdit_recognitionArea2.textChanged.connect(self.autoFill2)  #自动识别区2，用于识别修改后的文件路径
        self.textEdit_recognitionArea2.setStyleSheet("background:gray")
        self.pushButton_clear.clicked.connect(self.clear)   #清除识别区以及自动填入的内容
        self.pushButton_Open.clicked.connect(self.openFile)     #打开文件
        self.pushButton_del.clicked.connect(self.delSeleted)    #删除单条记录
        self.pushButton_search.clicked.connect(self.search)
        self.pushButton_filter.clicked.connect(self.statusFilter)
        self.pushButton_edit.clicked.connect(self.edit)     #保存更改
        self.pushButton_clear_2.clicked.connect(self.clear)     #更改区的信息清除
        self.pushButton_ImportTable.clicked.connect(self.importSheet)   #从excel表格导入数据
        self.pushButton_share.clicked.connect(self.share)   #导出选中项目为表格
        self.pushButton_openPath.clicked.connect(self.openPath)     #打开文件所在路径
        self.tableWidget.currentCellChanged.connect(self.showSelection)     #读取用户选定的格子信息，并填入右侧修改框中。

        self.action.triggered.connect(self.checkUpdate)     #菜单栏
        self.action_2.triggered.connect(self.about)
        self.action_4.triggered.connect(self.donate)

        self.checkTaskList()    #进程数量检查，确保只有一个进程运行

        self.tableWidget.itemSelectionChanged.connect(self.saveChange)  # 自动读取并保存用户对格子的修改
        self.selectedData = ''  #初始化修改的位置0，如果原始数据与现在数据不一样，就保存修改。
        self.selectedRow = 0
        self.selectedCol = 0
        self.oldID = ""


    def checkTaskList(self):
        taskList = getstatusoutput(['tasklist'])[1]

        # print(taskList)
        instance = taskList.count("PlasmidManager")
        if instance == 1: #打包好后，本程序会算是一个运行中的实例，所以会是1
            pass
        elif instance == 0:    #调试的时候，实例会是0
            pass
        else:
            QMessageBox.about(self,"错误","不能同时打开相同的进程")
            print(instance)
            sys.exit()



    def checkUpdate(self):
        """使用requests模块和GitHub api获取最新版本"""

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        latestInfo = get("https://gitee.com/api/v5/repos/MasterChiefm/PlasmidManager/releases/latest", timeout=2,  headers= headers)
        print(latestInfo)
        try:
            info = latestInfo.text
            info = loads(info)
            print(info)
            latestVersion = info["tag_name"]
            releaseInfo = info["body"]
            #print(latestVersion)

            if latestVersion == self.version:
                QMessageBox.about(self, "更新", "已经是最新")
            else:
                msg = latestVersion + "\n" + releaseInfo
                QMessageBox.about(self,"更新",msg)
                os.startfile("https://gitee.com/MasterChiefm/PlasmidManager/releases")



        except Exception as e:
            QMessageBox.about(self,"网络错误","无法连接到GitHub服务器")
            print(e)

    def about(self):
        """打开应用主页"""
        try:
            os.startfile("https://gitee.com/MasterChiefm/PlasmidManager")
        except:
            pass

    def donate(self):
        """收款码"""
        try:
            os.startfile("https://cdn.jsdelivr.net/gh/Masterchiefm/pictures/68747470733a2f2f6d6f716971696e2e636e2f77702d636f6e74656e742f75706c6f6164732f323032302f30342f64617368616e672e706e67.png")
        except:
            pass





    def saveChange(self):
        try:
            index = self.tableWidget.selectionModel().currentIndex()
            row = int(index.row())
            column = int(index.column())

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
                    self.table.table[self.oldID][lable[self.selectedCol]] = nowData
                    self.table.writeJson()
                   # print("changed")

            self.selectedRow = row
            self.selectedCol = column
            self.oldID = id




        except Exception as e:
            print(e)





    def autoFillPath(self,path):
        #print("dddd")

        filePath = path.replace("\n","")
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
        self.showArrangedTable(self.table.toTable())
        self.clear()

    def autoFill(self):
        file = self.textEdit_recognitionArea.toPlainText()
        filePath = file.replace("file:///", "")
        name = file.split("/")[-1]
        self.plainTextEdit_name.setPlainText(name)
        self.lineEdit_path.setText(filePath)


    def autoFill2(self):
        file = self.textEdit_recognitionArea2.toPlainText()
        path = file.replace("file:///", "")
        self.lineEdit_selectedPath.setText(path)


    def add(self):
        file = self.textEdit_recognitionArea.toPlainText()
        files = file.split("file:///")
        print(files)
        for f in files:
            if f == '':
                pass
            else:
                if os.path.isdir(f.replace("\n","")):
                    self.autoFillPath(f.replace("\n",""))
                else:
                    print('s')
                    plasmid = dataBase.PLASMID()
                    plasmid.info["name"] = f.split("/")[-1].replace("\n","")
                    plasmid.info["abbr"] = self.lineEdit_abbr.text()
                    tags = self.lineEdit_tag.text().replace("，", ",")
                    plasmid.info["tag"] = tags
                    plasmid.info["info"] = self.plainTextEdit_info.toPlainText()
                    plasmid.info["path"] = f.replace("\n","")
                    plasmid.info["status"] = self.comboBox.currentText()
                    if plasmid.info["name"] == "":
                        pass
                    else:
                        self.table.addItem(plasmid)


        self.table.writeJson()
        self.showArrangedTable(self.table.toTable())
        self.clear()
        return 0

    def clear(self):
        self.lineEdit_tag.clear()
        self.lineEdit_path.clear()
        self.plainTextEdit_name.clear()
        self.lineEdit_abbr.clear()
        self.plainTextEdit_info.clear()
        self.textEdit_recognitionArea.clear()
        self.textEdit_recognitionArea2.clear()


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
        self.showArrangedTable(self.table.toTable())

    def showArrangedTable(self,sheet):

        self.tableWidget.setRowCount(len(sheet.index))
        brushR = QtGui.QBrush(QtGui.QColor(200, 86, 75))
        brushR.setStyle(QtCore.Qt.SolidPattern)

        brushG = QtGui.QBrush(QtGui.QColor(110, 200, 82))
        brushG.setStyle(QtCore.Qt.SolidPattern)

        brushY = QtGui.QBrush(QtGui.QColor(255, 0, 255))
        brushY.setStyle(QtCore.Qt.SolidPattern)

        brushB = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brushB.setStyle(QtCore.Qt.SolidPattern)

        for id in sheet.index:
            # print(id)
            name = QTableWidgetItem(sheet.loc[id, "name"])
            index = sheet.index.get_loc(id)

            status = sheet.loc[id, "status"]
            statusItem = QTableWidgetItem(status)

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

            path = sheet.loc[id,"path"]
            pathItem = QTableWidgetItem(path)
            if os.path.exists(path):
                pass
            else:
                pathItem.setForeground(brushR)
                name.setForeground(brushR)

            self.tableWidget.setItem(index, 2, statusItem)
            self.tableWidget.setItem(index, 1, name)
            self.tableWidget.setItem(index, 5, pathItem)
            self.tableWidget.setItem(index, 0, QTableWidgetItem(sheet.loc[id, "abbr"]))
            self.tableWidget.setItem(index, 4, QTableWidgetItem(sheet.loc[id, "tag"]))
            self.tableWidget.setItem(index, 3, QTableWidgetItem(sheet.loc[id, "info"]))
            self.tableWidget.setItem(index,6,QTableWidgetItem(sheet.loc[id,"time"]))
            self.tableWidget.setItem(index, 7, QTableWidgetItem(id))


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
            self.showArrangedTable(self.table.toTable())
            #QMessageBox.about(self,"refresh","done!")
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

            self.plainTextEdit_selectedName.setPlainText(self.tableWidget.item(row,1).text())
            self.lineEdit_selectedAbbr.setText(self.tableWidget.item(row,0).text())
            self.plainTextEdit_info.setPlainText(self.tableWidget.item(row,3).text())
            self.lineEdit_selectedTag.setText(self.tableWidget.item(row,4).text())
            self.comboBox_selectedStatus.setCurrentText(self.tableWidget.item(row,2).text())
            self.lineEdit_selectedID.setText(self.tableWidget.item(row,7).text())
            self.lineEdit_selectedPath.setText(self.tableWidget.item(row,5).text())
            self.label_row.setText("当前选择"+str(row+1)+"行,")
            self.label_col.setText(str(column+1)+"列")


        except Exception as e:
            print(e)
            pass

    def edit(self):
        id = self.lineEdit_selectedID.text()
        name =self.plainTextEdit_name.toPlainText()
        abbr = self.lineEdit_selectedAbbr.text()
        status = self.comboBox_selectedStatus.currentText()
        tag = self.lineEdit_selectedTag.text()
        info = self.plainTextEdit_info.toPlainText()
        path = self.lineEdit_selectedPath.text()
        self.table.table[id]["name"] = name
        self.table.table[id]["abbr"] = abbr
        self.table.table[id]["status"] = status
        self.table.table[id]["tag"] = tag
        self.table.table[id]["info"] = info
        self.table.table[id]["path"] = path
        self.table.writeJson()
        self.showArrangedTable(self.table.toTable())
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
            self.showArrangedTable(self.table.toTable())
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