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



class CookieUpdate(BaseModel):
    cookieStPsi: str
    cookieStPvi: str
    cookieStSi: str
    cookieStSp: str
    cookieStSn: str
    cookieGviem: str
    cookieNid18: str
    def to_dic(self):
        return {
            'temp_cookie_st_psi': self.cookieStPsi,
            'temp_cookie_st_pvi': self.cookieStPvi,
            'temp_cookie_st_si': self.cookieStSi,
            'temp_cookie_st_sp': self.cookieStSp,
            'temp_cookie_st_sn': self.cookieStSn,
            'temp_cookie_gviem': self.cookieGviem,
            'temp_cookie_nid18': self.cookieNid18,
        }

