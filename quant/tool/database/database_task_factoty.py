# -*- encoding:utf-8 -*-
"""
date: 2022/11/20
author: Berserker
"""
from .database_task import BulkUpdateTask, CoreUpdateTask
from quant.libs.multi_thread.xtask import XTaskFactory
from quant.tool.file_writer import FileWriterTaskFactory, FileWriterHandleEnum, FileWriterTask


class BulkUpdateTaskFactory(XTaskFactory):

    def __init__(self, model_cls):
        super(BulkUpdateTaskFactory, self).__init__(BulkUpdateTask)
        self._model_cls = model_cls

    def get_task(self, data):
        if not data:
            return None
        return self.task_cls(self._model_cls, data)

  
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
                 writer_handle_type=FileWriterHandleEnum.WRITER):
        super(CacheFileWriterTaskFactory, self).__init__(FileWriterTask)
        self.flush_count = flush_count
        self.stock_list = stock_list
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
        
    def data_to_string_callback(self, handle=None):
        count = handle.get_count() % self.slice_capacity
        str_data = str(handle.get_data()).replace("'", "\"")
        name_list = handle.get_name().split('-', 2)
        num = int(name_list[0]) - int(name_list[1])
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
            print('flush:' + handle.get_name())
            return True
        return False
    
    def finish_condition_callback(self, handle=None):
        count = handle.get_count()
        name_list = handle.get_name().split('-', 2)
        num = int(name_list[0]) - int(name_list[1])
        if num + 1 < self.slice_capacity and count == num + 1:
            print('finish:' + handle.get_name())
            return True
        if count % self.slice_capacity == 0:
            print('finish:' + handle.get_name())
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
        prefix_name = '%d-%d-' % (self.temp_stock_list[-1].id, self.temp_stock_list[0].id)
        print('%s : %d' % (prefix_name, stock.id))
        return prefix_name
        
    def get_task(self, data, stock, *args, **kwargs):
        return self.writer_factory.get_task(data, stock)
    
    