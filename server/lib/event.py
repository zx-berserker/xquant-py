# -*- coding:utf-8 -*-
"""
date: 2026/03/16
author: Berserker
"""
from queue import Queue
import time


class EventQueue:
    _event_queue = Queue(30)
    _is_running = True
    _is_available = False

    @classmethod
    def set_available(cls, available:bool):
        cls._is_available = available

    @classmethod
    def is_available(cls):
        return cls._is_available

    @classmethod
    def put_event(cls, event):
        if not cls._is_available:
            return
        while cls._is_running:
            try:
                cls._event_queue.put(event, timeout=5)
            except:
                continue
            break

    @classmethod
    def get_event(cls):
        if not cls._is_available:
            return None        
        while cls._is_running:
            try:
                event = cls._event_queue.get(block=False)
            except:
                return None
            if event:
                return event.to_dic()
            

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