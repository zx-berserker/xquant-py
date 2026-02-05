# -*- encoding:utf-8 -*-
"""
date: 2022/11/20
author: Berserker
"""
from .database_task import BulkUpdateTask, CoreUpdateTask, CacheFileReaderTask
from quant.libs.multi_thread.xtask import XTaskFactory
from quant.tool.file_writer import FileWriterTaskFactory, FileWriterHandleEnum, FileWriterTask
from quant.libs.error import XException
from quant.libs.enums import ErrorCodeEnum
import json
import os
from quant.libs.log import XLog


class CacheFileReaderTaskFactory(XTaskFactory):
    def __init__(self, dir_path:str):
        super(CacheFileReaderTaskFactory, self).__init__(CacheFileReaderTask)
        self.dir_path = dir_path
        self._exception = None

    def get_task(self, file_name):
        self.except_watch()
        file_name = os.path.join(self.dir_path, file_name)
        task:CacheFileReaderTask = self.task_cls(file_name)
        task.add_except_callback(self.task_except_callback)
        return task

    def env_prepare(self):
        pass

    def task_except_callback(self, exception):
        self._exception = exception

    def except_watch(self):
        if self._exception:
            raise self._exception


class BulkUpdateTaskFactory(XTaskFactory):

    def __init__(self, model_cls):
        super(BulkUpdateTaskFactory, self).__init__(BulkUpdateTask)
        self._model_cls = model_cls

    def get_task(self, data, *args, **kwargs):
        self.except_watch()
        if data is None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID,"param data is invalid!")
        task:BulkUpdateTask = self.task_cls(self._model_cls, data)
        task.add_except_callback(self.task_except_callback)
        task.add_done_callback(lambda:XLog.info(*args, **kwargs))
        return task
    
    def task_except_callback(self, exception):
        self._exception = exception

    def except_watch(self):
        if self._exception:
            raise self._exception

  
class CoerUpdateTaskFactory(XTaskFactory):

    def __init__(self, model_cls):
        super(CoerUpdateTaskFactory, self).__init__(CoreUpdateTask)
        self._model_cls = model_cls

    def get_task(self, data, *args, **kwargs):
        if not data:
            return None
        return self.task_cls(self._model_cls, data)


class CacheFileWriterTaskFactory(XTaskFactory):
    def __init__(self, file_path, file_base_name='temp', stock_list=None, flush_count=10, slice_capacity=100, 
                 writer_handle_type=FileWriterHandleEnum.WRITER, file_prefix_base_name:str=""):
        super(CacheFileWriterTaskFactory, self).__init__(FileWriterTask)
        self.flush_count = flush_count
        self.stock_list = stock_list
        self.file_prefix_base_name = file_prefix_base_name
        self.writer_factory = FileWriterTaskFactory(file_path, file_base_name, writer_handle_type)
        self.writer_factory.set_callback(self.data_to_string_callback, self.flush_condition_callback,
                                         self.finish_condition_callback, self.auto_prefix_name_callback)
        self.slice_capacity = slice_capacity
        list_len = len(self.stock_list)
        if list_len < self.slice_capacity:
            self.temp_stock_list = self.stock_list
        else:
            self.temp_stock_list = self.stock_list[:self.slice_capacity]
        self.slice_count = 0
        self.first_empty = False
        
    def data_to_string_callback(self, handle=None, data=None):
        if handle==None or data == None:
            raise XException(ErrorCodeEnum.CODE_PARAMETER_INVALID,"param is None!")
        count = handle.get_count() % self.slice_capacity
        str_data = str(data).replace("'", "\"")
        # name_list = handle.get_name().split('-', 2)
        # num = int(name_list[0]) - int(name_list[1])
        num = len(self.temp_stock_list) - 1
        if num != 0:          
            if self.first_empty == True:
                temp_str = str_data[1:]
            else:
                temp_str = ',' + str_data[1:]
                
            if count == 0:
                if str_data == '[]':
                    self.first_empty = True
                return str_data[:-1]
            elif count == num:
                if str_data == '[]':
                    return ']'
                return temp_str
            else:
                if str_data == '[]':
                    return ''
                if self.first_empty:
                    self.first_empty = False
                return temp_str[:-1]
        return str_data
    
    def flush_condition_callback(self, handle=None):
        count = handle.get_count()
        if count % self.flush_count == 0:
            XLog.info('flush:' + handle.get_name())
            return True
        return False
    
    def finish_condition_callback(self, handle=None):
        count = handle.get_count()
        # name_list = handle.get_name().split('-', 2)
        # num = int(name_list[0]) - int(name_list[1])
        # if num + 1 < self.slice_capacity and count == num + 1:
        num = len(self.temp_stock_list)
        if num < self.slice_capacity and count == num:
            XLog.info('finish:' + handle.get_name())
            return True
        if count % self.slice_capacity == 0:
            XLog.info('finish:' + handle.get_name())
            return True
        return False

    def auto_prefix_name_callback(self, stock):
        if stock not in self.temp_stock_list:
            self.slice_count += 1
            begin = self.slice_count * self.slice_capacity
            end = begin + self.slice_capacity
            if end > len(self.stock_list):
                end = None
            self.temp_stock_list = self.stock_list[begin:end]
        prefix_name = '%s%s(%d)_%s(%d)-' % (self.file_prefix_base_name, self.temp_stock_list[-1].scode, self.temp_stock_list[-1].id, self.temp_stock_list[0].scode, self.temp_stock_list[0].id)
        XLog.info('%s : %s(%d)' % (prefix_name, stock.scode,stock.id))
        return prefix_name
        
    def get_task(self, data, stock, *args, **kwargs):
        return self.writer_factory.get_task(data, stock)
    

    def env_release(self):
        self.writer_factory.env_release()
    