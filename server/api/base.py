# -*- encoding:utf-8 -*-
"""
date: 2026/10/30
author: Berserker
"""

from server.schema import Fail, Success
from quant.libs.log import XLog
import json

class ApiBase:

    @classmethod
    def api(cls, fn):
        def decorator(*args, **kwargs):
            try:
                data = fn(*args, **kwargs)
                data_js = json.dumps( data)
                return Success(data_js)
            except Exception as e:
                XLog.print(e)
        return decorator