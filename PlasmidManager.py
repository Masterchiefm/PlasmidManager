# PlasmidManager
# By M.Q. at Shanghai
# 2022.06.29
# dependence：
# PyQt5,qt-tools,requests

# GUI显示相关模块
import time

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTreeWidgetItem, QAbstractItemView
from PyQt5.QtGui import QIcon, QBrush, QColor, QDrag
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from GUI import Ui_MainWindow
import icons_rc

# 系统进程管理相关
from subprocess import getstatusoutput
from requests import get
from json import loads
import os
import sys

# 数据处理相关
import pandas as pd
import dataBase
from shutil import copyfile, rmtree
import AlignmentTool



class MyMainWin(QMainWindow, Ui_MainWindow):

    drop_signal = pyqtSignal()

    def __init__(self, parent=None):
        """质粒管理工具"""
        self.version = "2.0.2"
        self.checkTaskList()  # 进程数量检查，确保只有一个进程运行
        super(MyMainWin, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("项目构建管理-v" + self.version)  # 根据版本号改应用标题

        self.data_base = dataBase.DATABASE()
        try:
            self.data_base.readJson("data.json")
        except:
            self.data_base.writeJson()
            self.data_base.readJson("data.json")

        self.getFolderStructure()

        #文件夹控件属性
        self.treeWidget_folders.dragEnabled()
        self.treeWidget_folders.setDragEnabled(True)
        self.treeWidget_folders.setExpandsOnDoubleClick(False)
        self.tableWidget_projects.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableWidget_projects.setDragEnabled(True)
        self.current_folder_id = "root"
        self.textEdit_recognitionArea2.setStyleSheet("background:gray")
        self.setAcceptDrops(True)

        self.action.triggered.connect(self.checkUpdate)  # 菜单栏
        self.action_2.triggered.connect(self.about)
        self.action_4.triggered.connect(self.donate)




        try:
            with open("note.txt","r+") as f:
                note = f.read()
                print("note is ", note)
                if note == "":
                    self.widget_note.hide()
                else:
                    self.plainTextEdit_note.setPlainText(note)
        except:
            with open("note.txt","w") as f:
                f.write("")
                self.widget_note.hide()


        self.pushButton_ImportTable.clicked.connect(self.importSheet)
        self.treeWidget_folders.clicked.connect(self.currentFolderSelected)
        self.treeWidget_folders.clicked.connect(self.getProjects)
        self.treeWidget_folders.doubleClicked.connect(self.expandFolder)
        self.tableWidget_projects.itemClicked.connect(self.currentProjectSelected)
        self.pushButton_add_folder.clicked.connect(self.addFolder)
        self.pushButton_del_folder.clicked.connect(self.delFolder)
        self.pushButton_clear.clicked.connect(self.clear)
        self.pushButton_clear_2.clicked.connect(self.clear)
        try:
            self.pushButton_add.clicked.connect(self.autoRecognize)  # 添加项目
        except Exception as e:
            QMessageBox.about(self,"Error",str(e))
        self.showAllProjects()
        self.pushButton_WriteTable.clicked.connect(self.saveTable)
        self.pushButton_Open.clicked.connect(self.openFile)
        self.pushButton_openPath.clicked.connect(self.openPath)
        self.pushButton_del.clicked.connect(self.delSeleted)
        self.pushButton_edit.clicked.connect(self.edit)
        self.pushButton_share.clicked.connect(self.share)
        self.pushButton_filter.clicked.connect(self.statusFilter)
        self.pushButton_search.clicked.connect(self.search)
        self.pushButton_saveTable.clicked.connect(self.saveChangedTable)
        self.radioButton_sort.clicked.connect(self.allowSort)
        self.pushButton_note.clicked.connect(self.openNoteFrame)
        self.pushButton_saveNote.clicked.connect(self.saveNote)
        self.pushButton_clearNote.clicked.connect(self.clearNote)
        self.pushButton_copy_file.clicked.connect(self.copyFile2ProgramDir)

        #print(type(self.pushButton_clearNote.clicked))
        #print(type(self.treeWidget_folders.dropped))

        #self.treeWidget_folders.dropped.connect(self.changeParentFolder)
        self.treeWidget_folders.dropped.connect(self.changeParentFolder)



        self.pushButton_align.clicked.connect(self.align)
        #self.subWin = AlignmentTool.MyMainWin()


    def align(self):
        plasmids = []
        self.subWin = AlignmentTool.MyMainWin()
        for item in self.tableWidget_projects.selectedItems():
            row = item.row()
            id = self.tableWidget_projects.item(row, 5).text()
            path = self.tableWidget_projects.item(row, 3).text()
            if os.path.isfile(path):
                if  (".fa" in path.lower()[-4:]) or (".ab1" in path.lower()[-4:]) or (".gb" in path.lower()[-4:]) or (".dna" in path.lower()[-4:]):
                    plasmids.append(path)
        print(plasmids)
        self.subWin.generateDNAList(plasmids)
        self.subWin.show()






    def copyFile2ProgramDir(self):
        id = self.current_project_id
        current_path = os.path.abspath(".")
        data_path = os.path.join(current_path,"data")


        # 创建数据目录
        if os.path.exists(data_path):
            pass
        else:
            os.mkdir(data_path)

        #
        data = self.data_base.data

        type_ = data[id]["type"]
        # 判断是否是文件
        if type_ != "project":
            return

        old_path = data[id]["path"]
        # 判断文件路径是否存在
        try:
            if os.path.isfile(old_path):
                pass
            else:
                return
        except:
                return


            # 判断是否需要复制

            #print(path)
            #print(os.path.isfile(path))

        print("复制文件...")
        file_name = old_path.split("/")[-1]
        parent_path = os.path.join(data_path,id)
        print(os.path.exists(parent_path))
        if os.path.exists(parent_path):
            pass
        else:
            print(str(parent_path))
            os.mkdir(str(parent_path))

        default_path = os.path.join(parent_path, file_name)
        path, fileType = QFileDialog.getSaveFileName(self,"保存jk路径", default_path,"")
        if path:
            new_path = os.path.abspath(path)
            if new_path != default_path:
                rmtree(parent_path)

            copyfile(old_path, new_path)
            data[id]["path"] = new_path
            self.data_base.writeJson()
            self.getProjects()
        else:
            rmtree(parent_path)





    def changeParentFolder(self, drag_ids, drop_to_item_id):


        # 判断托到的是不是根文件夹
        if drop_to_item_id == "root":
            drop_to_item_tree = "root"
            drop_to_item_id = ""
        else:
            drop_to_item_tree = self.data_base.getDirTree(drop_to_item_id)

        for drag_id in drag_ids:
            drag_item_tree = self.data_base.getDirTree(drag_id)

            #判断托的是不是根或者未分类文件夹
            if drag_id == "root":
                pass
            elif drag_id == "unsorted":
                pass

            # 判断拖动的类型
            drag_type = self.data_base.data[drag_id]["type"]

            # 拖的是文件夹，且拖到空白处：
            if drag_type == "folder" and drop_to_item_id == "unsorted":
                drop_to_item_id = ""
                self.data_base.changeTmpData(drag_id, "parent", drop_to_item_id)
                self.getFolderStructure()
                self.getProjects()
                continue


            # 拖的是文件
            if drag_type == "project":
                self.data_base.changeTmpData(drag_id, "parent", drop_to_item_id)
                self.getFolderStructure()
                self.getProjects()
                continue

            # 拖子文件夹进进父文件夹
            elif (drag_type == "folder") and (not(drag_item_tree in drop_to_item_tree)):
                self.data_base.changeTmpData(drag_id, "parent", drop_to_item_id)
                self.getFolderStructure()
                self.getProjects()
                continue

            # 拖父文件夹进子文件
            elif (drag_item_tree in drop_to_item_tree):
                self.getFolderStructure()
                self.getProjects()
                continue
        self.data_base.writeJson()








    def expandFolder(self):
        self.treeWidget_folders.expandItem(self.treeWidget_folders.currentItem())

    def openNoteFrame(self):
        if self.widget_note.isHidden():
            try:
                with open("note.txt",'r') as f:
                    note = f.read()
                    #print(note)
                    self.plainTextEdit_note.setPlainText(note)
            except:
                pass
            self.widget_note.show()
            self.pushButton_note.setText("关闭备忘录")
        else:
            self.pushButton_note.setText("备忘录")
            self.widget_note.hide()

    def clearNote(self):
        self.plainTextEdit_note.clear()
        with open("note.txt", 'w') as f:
            f.write("")

    def saveNote(self):
        note = self.plainTextEdit_note.toPlainText()
        try:
            with open("note.txt",'w') as f:
                f.write(note)
                QMessageBox.about(self,"成功","已保存")
        except Exception as e:
            QMessageBox.about(self,"ERR",str(e))



    def allowSort(self):
        """pqQT表格不能在允许排序的时候进行修改！"""
        if self.radioButton_sort.isChecked():
            self.tableWidget_projects.setSortingEnabled(True)
        else:
            self.tableWidget_projects.setSortingEnabled(False)

    def saveChangedTable(self):
        self.tableWidget_projects.setSortingEnabled(False)
        rows = self.tableWidget_projects.rowCount()
        for i in range(rows):
            id = self.tableWidget_projects.item(i, 5).text()
            name = self.tableWidget_projects.item(i, 0).text()
            status = self.tableWidget_projects.item(i, 1).text()
            info = self.tableWidget_projects.item(i, 2).text()
            path = self.tableWidget_projects.item(i, 3).text()
            time_ = self.tableWidget_projects.item(i, 4).text()
            self.data_base.data[id]["name"] = name
            self.data_base.data[id]["status"] = status
            self.data_base.data[id]["info"] = info
            self.data_base.data[id]["path"] = path
            self.data_base.data[id]["time"] = time_

        self.data_base.writeJson()
        QMessageBox.about(self, "成功", "已保存")

    def statusFilter(self):
        text = self.comboBox_status.currentText()
        #print(text)
        if text == "":
            return 0
        elif text == "显示全部":
            self.showAllProjects()
            return 0

        data = self.data_base.data
        text = text.lower()
        arranged_ids = []
        for id in self.current_project_ids:
            if data[id]["status"] in text:
                arranged_ids.append(id)

        arranged_ids.reverse()
        self.current_project_ids = arranged_ids
        self.showArrangedProject(self.current_project_ids)

    def search(self):
        text = self.lineEdit_search.text()
        text = text.replace("，",",")
        key_text = text.split(",")
        option = self.comboBox_search.currentText()
        data = self.data_base.data
        arranged_ids = []
        # print(text)

        for id in self.current_project_ids:
            name = data[id]["name"]
            status = data[id]["status"]
            info = data[id]["info"]
            path = data[id]["path"]
            time_ = data[id]["time"]

            if option == "全局":
                combinedInfo = ( name  + info + status + path + time_).lower()
            elif option == "名称":
                combinedInfo = name.lower()

            elif option == "备注":
                combinedInfo = info.lower()

            elif option == "时间":
                combinedInfo = time_.lower

            else:
                combinedInfo = ( name + status + info + path).lower()

            key_count = len(key_text)
            score = 0
            for text in key_text:
                if text in combinedInfo:
                    score = score + 1

            if score == key_count:
                arranged_ids.append(id)

        self.showArrangedProject(arranged_ids)




    def importSheet(self):
        try:
            path, fileType = QFileDialog.getOpenFileName(self,"path","","excel(*.xlsx)")
            #print(path)
            sheet = pd.read_excel(path,index_col=0)
        except Exception as e:
            with open("crash_log.txt","a") as f:
                crash_time = str(time.ctime()) + "--import sheet crashed \n"
                f.write(crash_time + str(e))
            return 0


        for i in sheet.index:
            project = dataBase.PROJECT()
            name = sheet.loc[i,"name"]
            status = sheet.loc[i, "status"]
            info = sheet.loc[i,"info"]
            path = sheet.loc[i,"path"]
            add_time = sheet.loc[i,"time"]
            parent = str(self.current_folder_id)
            project.path = str(path)
            project.info = str(info)
            project.path = str(path)
            project.name = str(name)
            project.status = str(status)
            project.time = str(add_time)
            project.parent = parent




            #print(type(project))
            self.data_base.addItem(project)


        self.getProjects()
        self.data_base.writeJson()

        #except Exception as e:
        #    QMessageBox.about(self,"错误","不支持该表格形式，请确保表格内有对应列" + str(e))

    def saveTable(self):
        path,fileType= QFileDialog.getSaveFileName(self,"path","","excel(*.xlsx)")
        if path:
            self.data_base.writeTable(path)
            QMessageBox.about(self,"完成","已导出到" + str(path))

    def share(self):
        items = self.tableWidget_projects.selectedItems()
        newSheet = pd.DataFrame(columns = [ "name", "status", "info", "path", "time"])
        # print(newSheet)
        selectedRows = []
        for i in items:
            row = i.row()
            id = self.tableWidget_projects.item(row, 5).text()
            newSheet.loc[id, 'name'] = self.tableWidget_projects.item(row, 0).text()
            newSheet.loc[id, 'status'] = self.tableWidget_projects.item(row, 1).text()
            newSheet.loc[id, 'info'] = self.tableWidget_projects.item(row, 2).text()
            newSheet.loc[id, 'path'] = self.tableWidget_projects.item(row, 3).text()
            newSheet.loc[id, 'time'] = self.tableWidget_projects.item(row, 4).text()

        try:
            path, fileType = QFileDialog.getSaveFileName(self, "path", "", "excel(*.xlsx)")
            if path:
                newSheet.to_excel(path)
        except:
            pass

    def openFile(self):
        try:
            index = self.tableWidget_projects.selectionModel().currentIndex()
            row = index.row()
            path = self.tableWidget_projects.item(row, 3).text()
            if path == "":
                QMessageBox.about(self, "找不到文件", "路径未设置，请修改路径")
            else:
                os.startfile(path)
        except Exception as e:
            QMessageBox.about(self, "找不到文件", str(e) + "\n 请再次确认并修改文件路径!")


    def openPath(self):
        try:
            index = self.tableWidget_projects.selectionModel().currentIndex()
            row = index.row()
            filePath = self.tableWidget_projects.item(row, 3).text()
            if filePath == "":
                QMessageBox.about(self, "找不到目录", "路径未设置，请修改路径")
            else:
                parentPath = os.path.dirname(filePath)
                os.startfile(parentPath)
        except Exception as e:
            QMessageBox.about(self, "找不到目录", str(e) + "\n 请再次确认并修改文件路径!")

    def delSeleted(self):
        selection = self.tableWidget_projects.selectedIndexes()
        for item in selection:
            try:
                row = item.row()
                id = self.tableWidget_projects.item(row, 5).text()
                self.data_base.data.pop(id)
                path = self.tableWidget_projects.item(row, 3).text()
                if id in path:

                    folder = os.path.join( str(os.path.abspath(".")), "data/" + id)
                    print(folder)
                    print("删除"+ folder)
                    rmtree(folder)
            except Exception as e:
                print(e)
            #pass
        self.data_base.writeJson()
        self.getProjects()

    def edit(self):
        id = self.lineEdit_selectedID.text()
        name = self.plainTextEdit_selectedName.toPlainText()
        status = self.comboBox_selectedStatus.currentText()
        info = self.plainTextEdit_selectedInfo.toPlainText()
        path = self.lineEdit_selectedPath.text()
        file = self.textEdit_recognitionArea2.toPlainText()
        if "file" in file:
            path = file.replace("file:///", "")
            self.lineEdit_selectedPath.setText(path)

        try:
            self.data_base.data[id]["name"] = name
        except:
            QMessageBox.about(self,"Erro","请选中文件再修改")
            return 0
        self.data_base.data[id]["status"] = status
        self.data_base.data[id]["info"] = info
        self.data_base.data[id]["path"] = path
        self.data_base.writeJson()
        self.current_project_ids.reverse()
        self.showArrangedProject(self.current_project_ids)
        QMessageBox.about(self, "修改", "完成！")
        self.clear()


    def addFile2DataBase(self,file_path):
        path = file_path
        name = path.split("/")[-1]
        project = dataBase.PROJECT()
        project.name = name
        project.path = path
        project.info = self.plainTextEdit_info.toPlainText()
        project.status = self.comboBox.currentText()
        if self.current_folder_id == "root":
            project.parent = ""
        else:
            project.parent = self.current_folder_id
        self.data_base.addItem(project)
        self.data_base.writeJson()




    def autoRecognize(self):
        text = self.textEdit_recognitionArea.toPlainText()
        files = []
        if text == "":
            name = self.plainTextEdit_name.toPlainText()
            if name != "":
                name = "/" + str(name).strip()
                files.append(name)
            else:
                print("空")
                return 0



        items = text.split("file:///")
        for i in items:
            path = i.replace("\n","")
            if os.path.isfile(path):
                files.append(path)

            elif path == "":
                continue
            elif os.path.isdir(path):
                print("path is ", path)
                sub_files = os.listdir(path)

                parentPath = path
                if "/" in parentPath[-1]:
                    pass
                else:
                    parentPath = parentPath + "/"

                for f in sub_files:
                    path = parentPath + f
                    files.append(path)
            else:
                QMessageBox.about(self,"Error","文件(夹)\n" + path + "\n不存在/无法访问")

        for path in files:
            self.addFile2DataBase(path)

        self.data_base.writeJson()
        self.getProjects()
        self.clear()


    def clear(self):
        self.lineEdit_tag.clear()
        self.lineEdit_path.clear()
        self.plainTextEdit_name.clear()
        self.plainTextEdit_info.clear()
        self.textEdit_recognitionArea.clear()
        self.textEdit_recognitionArea2.clear()
        self.plainTextEdit_selectedInfo.clear()
        self.plainTextEdit_selectedName.clear()
        self.lineEdit_selectedPath.clear()

    def delFolder(self):
        try:
            folder_id = self.current_folder_id
            name = self.current_folder_name
        except:
            QMessageBox.about(self, "Error", "先选中要删除的文件夹")
            return 0

        if folder_id == "root":
            folder_id = ""

        data = self.data_base.data
        for id in data:
            parent = data[id]["parent"]
            if parent == folder_id:
                QMessageBox.about(self, "Error", "文件夹非空！无法删除")
                return 0

        ok = QMessageBox.question(self,"确认删除",name + " 将被删除")
        if ok == QMessageBox.Yes:
            try:
                self.data_base.removeItem(folder_id)
                self.data_base.writeJson()
                currentItem = self.treeWidget_folders.currentItem()
                parentItem = currentItem.parent()
                parentItem.removeChild(currentItem)
                self.treeWidget_folders.clearSelection()
            except Exception as e:
                print(e)
                QMessageBox.about(self,"Error","文件夹不存在\n" + str(e))



    def addFolder(self):
        try:
            parent_folder = self.current_folder_name
            parent_id = self.current_folder_id
        except:
            parent_folder = "所有文件"
            parent_id = ""

        msg = "在 " + parent_folder + " 目录下创建以下文件夹："
        name, ok = QInputDialog.getText(self,"New Folder",msg)

        if name and ok:
            folder = dataBase.FOLDER()
            folder.name = name
            folder.parent = parent_id
        else:
            return 0

        self.data_base.addItem(folder)
        self.data_base.writeJson()
        self.getFolderStructure()


    def currentProjectSelected(self):
        self.tableWidget_projects.setSortingEnabled(False)
        self.radioButton_sort.setChecked(False)
        self.tabWidget.setCurrentIndex(1)
        index = self.tableWidget_projects.currentIndex()
        col = index.column()
        row = index.row()
        self.current_project_col = col
        self.current_project_row =row
        self.current_project_id = self.tableWidget_projects.item(row, 5).text()
        name = self.tableWidget_projects.item(row, 0).text()
        status = self.tableWidget_projects.item(row, 1).text()
        info = self.tableWidget_projects.item(row, 2).text()
        path = self.tableWidget_projects.item(row, 3).text()
        self.lineEdit_selectedID.setText(self.current_project_id)
        self.plainTextEdit_selectedName.setPlainText(name)
        self.plainTextEdit_selectedInfo.setPlainText(info)
        self.comboBox_selectedStatus.setCurrentText(status)
        self.lineEdit_selectedPath.setText(path)

    def currentFolderSelected(self):
        self.tableWidget_projects.setSortingEnabled(False)
        self.radioButton_sort.setChecked(False)
        folder = self.treeWidget_folders.currentItem()
        id = folder.whatsThis(0)
        name = folder.text(0)
        # self.label_seleted_name.setText(name)
        self.current_folder_id= id
        self.current_folder_name = name


    def getFolderStructure(self):
        # 设置根节点
        root = QTreeWidgetItem()
        root.setText(0, '所有文件')
        root.setWhatsThis(0,"root")
        root.setIcon(0,QIcon("ico.png"))
        # root.setIcon(0, icons_rc.qt_resource_data)

        unsorted = QTreeWidgetItem()
        unsorted.setText(0,"未分类")
        unsorted.setWhatsThis(0, "unsorted")
        unsorted.setIcon(0,QIcon("ico.png"))

        self.treeWidget_folders.clear()

        self.treeWidget_folders.addTopLevelItem(root)
        self.treeWidget_folders.addTopLevelItem(unsorted)

        for id in self.data_base.data:
            try:
                parent = self.data_base.data[id]["parent"]
            except:
                parent = ""
                self.data_base.data[id]["parent"] = ""

            name = self.data_base.data[id]["name"]
            try:
                type_ = self.data_base.data[id]["type"]
            except:
                type_ = "project"
                self.data_base.data[id]["type"] = type_
                self.data_base.writeJson()


            if type_ == "folder":
                locals()[id] = QTreeWidgetItem()
                locals()[id].setText(0, name)
                locals()[id].setWhatsThis(0, id)



        for id in self.data_base.data:
            parent = self.data_base.data[id]["parent"]
            name = self.data_base.data[id]["name"]
            type_ = self.data_base.data[id]["type"]
            if type_ == "folder":
                if parent == "":
                    root.addChild(locals()[id])
                    unsorted.addChild(locals()[id])
                else:
                    locals()[parent].addChild(locals()[id])

        self.treeWidget_folders.expandToDepth(1)
        self.treeWidget_folders.resizeColumnToContents(0)

    def getProjects(self):
        data = self.data_base.data
        self.current_project_ids = []
        for id in data:
            project = data[id]
            parent = project["parent"]
            type_ = project["type"]
            if parent == "":
                parent = "root"

            if (parent == self.current_folder_id) and (type_ == "project"):
                self.current_project_ids.append(id)
            elif (self.current_folder_id == "root") and (type_ == "project"):
                self.current_project_ids.append(id)
            elif (self.current_folder_id == "unsorted") and (parent == "root") and (type_ == "project"):
                self.current_project_ids.append(id)




        self.showArrangedProject(self.current_project_ids)


    def showAllProjects(self):
        all_project_ids = []
        data = self.data_base.data
        for id in data:
            type_ = data[id]["type"]
            if type_ == "project":
                all_project_ids.append(id)
        self.current_project_ids = all_project_ids
        self.showArrangedProject(self.current_project_ids)

    def showArrangedProject(self,project_list):
        #project_list.reverse()
        data = self.data_base.data
        self.tableWidget_projects.setSortingEnabled(False)
        arranged_project_ids = project_list
        self.tableWidget_projects.clearContents()
        arranged_project_ids.reverse()
        self.tableWidget_projects.setRowCount(len(arranged_project_ids))


        row = 0
        for id in arranged_project_ids:
            project = data[id]
            name = project["name"]
            try:
                info = project["info"]
            except:
                info = ""
                self.data_base.data[id]["info"] = ""
                self.data_base.writeJson()

            status = project["status"]
            add_time = project["time"]
            path = project["path"]

            name_item = QTableWidgetItem(name)
            name_item.setWhatsThis(id)
            status_item = QTableWidgetItem(status)
            status_item.setWhatsThis(id)
            info_item = QTableWidgetItem(info)
            info_item.setWhatsThis(id)
            path_item = QTableWidgetItem(path)
            path_item.setWhatsThis(id)
            time_item = QTableWidgetItem(add_time)
            time_item.setWhatsThis(id)
            id_item = QTableWidgetItem(id)
            id_item.setWhatsThis(id)


            if "完成" in status:
                status_item.setBackground(QColor(255,255,255))
            elif "未" in status:
                status_item.setBackground(QColor(0,255,0))
            elif "正在" in status:
                status_item.setBackground(QColor(200,200,230))
            elif "败" in status:
                status_item.setBackground(QColor(240,200,200))
            elif "突变" in status:
                status_item.setBackground(QColor(230,150,140))
            else:
                status_item.setBackground(QColor(200,200,0))

            if os.path.exists(path):
                if name in path:
                    pass
                else:
                    name_item.setForeground(QColor(0,0,230))
            else:
                name_item.setForeground(QColor(255,0,0))
                path_item.setForeground(QColor(255,0,0))
            self.tableWidget_projects.setItem(row,0,name_item)
            self.tableWidget_projects.setItem(row,1,status_item)
            self.tableWidget_projects.setItem(row,2,info_item)
            self.tableWidget_projects.setItem(row,3,path_item)
            self.tableWidget_projects.setItem(row,4,time_item)
            self.tableWidget_projects.setItem(row,5,id_item)
            row = row + 1


        self.tableWidget_projects.resizeColumnToContents(0)
        self.tableWidget_projects.resizeColumnToContents(1)
        self.tableWidget_projects.resizeColumnToContents(2)



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

import AlignmentTool






if __name__ == "__main__":

    app = QApplication(sys.argv)
    win = MyMainWin()
    subWin = AlignmentTool.MyMainWin()
    win.show()
    sys.exit(app.exec_())
