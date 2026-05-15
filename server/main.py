# -*- coding:utf-8 -*-
"""
date: 2025/10/27
author: Berserker
"""
import sys
import asyncio

# 仅在 Windows 系统下强制切换为 ProactorEventLoop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


from fastapi import FastAPI
from server.api import router
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from server.lib.worker import ServerWorkerController
from config.settings import GlobeConfig
from server.lib.lifespan import lifespan
from server.cron import CronSchedule
from tools import Crons, get_cron_router


GlobeConfig.is_fastapi_server = True
GlobeConfig.is_log_file = True

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

crons = Crons(app) 
CronSchedule.init(crons)
app.include_router(router, prefix="/api/v1")
app.include_router(get_cron_router(), prefix="/api/v1/crons")
