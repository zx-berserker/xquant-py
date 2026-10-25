from fastapi import APIRouter, Query, File, UploadFile, HTTPException, status
from server.schema import QuoteUpdate, Fail, Success, CookieUpdate
import json
from quant.spider.tdx.tdx_query import TdxQuery, QuotePeriodEnum as TdxQuotePeriodEnum
from quant.libs.enums import QuotePeriodEnum
import os, httpx
from pathlib import Path
from quant.libs.log import XLog
from quant.spider.tdx.tdx_query import TdxQuery
from fastapi.responses import FileResponse
from config.secure import CACHE_FILE_PATH

__all__ = ["router"]

router = APIRouter()



@router.get('/json/list')
async def list_json():
    file_list = []
    file_name_list = os.listdir(CACHE_FILE_PATH)
    for name in file_name_list:
        name_list = name.split(".")
        if "json" in name_list:
            file_list.append(name)
    data_js = json.dumps(file_list)
    return Success(data_js)

@router.get('/json/download')
async def download_json(
    name:str = Query('', description="json file name"),
):
    file_path = os.path.join(CACHE_FILE_PATH, name)
    p = Path(file_path)
    if not p.is_file(): 
        raise HTTPException(404)
    return FileResponse(p, filename=p.name)


@router.get('/json/remove')
async def remove_json():   
    XLog.info("remove_json()")
    try:
        directory = Path('/home/xquant/cache/')
        for json_file in directory.glob('*.json'):
            json_file.unlink(missing_ok=True)
        return Success()
    except Exception as e:
        return Fail(str(e))
    

@router.get('/log/remove')
async def remove_log():
    XLog.info("remove_log()")
    try:
        directory = Path('/home/xquant/log/')
        for json_file in directory.glob('*.log'):
            json_file.unlink(missing_ok=True)
        return Success()
    except Exception as e:
        return Fail(str(e))



@router.get('/tdx/reconnect')
async def tdx_reconnect():
    try:
        TdxQuery.disconnect()
        return Success()
    except Exception as e:
        return Fail(str(e))

