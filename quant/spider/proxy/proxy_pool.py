# -*- coding:utf-8 -*-
"""
date: 2026/02/06
author: Berserker
"""
from quant.libs.multi_thread import XThread
from .proxy import Proxy
from queue import Queue, Empty
from config import root_dir
import json
import os

class ProxyPool(XThread):

    def __init__(self, maxsize=50):
        super(ProxyPool, self).__init__("ProxyPool")
        self.proxy_queue = Queue(maxsize)
        self.is_stop = False

    def get_proxy(self):
        proxy = self.proxy_queue.get()
        return proxy
    
    def stop(self):
        self.is_stop = True

    def thread_main(self):
        try:
            json_file_path = os.path.join(root_dir, "config", "proxy_list.json")
            with open(json_file_path,"r") as file:
                data_list = json.load(file)
                for data in data_list:
                    proxy_str = data["proxy"]
                    self.proxy_queue.put(proxy_str, block=False)
        except:
            pass
        while True:
            proxy_list = Proxy.get_proxy(use_json_file=False)
            for proxy in proxy_list:
                while True:
                    try:
                        self.proxy_queue.put(proxy, timeout=5)
                    except:
                        if self.is_stop:
                            return
                        continue
                    break
