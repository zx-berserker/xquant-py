# -*- encoding:utf-8 -*-
"""
date: 2022/11/20
author: Berserker
"""

import os
from pathlib import Path, PureWindowsPath
from src.libs.multi_thread.xtask import XTask, XTaskFactory
from enum import Enum


class FileWriterHandleEnum(Enum):
    WRITER = 'w+'
    APPEND = 'a+'
    BYTE_WRITER = 'wb+'
    BYTE_APPEND = 'ab+'


class DefaultCallback(object):
    def data_to_string_callback(cls, Handle=None):
        return Handle.get_data()
    
    def flush_condition_callback(cls, Handle=None):
        return True
    
    def finish_condition_callback(cls, Handle=None):
        return True

    def auto_prefix_name_callback(cls, *args, **kwargs):
        return 'default-'
    

class FileWriterHandle(object):
    def __init__(self, file_path, file_name='default-temp', handle_type=FileWriterHandleEnum.WRITER):
        self.path = file_path
        self.name = file_name
        if not self.path:
            self.path = os.getcwd()
        else:
            path = Path(self.path)
            if not path.exists():
                os.makedirs(self.path, 0o755)

        self.type = handle_type
        self.full_name = str(PureWindowsPath(self.path, self.name))
        self.cache_data = ''
        self.writer = open(self.full_name, self.type.value, encoding='utf-8')
        self.temp_data = None
        self.count = 0
        
    def set_condition_callback(self, data_to_string_callback=DefaultCallback.data_to_string_callback,
                               flush_condition_callback=DefaultCallback.flush_condition_callback,
                               finish_condition_callback=DefaultCallback.finish_condition_callback,
                               before_release_callback=None):
        self.data_to_string_callback = data_to_string_callback
        self.flush_condition_callback = flush_condition_callback
        self.finish_condition_callback = finish_condition_callback
        self.before_release_callback = before_release_callback
    
    def write(self, data):
        self.temp_data = data
        self.cache_data += self.data_to_string_callback(self)
        self.count += 1
    
    def get_count(self):
        return self.count
      
    def get_name(self):
        return self.name
        
    def get_data(self):
        return self.temp_data
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.flush_condition_callback(self):
            self.writer.write(self.cache_data)
            self.cache_data = ''
        if self.finish_condition_callback(self):
            if self.cache_data != '':
                self.writer.write(self.cache_data)
                self.writer.close()
            if self.before_release_callback:
                self.before_release_callback(self)


class FileWriterTask(XTask):
    def __init__(self, writer_handle, data):
        super(FileWriterTask, self).__init__()
        self.handle = writer_handle
        self.data = data

    def task_main(self):
        with self.handle as handle:
            handle.write(self.data)


class FileWriterTaskFactory(XTaskFactory):
    def __init__(self, file_path, file_base_name='temp', writer_handle_type=FileWriterHandleEnum.WRITER):
        super(FileWriterTaskFactory, self).__init__(FileWriterTask)
        self.file_path = file_path
        self.file_name = file_base_name
        if not file_path:
            self.path = os.getcwd()
        else:
            path = Path(self.file_path)
            if not path.exists():
                os.makedirs(self.file_path, 0o755)

        self.handle_type = writer_handle_type
        self.handle_dic = {}
        
    def set_callback(self, data_to_string_callback=DefaultCallback.data_to_string_callback,
                     flush_condition_callback=DefaultCallback.finish_condition_callback,
                     finish_condition_callback=DefaultCallback.finish_condition_callback,
                     auto_prefix_name_callback=DefaultCallback.auto_prefix_name_callback):
        self.data_to_string_callback = data_to_string_callback
        self.flush_condition_callback = flush_condition_callback
        self.finish_condition_callback = finish_condition_callback
        self.prefix_name_callback = auto_prefix_name_callback
         
    def before_handle_release_callback(self, handle):
        del self.handle_dic[handle.get_name()]

    def get_task(self, data, *args, **kwargs):
        file_name = '' + self.prefix_name_callback(*args, **kwargs) + self.file_name
        if file_name not in self.handle_dic:
            handle = FileWriterHandle(self.file_path, file_name, self.handle_type)
            handle.set_condition_callback(self.data_to_string_callback,
                                          self.flush_condition_callback,
                                          self.finish_condition_callback,
                                          self.before_handle_release_callback)
            self.handle_dic[file_name] = handle
        return self.task_cls(self.handle_dic[file_name], data)
    
