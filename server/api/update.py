from fastapi import APIRouter
from server.schema import QuoteUpdate, Fail, Success
from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Request
import time
from server.lib.worker import UpdateWorkerTask, ServerWorker, UpdateWorkerTask
from quant.libs.log import XLog
from typing import List

__all__ = ["router"]

router = APIRouter()

@router.post("/quote")
async def update_quote(data_list:List[QuoteUpdate]):
    UpdateWorkerTask.update_state = "Update State: Start."
    try:
        for item in data_list:
            task = UpdateWorkerTask(**item.to_dic())
            ServerWorker.worker_task_queue.put(task)
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


