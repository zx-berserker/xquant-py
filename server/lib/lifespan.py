# -*- coding:utf-8 -*-
"""
date: 2026/01/26
author: Berserker
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from server.lib.worker import ServerWorkerController

@asynccontextmanager
async def lifespan(app: FastAPI):
    ServerWorkerController.start()
    yield
    ServerWorkerController.stop()
    pass

