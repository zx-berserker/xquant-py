# -*- encoding:utf-8 -*-
"""
date: 2026/10/30
author: Berserker
"""

from quant.libs.multi_thread.xtask import XTask
from .cot import Cot
from quant.libs.log import XLog

class FutureCotUpdateTask(XTask):

    def __init__(self, year:str, name="FutureCotUpdateTask"):
        super(FutureCotUpdateTask, self).__init__(name)
        self.year = year

    def task_main(self):
        try:
            Cot.cot_update_csv_weekly(self.year)
            Cot.cot_update_indicator_weekly()
        except Exception as e:
            XLog.error(e)
        