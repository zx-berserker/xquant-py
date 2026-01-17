from pydantic import BaseModel
from typing import List
from quant.spider.east_money import QuotePeriodEnum


class QuoteUpdate(BaseModel):
    startTime: str
    endTime: str
    period: str
    limit: int

    def to_dic(self):
        QuotePeriodEnum.DAILY
        return {
            'start_time': self.startTime,
            'end_time': self.endTime,
            'period': QuotePeriodEnum[self.period],
            'limit': self.limit,
        }





