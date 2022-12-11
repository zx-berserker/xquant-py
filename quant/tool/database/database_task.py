# -*- encoding:utf-8 -*-
"""
date: 2022/11/20
author: Berserker
"""
from .base import SQLAlchemy
from quant.libs.multi_thread.xtask import XTask


class BulkUpdateTask(XTask):

    def __init__(self, model_cls, data_list):
        super(BulkUpdateTask, self).__init__()
        self.model_cls = model_cls
        self.data_list = data_list

    def task_main(self):
        print(self.data_list[0])
        with SQLAlchemy.session_context() as session:
            with SQLAlchemy.auto_commit(session):
                session.bulk_insert_mappings(self.model_cls, self.data_list)
                # session.execute(self.model_cls.__table__.insert(), self.data_list)
                

class CoreUpdateTask(XTask):
    def __init__(self, model_cls, data_list):
        super(CoreUpdateTask, self).__init__()
        self.model_cls = model_cls
        self.data_list = data_list
        
    def task_main(self):
        print(self.data_list[0])
        with SQLAlchemy.engine_begin() as conn:
            conn.execute(self.model_cls.__table__.insert(), self.data_list)
            
            
# class CacheWriterTask(XTask):
#     def __init__(self, data_lsit):
#         super(CoreUpdateTask, self).__init__()
#         self.data_list = data_lsit
        
#     def task_main(self):
        