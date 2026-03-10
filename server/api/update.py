from fastapi import APIRouter
from server.schema import QuoteUpdate, Fail, Success, CookieUpdate
from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Request
import time
from server.lib.worker import UpdateWorkerTask, ServerWorker, UpdateWorkerTask
from quant.libs.log import XLog
from typing import List
from quant.spider.east_money import ProductQuery
import json

__all__ = ["router"]

router = APIRouter()

@router.post("/quote")
async def update_quote(data_list:List[QuoteUpdate]):
    UpdateWorkerTask.update_state = "Update State: Start."
    try:
        for item in data_list:
            task = UpdateWorkerTask(**item.to_dic())
            ServerWorker.worker_task_queue.put(task)
            XLog.info("update task(start_time:%s, end_time:%s, period:%s)." % (item.startTime, item.endTime, item.period))
    except Exception as e:
        return Fail(str(e))
    return Success()



@router.get("/sse")
async def sse_update_quote_root(request: Request):
    async def update_quote_task_event_generator(request: Request):
        is_first = True
        while True:
            if await request.is_disconnected():
                break
            if is_first:
                message = UpdateWorkerTask.update_state
                is_first = False
            else:
                message = XLog.fastapi_get()
            if message:
                id = str(time.time())
                data = {
                    "event": "QuoteUpdateEvent", 
                    "id": id,
                    "data": message,
                    "retry": 3000,
                }
                yield data
    
    f = update_quote_task_event_generator(request)
    return EventSourceResponse(f)



@router.post("/cookie")
async def update_cookie(data: CookieUpdate):
    cookie_data_dic = data.to_dic()
    try:
        with open(ProductQuery.json_temp_cookies_file_path,"r") as file:
            temp_cookies = json.load(file)
        for key in cookie_data_dic.keys():
            if cookie_data_dic[key] and cookie_data_dic[key] != '':
                temp_cookies[key] = cookie_data_dic[key]
        with open(ProductQuery.json_temp_cookies_file_path,"w") as file:
            json.dump(temp_cookies,file)
        
        ProductQuery.read_temp_cookies()
    except Exception as e:
        return Fail(str(e))
    return Success()
