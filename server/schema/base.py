# -*- coding:utf-8 -*-
"""
date: 2025/10/28
author: Berserker
"""

from fastapi.responses import JSONResponse
from typing import Optional, Any



class Success(JSONResponse):

    def __init__(self, data:Optional[Any]=None, msg:Optional[str]="OK", **kargs):
        content = {"data":data, "msg":msg}
        content.update(kargs)
        super().__init__(content, 200)




class Fail(JSONResponse):

    def __init__(self, msg:str, code:str = "ff000000", **kargs):
        content = {"code":code, "msg":msg}
        content.update(kargs)
        super().__init__(content, 400)