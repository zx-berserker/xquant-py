# -*- encoding:utf-8 -*-
"""
date: 2022/11/20
author: Berserker
"""
from .base import SQLAlchemy
from quant.libs.multi_thread.xtask import XTask
import json
import os
from quant.libs.log import XLog


class CacheFileReaderTask(XTask):
     
    def __init__(self, file_name:str):
        super(CacheFileReaderTask, self).__init__()
        self.file_name = file_name

    def task_main(self):
        with open(self.file_name,"r", encoding="utf-8") as file:
            data = json.load(file)
            self.ret_data = data
            return data
        
    def get_meta_data(self):
        return self.file_name
 
    def __repr__(self):
        return "<CacheFileReaderTask id:%d file_name:%s>" % (id(self), self.file_name)


class BulkUpdateTask(XTask):

    def __init__(self, model_cls, data_list):
        super(BulkUpdateTask, self).__init__()
        self.model_cls = model_cls
        self.data_list = data_list

    def task_main(self):
        with SQLAlchemy.session_context() as session:
            session.bulk_insert_mappings(self.model_cls, self.data_list)
            session.commit()
                # session.execute(self.model_cls.__table__.insert(), self.data_list)
                

class CoreUpdateTask(XTask):
    def __init__(self, model_cls, data_list):
        super(CoreUpdateTask, self).__init__()
        self.model_cls = model_cls
        self.data_list = data_list
        
    def task_main(self):
        XLog.info(self.data_list[0])
        with SQLAlchemy.engine_begin() as conn:
            conn.execute(self.model_cls.__table__.insert(), self.data_list)
            
            
# class CacheWriterTask(XTask):
#     def __init__(self, data_lsit):
#         super(CoreUpdateTask, self).__init__()
#         self.data_list = data_lsit
        
#     def task_main(self):
        