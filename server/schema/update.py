from pydantic import BaseModel
from typing import List
from quant.libs.enums import QuotePeriodEnum


class QuoteUpdate(BaseModel):
    startTime: str
    endTime: str
    period: str
    limit: int

    def to_dic(self):

        return {
            'start_time': self.startTime,
            'end_time': self.endTime,
            'period': QuotePeriodEnum[self.period],
            'limit': self.limit,
        }





