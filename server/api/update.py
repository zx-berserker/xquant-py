from fastapi import APIRouter
from server.schema import QuoteUpdate, Fail, Success, CookieUpdate
from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Request
import time
from server.lib.worker import ServerWebWorker
from server.lib.worker_task import StockUpdateWorkerTask, FutureUpdateWorkerTask
from quant.libs.log import XLog
from typing import List
from quant.spider.east_money import ProductQuery
from server.lib.event import EventQueue
import json
from server.lib.worker import ServerWebWorker
from uuid import uuid4

__all__ = ["router"]

router = APIRouter()

@router.post("/exit")
async def update_exit():
    ServerWebWorker.task_exit()

@router.post("/quote")
async def update_quote(data_list:List[QuoteUpdate]):
    StockUpdateWorkerTask.update_state = "StockUpdateWorkerTask State: Start."
    try:
        for item in data_list:
            task = StockUpdateWorkerTask(**item.to_dic())
            ServerWebWorker.put_task(task)
            XLog.info("StockUpdateWorkerTask(start_time:%s, end_time:%s, period:%s)." % (item.startTime, item.endTime, item.period))
    except Exception as e:
        return Fail(str(e))
    return Success()


@router.post("/quote_future")
async def update_quote(data_list:List[QuoteUpdate]):
    FutureUpdateWorkerTask.update_state = "FutureUpdateWorkerTask State: Start."
    try:
        for item in data_list:
            task = FutureUpdateWorkerTask(**item.to_dic())
            ServerWebWorker.put_task(task)
            XLog.info("FutureUpdateWorkerTask(start_time:%s, end_time:%s, period:%s)." % (item.startTime, item.endTime, item.period))
    except Exception as e:
        return Fail(str(e))
    return Success()


@router.get("/sse")
async def sse_update_quote_root(request: Request):
    async def update_quote_task_event_generator(request: Request):
        is_first = True
        id = uuid4().hex
        EventQueue.set_available(True, id)
        while True:
            event = None
            if await request.is_disconnected():
                EventQueue.set_available(False, id)
                print("XQuant Client disconnected from SSE.")
                break
            if is_first:
                message = f'Stock {StockUpdateWorkerTask.update_state} || Future {FutureUpdateWorkerTask.update_state}({FutureUpdateWorkerTask.is_active}) <Task: {ServerWebWorker.get_task_num()}>'
                event_id = str(time.time())
                event = {
                    "event": "QuoteUpdateEvent", 
                    "id": event_id,
                    "data": message,
                    "retry": 3000,
                }
                is_first = False
            else:
                event = EventQueue.get_event(id)
            if event:
                yield event
    
    f = update_quote_task_event_generator(request)
    return EventSourceResponse(f)



@router.post("/cookie")
async def update_cookie(data: CookieUpdate):
    XLog.info("update_cookie(cookieStPsi:%s)." % CookieUpdate.cookieStPsi)
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
