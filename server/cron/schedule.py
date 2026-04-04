# -*- coding:utf-8 -*-
"""
date: 2025/01/11
author: Berserker
"""
from tools import Crons
from server.lib.worker import ServerWebWorker
from quant.libs.log import XLog
from datetime import datetime
from server.lib.worker_task import FutureUpdateWorkerTask
# from server.lib.cookie import Cookie
__all__ = ["CronSchedule"]


class CronSchedule:

    @classmethod
    def init(cls, crons: Crons):

        @crons.cron("0 0 */1 * *", name="corn_start", tags=["server"])
        async def cron_start():
             now = datetime.now()
             XLog.info("@cron cron_start(%s)" % str(now))

        @crons.cron("*/10 0-6 * * 1-6", name="cron_future_update", tags=["server"])
        async def cron_future_update():
            FutureUpdateWorkerTask.is_active = True
            XLog.info("@cron cron_future_update()")


        @crons.cron("*/10 15-23 * * 1-5", name="cron_future_forbidden_update", tags=["server"])
        async def cron_future_forbidden_update():
            FutureUpdateWorkerTask.is_active = False
            XLog.info("@cron cron_future_forbidden_update()")




