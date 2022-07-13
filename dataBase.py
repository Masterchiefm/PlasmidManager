#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
#import time
import pandas as pd
from uuid import uuid1 as uid
import time


# In[2]:


class PLASMID:
    def __init__(self):
        """单个对象的基本信息"""
        addTime = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
        self.info = {
            "abbr":"",
            "name":"",
            "status":"",
            "tag":"",
            "info":"",
            "path":"",
            "time":addTime,
            "parent":""
        }        


# In[14]:


class TABLE:
    def __init__(self):
        """表格信息"""
        self.table = {}
        
    def addItem(self,obj):
        id = str(uid())

        plasmid = dict(obj.info)
        self.table.update({id:plasmid})
        
        
    def readJson(self,file):
        with open(file,"r") as json_file:
            try:
                self.table = json.load(json_file)
            except Exception as e:
                print(e)
                
            
    
    def writeJson(self):
        path = "data.json"
        content = json.dumps(self.table)
        with open(path,"w") as json_file:
            try:
                json_file.write(content)
            except Exception as e:
                print(e)
    
    
    def readTable(self,file):
        pass
    
    def writeTable(self,path):
        col = ["abbr","name","status","tag","info","path"]
        sheet = pd.DataFrame(columns=col)
        for id in self.table.keys():
            sheet.loc[id,"abbr"] = self.table[id]["abbr"]
            sheet.loc[id,"name"] = self.table[id]["name"]
            status_code = self.table[id]["status"][0]
            sheet.loc[id,"status"] = self.table[id]["status"]
            sheet.loc[id,"tag"] = self.table[id]["tag"]
            sheet.loc[id,"info"] = self.table[id]["info"]
            sheet.loc[id,"path"] = self.table[id]["path"]
            sheet.loc[id,"time"] = self.table[id]["time"]

        sheet.to_excel(path)

    def toTable(self):
        col = ["abbr","name","status","tag","info","path"]
        sheet = pd.DataFrame(columns=col)
        for id in self.table.keys():
            sheet.loc[id,"abbr"] = self.table[id]["abbr"]
            sheet.loc[id,"name"] = self.table[id]["name"]
            status_code = self.table[id]["status"][0]
            sheet.loc[id,"status"] = self.table[id]["status"]
            sheet.loc[id,"tag"] = self.table[id]["tag"]
            sheet.loc[id,"info"] = self.table[id]["info"]
            sheet.loc[id,"path"] = self.table[id]["path"]
            sheet.loc[id, "time"] = self.table[id]["time"]

        return sheet
    
        






