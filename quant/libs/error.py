# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

class XException(Exception):

    def __init__(self, error_code=None, description=None, name="SystemException"):
        if error_code:
            self.error_code = error_code.value
        if description:
            self.description = description
        self.name = name
        super(XException, self).__init__()

    def get_error_code(self):
        return self.error_code

    def __str__(self):
        error_code = self.error_code if self.error_code is not None else "???"
        return "%s %s: %s" % (error_code, self.name, self.description)

    def __repr__(self):
        error_code = self.error_code if self.error_code is not None else "???"
        return "<%s '%s: %s'>" % (self.__class__.__name__, error_code, self.name)
