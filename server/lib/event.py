# -*- coding:utf-8 -*-
"""
date: 2026/03/16
author: Berserker
"""
from queue import Queue
import time

class EventBase:
    name = "EventBase"

    def __init__(self, data:str):
        self.id = str(time.time())
        self.retry = 3000
        self.data = data

    def to_dic(self):
        return {
            "event": self.name, 
            "id": self.id,
            "data": self.data,
            "retry": self.retry,
        }



class EventQueue:
    # _event_queue = Queue(30)
    _is_running = True
    _is_available = False
    _event_queue_dic:dict[str,Queue] = {}
    _client_count = 0 

    @classmethod
    def set_available(cls, available:bool, id:str):
        if available:
            cls._is_available = available
            cls._client_count += 1
            cls._event_queue_dic[id] = Queue(30)
        else:
            cls._client_count -= 1
            if id in cls._event_queue_dic.keys():
                del cls._event_queue_dic[id]
            if cls._client_count < 1:
                cls._is_available = available

    @classmethod
    def is_available(cls):
        return cls._is_available

    # @classmethod
    # def put_event(cls, event):
    #     if not cls._is_available:
    #         return
    #     for key in cls._event_queue_dic.keys():
    #         while cls._is_running:
    #             try:
    #                 cls._event_queue_dic[key].qsize()
    #             except:
    #                 break
    #             try:
    #                 cls._event_queue_dic[key].put(event, block=False)
    #             except:
    #                 continue
    #             break

    
    @classmethod
    def put_event(cls, event):
        if not cls._is_available:
            return
        for key in cls._event_queue_dic.keys():
            try:
                cls._event_queue_dic[key].put(event, block=False)
            except:
                continue


    @classmethod
    def get_event(cls, id:str) -> dict:
        if not cls._is_available:
            return None        
        while cls._is_running:
            try:
                event:EventBase = cls._event_queue_dic[id].get(block=False)
                return event.to_dic()
            except:
                return None
                
            




class QuoteUpdateEvent(EventBase):
    name = "QuoteUpdateEvent"

    def __init__(self, message):
        super(QuoteUpdateEvent, self).__init__(message)





class QuoteUpdateCookieEvent(EventBase):
    name = "QuoteUpdateCookieEvent"

    def __init__(self):
        super(QuoteUpdateCookieEvent, self).__init__("UpdateCookie")






if __name__ == "__main__":

    event = QuoteUpdateEvent("hello")
    data = event.to_dic()
    print(data)