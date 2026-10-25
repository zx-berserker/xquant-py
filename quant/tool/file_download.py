import asyncio, httpx
from pathlib import Path
import json
import os
from quant.libs.log import XLog
from config.settings import GlobeConfig


if os.getenv("mode") == "IDE":
    HOST = "127.0.0.1"
else:
    HOST = "65.49.207.215"


async def adownload(name: str):
    url = f'http://{HOST}:8010/api/v1/xquant/tool/json/download'
    param = {"name":name}
    file_path = os.path.join('/home/xquant/cache', name)
    dest = Path(file_path)
    async with httpx.AsyncClient(timeout=None) as cli:
        async with cli.stream("GET", url, params=param, follow_redirects=True) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                async for data in r.aiter_bytes(64 * 1024):
                    f.write(data)
            XLog.info('Download: ', name)

async def main():
    try:
        res = httpx.get(f'http://{HOST}:8010/api/v1/xquant/tool/json/list')
        res_json = res.json()
        name_list = json.loads(res_json['data'])
        XLog.info("json_list:", name_list)
        await asyncio.gather(*(adownload(name) for name in name_list))
    except Exception as e:
        XLog.error(e)



if __name__ == '__main__':
    GlobeConfig.is_print = True
    GlobeConfig.is_log_file = False
    asyncio.run(main())