#!/usr/bin/env python
# coding: utf-8

# In[30]:


from uuid import uuid1 as uid
import time
import json
from PyQt5.QtWidgets import QMessageBox, QFileDialog


# In[2]:


class DATA:
    """数据的基本信息"""

    def __init__(self):
        self.time = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
        self.name = 'uname'
        self.type = ''
        self.parent = ''
        self.info = ''


# In[3]:


#####结构#####
# 文件夹
# |---文件夹
#     |---项目
#         |---文件1
#         |---文件2
#
# 文件夹
#

class FILE(DATA):
    """文件信息"""

    def __init__(self, name='uname file'):
        super().__init__()
        self.name = name
        self.type = 'file'
        self.status = ''
        self.tag = ''
        self.path = ''


class FOLDER(DATA):
    """文件夹基本信息"""

    def __init__(self, name='uname folder'):
        super().__init__()
        self.name = name
        self.type = 'folder'


class PROJECT(DATA):
    """项目信息"""

    def __init__(self, name='uname project'):
        super().__init__()
        self.type = 'project'
        self.name = name
        self.status = ''
        self.path = ''
        self.files = []


# In[78]:


class DATABASE():
    def __init__(self):
        self.data = {}

    def addItem(self, item):
        if "id" in item.__dict__.keys():
            id = item.__dict__["id"]
        else:
            id = str(uid())
        self.data[id] = item.__dict__

    def removeItem(self, id):
        self.data.pop(id)

    def refreshData(self):
        for id in self.data:
            # 用于兼容、更新旧数据
            try:
                parent = self.data[id]["parent"]
            except:
                self.data[id]["parent"] = ''

            try:
                type_ = self.data[id]["type"]
            except:
                self.data[id]["type"] = "file"

    def getFolderStructure(self):
        data = self.data
        structure = {"root": []}

        for id in data:
            type_ = data[id]["type"]
            if type_ == "folder":
                structure[id] = []

        for id in data:
            type_ = data[id]["type"]
            if type_ == "folder":
                parent = data[id]["parent"]
                if parent == '':
                    structure["root"].append(id)
                else:
                    structure[parent].append(id)

        return structure

    def getDirTree(self):
        '''生成目录结构'''

        # 列出所有目录
        folder_ids = []
        for id in self.data:
            type_ = self.data[id]['type']
            if type_ == 'folder':
                folder_ids.append(id)

        # 根据一级节点信息生成目录树。
        trees = []
        for id in folder_ids:
            parent_dir = 'root'
            parent = data[id]['parent']
            if parent == '':
                parent = 'root'
            tree = parent + "/" + id
            self.data[id]["tree"] = tree
            trees.append(tree)

        # 列出未归类的文件夹
        unsorted_id = []
        for id in folder_ids:
            current_tree = data[id]["tree"]
            if "root" in current_tree[:5]:
                # 判断是否整理出完整路径
                # print('sorted')
                pass
            else:
                # 不是完整路径，往上补一级。
                unsorted_id.append(id)

        # 循环寻找上一级目录，直到全部补齐

        while len(unsorted_id):
            for id in unsorted_id:
                current_tree = self.data[id]["tree"]
                if "root" in current_tree[:5]:
                    unsorted_id.remove(id)
                else:
                    # 不是完整路径，往上补一级。
                    parent = current_tree.split('/')[0]
                    for i in trees:
                        if parent == i.split('/')[-1]:  # 查到到父节点
                            new_tree = i + current_tree.replace(parent, '')
                            trees.remove(current_tree)
                            trees.append(new_tree)
                            data[id]['tree'] = new_tree
        return trees

    def writeJson(self, path="data.json"):
        path = path
        content = json.dumps(self.data)
        with open(path, "w") as json_file:
            try:
                json_file.write(content)
                print("saved")
            except Exception as e:
                print(e)

    def writeTable(self, path):
        col = [ "name", "status", "info", "path", "time", "parent"]
        import pandas as pd
        sheet = pd.DataFrame(columns=col)
        for id in list(self.data.keys())[::-1]:
            type = self.data[id]["type"]
            if type == "project":
                pass
            else:
                continue
            sheet.loc[id, "name"] = self.data[id]["name"]
            sheet.loc[id, "status"] = self.data[id]["status"]
            sheet.loc[id, "info"] = self.data[id]["info"]
            sheet.loc[id, "path"] = self.data[id]["path"]
            sheet.loc[id, "time"] = self.data[id]["time"]
            sheet.loc[id, "parent"] = self.data[id]["parent"]

        sheet.to_excel(path)



    def toSheet(self):
        col = ["abbr", "name", "status", "tag", "info", "path", "parent"]
        sheet = pd.DataFrame(columns=col)
        for id in self.data.keys():
            sheet.loc[id, "abbr"] = self.data[id]["abbr"]
            sheet.loc[id, "name"] = self.data[id]["name"]
            status_code = self.data[id]["status"][0]
            sheet.loc[id, "status"] = self.data[id]["status"]
            sheet.loc[id, "tag"] = self.data[id]["tag"]
            sheet.loc[id, "info"] = self.data[id]["info"]
            sheet.loc[id, "path"] = self.data[id]["path"]
            sheet.loc[id, "time"] = self.data[id]["time"]
            sheet.loc[id, "partent"] = self.data[id]["parent"]
        return sheet

    def readJson(self, file):
        with open(file, "r") as json_file:
            try:
                self.data = json.load(json_file)
            except Exception as e:
                print(e)

    def changeData(self, id, data_type, new_data):
        new_data = new_data
        if data_type == "parent":
            if new_data == "root":
                new_data = ""

        self.data[id][data_type] = new_data
        self.writeJson()




