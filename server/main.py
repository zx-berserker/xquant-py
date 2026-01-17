# -*- coding:utf-8 -*-
"""
date: 2025/10/27
author: Berserker
"""

from fastapi import FastAPI
from server.api import router
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from server.lib.worker import ServerWorker
from config.settings import GlobeConfig

GlobeConfig.is_fastapi_server = True
GlobeConfig.is_log_file = True

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(router, prefix="/api/v1")

server_worker = ServerWorker()
server_worker.start()


# uvicorn main:app --host 0.0.0.0 --port 8080 --reload