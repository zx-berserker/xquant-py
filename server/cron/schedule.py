# -*- coding:utf-8 -*-
"""
date: 2025/01/11
author: Berserker
"""
from tools import Crons
from server.lib.worker import ServerWebWorker
from quant.libs.log import XLog
from datetime import datetime
# from server.lib.cookie import Cookie
__all__ = ["CronSchedule"]


class CronSchedule:

    @classmethod
    def init(cls, crons: Crons):

        @crons.cron("* * */1 * *", name="corn_start", tags=["server"])
        async def cron_start():
             now = datetime.now()
             XLog.info("@cron cron_start(%s)" % str(now))

        @crons.cron("* * * * 1,2,3,4,5,6", name="cron_future_update", tags=["server"])
        async def cron_future_update():
            ServerWebWorker.future_update()
            XLog.info("@cron cron_future_update()")
        #     Cookie.cookie_update()
        #     print("update cookie.")




