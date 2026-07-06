from fastapi import APIRouter, Query
from server.schema import QuoteUpdate, Fail, Success, CookieUpdate
import json
from quant.spider.tdx.tdx_query import TdxQuery, QuotePeriodEnum as TdxQuotePeriodEnum
from quant.libs.enums import QuotePeriodEnum

__all__ = ["router"]

router = APIRouter()


@router.get('/realtime_quote')
async def realtime_quote(
    period:str = Query('DAILY', description="period"),
    market:str = Query('-1', description="market"),
    code:str = Query("*", description="code"),
    count:int = Query(100, description="count"),
):
    # TdxQuery.connect()
    tdx_period = TdxQuotePeriodEnum[period]
    
    try:
        data_list = TdxQuery.get_realtime_quote(period=tdx_period, market=int(market), code=code, count=count)
        data_js = json.dumps(data_list)
        TdxQuery.is_bad_query()
        return Success(data_js)
    except Exception as e:
        TdxQuery.is_bad_query(True)
        return Fail(str(e))