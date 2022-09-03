
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTreeWidgetItem, QAbstractItemView, \
    QListWidgetItem, QDial, QProgressDialog
from PyQt5.QtGui import QIcon, QBrush, QColor, QDrag
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from AlignmentToolGUI import Ui_MainWindow

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

import re
from Bio import pairwise2
from Bio import SeqIO
import pandas as pd
import os
import time
import threading


class BackgroundAlign(QtCore.QThread):
    completed = pyqtSignal(str, str, float)
    def __int__(self):
        QtCore.QThread.__init__(self)
        self.seq_sanger = ""
        self.seq_plasmid = ""
        self.sanger_start = 30
        self.sanger_end = 730
        self.plasmid = ""
        self.sanger = ""

    def run(self) -> None:
        print(self.plasmid + "qidong")
        tool = AlignTool()
        score = float(tool.matchPer(seq_sanger=self.seq_sanger, seq_plasmid=self.seq_plasmid, sanger_start=self.sanger_start, sanger_end=self.sanger_end))
        self.completed.emit(self.plasmid, self.sanger, score)







class AlignTool(QtCore.QThread):
    analysed = pyqtSignal(str, str, float)

    def __init__(self, parent = None, file_list=[]):
        super(AlignTool, self).__init__(parent)
        QtCore.QThread.__init__(self)
        self.seq_sanger = ""
        self.seq_plasmid = ""
        self.sanger_start = 30
        self.sanger_end = 730
        self.plasmid = ""
        self.sanger = ""


    def reverseDNA(self, dna):
        dna = str(dna)
        result = ''
        dna = dna.upper().strip()
        b = ''.join(reversed(dna))
        for i in b:
            if i == "A":
                j = "T"
            elif i == "T":
                j = "A"
            elif i == "C":
                j = "G"
            elif i == "G":
                j = "C"
            else:
                j = "N"

            result = result + j
        return result

    def _openDNAFile(self, file_path):
        with open(file_path, "rb") as f:
            raw_data = f.read()
            data = re.findall("[a|A|t|T|g|G|C|c|N|n]+", str(raw_data))
            for seq in data:
                if len(seq) > 100:
                    dna = str(seq).upper()
                    return dna
        return ""

    def _openSeq(self, file_path):
        if "ab1" in file_path.lower():
            record = SeqIO.read(file_path, "abi")
            seq = str(record.seq)
            return seq

        with open(file_path, "r") as f:
            data = f.readlines()
            for seq in data:
                if ">" in seq:
                    pass
                else:
                    return seq

    def openFile(self, file_path):
        if "dna" in file_path.lower():
            seq = self._openDNAFile(file_path)
        else:
            seq = self._openSeq(file_path)
        return seq

    def matchPer(self, seq_sanger, seq_plasmid, sanger_start=30, sanger_end=730):
        sanger_result = seq_sanger[sanger_start:sanger_end]
        if len(seq_plasmid) < len(seq_sanger):
            if seq_plasmid in seq_sanger:
                return 1.0
            else:
                return 0

        if sanger_result[200:250] in seq_plasmid:
            # print("正")
            pass
        elif self.reverseDNA(sanger_result[200:250]) in seq_plasmid:
            # print("反")
            sanger_result = self.reverseDNA(sanger_result)

        match_region_1 = sanger_result[:15]
        match_region_2 = sanger_result[-15:]
        if match_region_1 in seq_plasmid and match_region_2 in seq_plasmid:
            # print("接头能比对")
            span_1 = int(re.search(match_region_1, seq_plasmid).span()[0])
            span_2 = int(re.search(match_region_2, seq_plasmid).span()[1])

            if span_2 < span_1:
                seq_to_align = seq_plasmid[span_1:] + seq_plasmid[:span_2]
            else:
                seq_to_align = seq_plasmid[span_1:span_2]

            # 计分
            alignment = pairwise2.align.globalms(seq_to_align, sanger_result, 5, -10, -10, -10)
            # print(alignment)
            score = float(alignment[0][2])
            full_score = float(len(sanger_result) * 5)
            ratial = score / full_score
            return score / full_score
        else:
            return 0

    def run(self) -> None:
        print(self.plasmid + "qidong")
        score = self.matchPer(seq_sanger=self.seq_sanger, seq_plasmid=self.seq_plasmid, sanger_start=self.sanger_start, sanger_end=self.sanger_end)
        self.analysed.emit(self.plasmid, self.sanger, score)
        #time.sleep(60)
        print(self.plasmid + "end")








class MyMainWin(QMainWindow, Ui_MainWindow):

    tool = AlignTool()
    def __init__(self, parent=None, plasmids = []):
        """测序批量比对工具"""
        super(MyMainWin, self).__init__(parent)
        self.plasmids = plasmids
        self.setupUi(self)
        self.generateDNAList(plasmids)
        self.result = {}

        self.pushButton_add_DNA.clicked.connect(self.addDNAfile)
        # self.pushButton_add_Sanger.clicked.connect(self.addSanger)
        self.pushButton_align.clicked.connect(self.generateAlignResult)
        self.listWidget_DNA.clicked.connect(self.showResult)

        self.pushButton_clear_Sanger.clicked.connect(self.clearSangerTable)
        self.pushButton_clear_expectation.clicked.connect(self.clearDNATable)
        self.pushButton_clear_DNA_recognition.clicked.connect(self.clearDNAInput)
        self.pushButton_clear_Sanger_recognition.clicked.connect(self.clearSangerInput)

        self.pushButton_add_line_to_expectation.clicked.connect(self.addLine)
        self.pushButton_export_template.clicked.connect(self.exportDNATable)
        self.pushButton_import.clicked.connect(self.importDNATable)
        self.pushButton_export_result.clicked.connect(self.exportResult)

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)






    def updateResult(self,plasmid, sanger, score):
        if plasmid in self.result.keys():
            pass
        else:
            self.result[plasmid] = pd.DataFrame()

        min_score = float(self.lineEdit_score.text())
        if score >= min_score:
            alignment = [sanger, score]
            self.result[plasmid].loc[0, 0 ] = sanger
            self.result[plasmid].loc[0, 1] = score
            self.result[plasmid] = self.result[plasmid].sort_values(by=1, ascending=False)
            #self.result[plasmid]
        #     try:
        #         sorted_result_frame = result_frame.sort_values(by=1, ascending=False)
        #     except Exception as e:
        #         print(e)
        #         print(result_frame)
        #         sorted_result_frame = result_frame
        #     result[plasmid] = sorted_result_frame
        #
        # self.result = result
        # self.listWidget_DNA.addItems(list(result.keys()))


    def exportResult(self):
        table = pd.DataFrame(columns=["样品名", "测序文件", "比对得分"])
        path, type_ = QFileDialog.getSaveFileName(self, "导出结果", "", "excle(*.xlsx)")
        col = 0
        for i in self.result:
            sub_result = self.result[i]
            table.loc[col,"样品名"] = i
            col = col + 1
            for index in sub_result.index:
                file = sub_result.loc[index, 0]
                score = sub_result.loc[index, 1]
                table.loc[col, "测序文件"] = file
                table.loc[col, "比对得分"] = score
                col = col + 1

            col = col + 2

        result = table.fillna(value="")
        try:
            result.to_excel(path)
            QMessageBox.about(self, "Done", "已保存到\n" + path)
        except Exception as e:
            QMessageBox.about(self, "Erro", str(e))







    def importDNATable(self):
        path, type_ = QFileDialog.getOpenFileName(self, "导入", "", "excel(*.xlsx)")
        if path:
            pass
        else:
            return
        table = pd.read_excel(path).fillna(value="")
        #table.fillna(value="")
        print(table.head())
        n = self.tableWidget_DNA.rowCount()
        self.tableWidget_DNA.setRowCount(n + len(table))
        for i in table.index:
            name = table.loc[i, "待比对样品名"]
            path =  table.loc[i, "DNA文件路径"]
            seq_5 = table.loc[i, "5` 附加"]
            seq_original = table.loc[i, "待比对序列"]
            seq_3 = table.loc[i,"3` 附加"]

            self.tableWidget_DNA.setItem(n, 0, QTableWidgetItem(name))
            self.tableWidget_DNA.setItem(n, 1, QTableWidgetItem(path))
            self.tableWidget_DNA.setItem(n, 2, QTableWidgetItem(seq_5))
            self.tableWidget_DNA.setItem(n, 3, QTableWidgetItem(seq_original))
            self.tableWidget_DNA.setItem(n, 4, QTableWidgetItem(seq_3))



    def exportDNATable(self):
        table = pd.DataFrame(columns=["待比对样品名","DNA文件路径","5` 附加","待比对序列","3` 附加"])
        data = self.tableWidget_DNA
        save_path, type_ = QFileDialog.getSaveFileName(self, "导出路径", "", "excel(*.xlsx)")
        if save_path:
            pass
        else:
            return

        for i in range(self.tableWidget_DNA.rowCount()):
            try:
                name = data.item(i,0).text()
            except:
                name = ""
            try:
                path = data.item(i,1).text()
            except:
                path = ""

            try:
                seq_5 = data.item(i,2).text()
            except:
                seq_5 = ""

            try:
                seq_original = data.item(i,3).text()
            except:
                seq_original = ""

            try:
                seq_3 = data.item(i,4).text()
            except:
                seq_3 = ""

            table.loc[i] = [name, path, seq_5, seq_original, seq_3]

        try:
            table.to_excel(save_path)
            QMessageBox.about(self, "完成", "已导出到" + save_path)
        except Exception as e:
            QMessageBox.about(self,"Erro",str(e))
        #print(save_path)



    def addLine(self):
        n = self.tableWidget_DNA.rowCount()
        self.tableWidget_DNA.setRowCount(n + 1)

    def clearDNAInput(self):
        self.plainTextEdit_DNA_file.clear()

    def clearSangerInput(self):
        self.plainTextEdit_Sanger_file.clear()

    def clearDNATable(self):
        self.tableWidget_DNA.clearContents()
        self.tableWidget_DNA.setRowCount(0)

    def clearSangerTable(self):
        self.tableWidget_Sanger.clearContents()
        self.tableWidget_Sanger.setRowCount(0)

    def clearResult(self):
        self.tableWidget_result.clearContents()
        self.tableWidget_result.setRowCount(0)
        self.listWidget_DNA.clear()

    def addDNAfile(self):
        text = (self.plainTextEdit_DNA_file.toPlainText()).replace("\n","")
        plasmids = text.split("file:///")
        plasmids.remove("")
        self.generateDNAList(plasmids)

    # def addSanger(self):
    #     text = (self.plainTextEdit_Sanger_file.toPlainText()).replace("\n", "")
    #     Sangers = text.split("file:///")
    #     Sangers.remove("")
    #     self.generateSangerList(Sangers)

    def generateDNAList(self, plasmids):
        #print(plasmids)
        n = self.tableWidget_DNA.rowCount()
        self.tableWidget_DNA.setRowCount(len(plasmids) + n)
        self.tabWidget_DNA.setCurrentIndex(0)

        for plasmid in plasmids:
            if os.path.isfile(plasmid):
                name = os.path.basename(plasmid)
                path = plasmid
                try:
                    DNA = self.tool.openFile(path)
                except:
                    DNA = ""
            else:
                name = plasmid
                path = ""


            name_item = QTableWidgetItem(name)
            path_item = QTableWidgetItem(path)
            DNA_item = QTableWidgetItem(DNA)
            self.tableWidget_DNA.setItem(n, 0, name_item)
            self.tableWidget_DNA.setItem(n, 1, path_item)
            self.tableWidget_DNA.setItem(n, 3, DNA_item)
            n = n + 1
        self.tableWidget_DNA.resizeColumnToContents(0)

    def generateSangerList(self):
        text = (self.plainTextEdit_Sanger_file.toPlainText()).replace("\n", "")
        Sangers = text.split("file:///")
        Sangers.remove("")


        n = self.tableWidget_Sanger.rowCount()
        self.tableWidget_Sanger.setRowCount(len(Sangers) + n)
        self.tabWidget_DNA.setCurrentIndex(2)

        for Sanger in Sangers:
            name = os.path.basename(Sanger)
            try:
                DNA = self.tool.openFile(Sanger)
            except:
                DNA = ""

            name_item = QTableWidgetItem(name)
            DNA_item = QTableWidgetItem(DNA)
            self.tableWidget_Sanger.setItem(n, 0, name_item)
            self.tableWidget_Sanger.setItem(n,1, DNA_item)

            n = n + 1




    def generateAlignResult(self):
        self.tabWidget_DNA.setCurrentIndex(2)
        t0 = time.time()



        self.generateSangerList()

        self.result = {}
        self.clearResult()

        item = QTableWidgetItem("正在进行比对")
        item.setBackground(QColor(211, 255, 0))
        self.tableWidget_result.setRowCount(1)
        self.tableWidget_result.setItem(0, 0, item)
        self.tableWidget_result.resizeColumnToContents(0)
        self.tabWidget_DNA.setCurrentIndex(2)



        # 读取待测序列
        n = self.tableWidget_DNA.rowCount()
        plasmids = {}
        for n in range(n):
            name = self.tableWidget_DNA.item(n, 0).text()
            try:
                seq_5 = self.tableWidget_DNA.item(n, 2).text()
            except:
                seq_5 = ""
            try:
                seq_origin = self.tableWidget_DNA.item(n, 3).text()
            except:
                seq_origin = ""
            try:
                seq_3 = self.tableWidget_DNA.item(n, 4).text()
            except:
                seq_3 = ""
            seq = seq_5 + seq_origin + seq_3
            if seq == "":
                continue
            else:
                plasmids[name] = seq

        #读取测序结果
        n = self.tableWidget_Sanger.rowCount()
        Sangers = {}

        for i in range(n):
            name = self.tableWidget_Sanger.item(i, 0).text()
            seq = self.tableWidget_Sanger.item(i, 1).text()
            if seq == "":
                continue
            else:
                Sangers[name] = seq

        result = {}
        time_count = len(plasmids) * len(Sangers)



        QMessageBox.about(self, "预计耗时", "预计消耗" + str(time_count) + "秒。点击确认开始")

        for plasmid in plasmids:
            alignment = []
            seq_plasmid = plasmids[plasmid]
            for sanger in Sangers:
                seq_sanger = Sangers[sanger]
                if len(seq_plasmid) < len(seq_sanger):
                    p = seq_sanger
                    s = seq_plasmid
                    seq_plasmid = p
                    seq_sanger = s
                else:
                    pass
                start = int(self.lineEdit_Sanger_start.text())
                end = int(self.lineEdit_Sanger_end.text())
                score = self.tool.matchPer(seq_sanger=seq_sanger, seq_plasmid=seq_plasmid, sanger_start=start, sanger_end=end)
                #self.tool.backgroundAnalyse(seq_sanger=seq_sanger, seq_plasmid=seq_plasmid, sanger_start=start, sanger_end=end)
                #self.tool.start()

                # self.task = BackgroundAlign()
                # self.task.plasmid = plasmid
                # self.task.sanger = sanger
                # self.task.sanger_start = start
                # self.task.sanger_end = end
                # self.task.seq_plasmid = seq_plasmid
                # self.task.seq_sanger = seq_sanger
                # self.task.completed.connect(self.updateResult)
                # self.task.start()
                # print("已经放后台")

                min_score = float(self.lineEdit_score.text())
                if score >= min_score:
                    #print(score)
                    alignment.append([sanger, score])
            result_frame = pd.DataFrame(alignment)
            try:
                sorted_result_frame = result_frame.sort_values(by=1, ascending=False)
            except Exception as e:
                print(e)
                print(result_frame)
                sorted_result_frame = result_frame
            result[plasmid] = sorted_result_frame

        self.result = result
        self.listWidget_DNA.addItems(list(result.keys()))
        t1 = time.time()
        dt = int(t1 - t0)


        item2 = QTableWidgetItem("请分别点击各个样品查看结果")
        item2.setBackground(QColor(0, 255, 0))
        self.tableWidget_result.setRowCount(1)
        self.tableWidget_result.setItem(0, 0,item2)
        self.tableWidget_result.resizeColumnToContents(0)
        self.tabWidget_DNA.setCurrentIndex(2)
        QMessageBox.about(self, "完成", "完成，总共耗时" + str(dt) + "秒\n请分别点击各个样品查看结果")


    def showResult(self):
        self.tabWidget_DNA.setCurrentIndex(2)
        name = self.listWidget_DNA.currentItem().text()
        try:
            sub_result = self.result[name]
        except:
            return

        i = 0
        self.tableWidget_result.setRowCount(len(sub_result))
        for index in sub_result.index:
            seq_file = sub_result.loc[index, 0]
            score = format(float(sub_result.loc[index, 1]), '.3f')
            seq_file_item = QTableWidgetItem(seq_file)
            score_item = QTableWidgetItem(str(score))
            if float(score) == 1.0:
                seq_file_item.setBackground(QColor(0, 255, 0))
            elif 0.9< float(score) < 1.0:
                seq_file_item.setBackground(QColor(255, 255, 0))
            elif 0.8< float(score) < 9:
                seq_file_item.setBackground(QColor(255, 255, 155))
            else:
                seq_file_item.setBackground(QColor(255, 0, 0))
            self.tableWidget_result.setItem(i, 0, seq_file_item)
            self.tableWidget_result.setItem(i, 1, score_item)
            i = i + 1
        self.tableWidget_result.resizeColumnToContents(0)
        self.tableWidget_result.resizeColumnToContents(1)















def win():
    app = QApplication(sys.argv)
    win = MyMainWin()
    win.show()
    sys.exit(app.exec_())







if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyMainWin()
    win.show()
    sys.exit(app.exec_())