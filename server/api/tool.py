from fastapi import APIRouter, Query
from server.schema import QuoteUpdate, Fail, Success, CookieUpdate
import json
from quant.spider.tdx.tdx_query import TdxQuery, QuotePeriodEnum as TdxQuotePeriodEnum
from quant.libs.enums import QuotePeriodEnum
import os
from pathlib import Path
from quant.libs.log import XLog

__all__ = ["router"]

router = APIRouter()


@router.get('/remove_json')
async def remove_json():   
    XLog.info("remove_json()")
    try:
        directory = Path('/home/xquant/cache/')
        for json_file in directory.glob('*.json'):
            json_file.unlink(missing_ok=True)
        return Success()
    except Exception as e:
        return Fail(str(e))
    

@router.get('/remove_log')
async def remove_log():
    XLog.info("remove_log()")
    try:
        directory = Path('/home/xquant/log/')
        for json_file in directory.glob('*.log'):
            json_file.unlink(missing_ok=True)
        return Success()
    except Exception as e:
        return Fail(str(e))