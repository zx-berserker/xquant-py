from fastapi import APIRouter
from server.schema import QuoteUpdate, Fail, Success
from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Request
import time
from server.lib.worker import UpdateWorkerTask, ServerWorker
from quant.libs.log import XLog

__all__ = ["router"]

router = APIRouter()

@router.post("/quote")
async def update_quote(data:QuoteUpdate):
    try:
        data_list = data.items
        for item in data_list:
            task = UpdateWorkerTask(**item.to_dic())
            ServerWorker.worker_task_queue.put(task)
    except Exception as e:
        return Fail(str(e))
    return Success()


@router.get("/sse")
async def sse_cron_task_root(request: Request):
    async def cron_task_event_generator(request: Request):
        while True:
            if await request.is_disconnected():
                print("Client disconnected from SSE.")
            message = XLog.fastapi_get(),
            id = str(time.time())
            data = {
                "event": "UpdateEvent", 
                "id": id,
                "data": message,
                "retry": 3000,
            }
            yield data
    
    f = cron_task_event_generator(request)
    return EventSourceResponse(f)


