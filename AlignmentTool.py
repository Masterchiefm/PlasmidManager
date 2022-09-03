
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTreeWidgetItem, QAbstractItemView, QListWidgetItem
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



class AlignTool:
    def __init__(self, file_list=[]):

        pass

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




class MyMainWin(QMainWindow, Ui_MainWindow):

    tool = AlignTool()

    def __init__(self, parent=None, plasmids = []):
        """测序批量比对工具"""
        super(MyMainWin, self).__init__(parent)
        self.setupUi(self)
        self.generateDNAList(plasmids)
        self.result = {}

        self.pushButton_add_DNA.clicked.connect(self.addDNAfile)
        self.pushButton_add_Sanger.clicked.connect(self.addSanger)
        self.pushButton_align.clicked.connect(self.generateAlignResult)
        self.listWidget_DNA.clicked.connect(self.showResult)

        self.pushButton_clear_Sanger.clicked.connect(self.clearSangerTable)
        self.pushButton_clear_expectation.clicked.connect(self.clearDNATable)
        self.pushButton_clear_DNA_recognition.clicked.connect(self.clearDNAInput)
        self.pushButton_clear_Sanger_recognition.clicked.connect(self.clearSangerInput)



    def clearDNAInput(self):
        self.plainTextEdit_DNA_file.clear()

    def clearSangerInput(self):
        self.plainTextEdit_Sanger_file.clear()

    def clearDNATable(self):
        self.tableWidget_DNA.clear()
        self.tableWidget_DNA.setRowCount(0)

    def clearSangerTable(self):
        self.tableWidget_Sanger.clear()
        self.tableWidget_Sanger.setRowCount(0)

    def clearResult(self):
        self.tableWidget_result.clear()
        self.tableWidget_result.setRowCount(0)
        self.listWidget_DNA.clear()

    def addDNAfile(self):
        text = (self.plainTextEdit_DNA_file.toPlainText()).replace("\n","")
        plasmids = text.split("file:///")
        plasmids.remove("")
        self.generateDNAList(plasmids)

    def addSanger(self):
        text = (self.plainTextEdit_Sanger_file.toPlainText()).replace("\n", "")
        Sangers = text.split("file:///")
        Sangers.remove("")
        self.generateSangerList(Sangers)

    def generateDNAList(self, plasmids):
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

    def generateSangerList(self, Sangers):
        n = self.tableWidget_Sanger.rowCount()
        self.tableWidget_Sanger.setRowCount(len(Sangers) + n)
        self.tabWidget_DNA.setCurrentIndex(1)

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

        self.tableWidget_Sanger.resizeColumnToContents(0)


    def generateAlignResult(self):
        self.clearResult()
        self.tabWidget_DNA.setCurrentIndex(2)

        result = {}

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

        # 开始比对
        result = {}
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
                min_score = float(self.lineEdit_score.text())
                if score >= min_score:
                    #print(score)
                    alignment.append([sanger, score])
            result_frame = pd.DataFrame(alignment)
            sorted_result_frame = result_frame.sort_values(by=1, ascending=False)
            result[plasmid] = sorted_result_frame

        self.result = result
        self.listWidget_DNA.addItems(list(result.keys()))


    def showResult(self):
        self.tabWidget_DNA.setCurrentIndex(2)
        name = self.listWidget_DNA.currentItem().text()
        sub_result = self.result[name]
        i = 0
        self.tableWidget_result.setRowCount(len(sub_result))
        for index in sub_result.index:
            seq_file = sub_result.loc[index, 0]
            score = sub_result.loc[index, 1]
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


















if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyMainWin()
    win.show()
    sys.exit(app.exec_())