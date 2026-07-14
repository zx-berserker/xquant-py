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
from quant.spider.tdx import TdxQuery
import pytz
# from server.lib.cookie import Cookie
__all__ = ["CronSchedule"]

shanghai_tz = pytz.timezone('Asia/Shanghai')

class CronSchedule:

    @classmethod
    def init(cls, crons: Crons):

        @crons.cron("*/2 * * * *", name="corn_start", tags=["server"])
        async def cron_start():
             now = datetime.now(shanghai_tz)
             XLog.info("@cron(%s) cron_start() xquant running." % str(now))

        @crons.cron("*/10 0-6 * * 1-6", name="cron_future_update", tags=["server"])
        async def cron_future_update():
            FutureUpdateWorkerTask.is_active = True
            XLog.info("@cron cron_future_update()")

        @crons.cron("*/1 8 * * *", name="cron_tdx_deacitve", tags=["server"])
        async def cron_tdx_deacitve():
            TdxQuery.is_active = False
            XLog.info("@cron cron_tdx_deacitve()")

        @crons.cron("*/1 9 * * *", name="cron_tdx_acitve", tags=["server"])
        async def cron_tdx_acitve():
            TdxQuery.is_active = True
            XLog.info("@cron cron_tdx_acitve()")
        

        @crons.cron("26 9 * * 1-5", name="tdx_reconnect", tags=["server"])
        async def tdx_reconnect():
            now = datetime.now(shanghai_tz)
            XLog.info("@cron(%s) tdx_reconnect()" % str(now))
            TdxQuery.disconnect()


        @crons.cron("*/10 15-23 * * 1-5", name="cron_future_forbidden_update", tags=["server"])
        async def cron_future_forbidden_update():
            FutureUpdateWorkerTask.is_active = False
            XLog.info("@cron cron_future_forbidden_update()")




