# -*- coding:utf-8 -*-
"""
date: 2025/11/22
author: Berserker
"""
# from curl_cffi import requests
import requests
from enum import Enum
import certifi
from config import root_dir
import os
# requests.packages.urllib3.disable_warnings()


class Proxy(object):
    class Type(Enum):
        HTTP = "http"
        HTTPS = "https"
        SOCKS4 = "socks4"
        SOCKS5 = "socks5"
        ALL = "all"

    base_ulr = "https://proxy.scdn.io/api/get_proxy.php"
    params = {
        "protocol": "http",
        "count": 20,
        # "country_code": "CN",
    }

    headers = {                       
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Cookie": "",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Sec-Ch-Ua":  '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        # 'Referer': 'https://quote.eastmoney.com/center/gridlist.html',
    }

    @classmethod
    def get_proxy(cls,type:Type, count:int=20) -> list:
        cls.params["count"] = count
        cls.params["protocol"] = type.value
        res = requests.get(cls.base_ulr, params=cls.params)
        data = res.json()
        proxy_list = []
        # url_east = "https://push2.eastmoney.com/api/qt/stock/get"

        
        if data["code"] and data["code"] == 200 and data["data"]:
            if data["data"]["proxies"]:
                res_pro_list = data["data"]["proxies"]
                for item in res_pro_list:
                    proxy_str = "%s://%s" % (type.value, item)
                    proxy = {
                        "http": proxy_str,
                        "https": proxy_str,
                    }
                    
                    try:
                        # url = "https://httpbin.org/ip"
                        # url = "https://jsonplaceholder.typicode.com/posts"
                        url = "https://httpbin.org/get"
                        check_res = requests.get(url,headers=cls.headers, proxies=proxy, timeout=5, verify=False)
                    except Exception as e:
                        print("Proxy except:", e)
                        continue
                    if check_res.status_code == 200:
                        proxy_list.append(proxy_str)
        return proxy_list

    @classmethod
    def get_requests_proxies_list(cls, num:int=20) -> list:
        proxy_list = []
        while(True):
            proxy_list.extend(cls.get_proxy(Proxy.Type.SOCKS4))
            list_len = len(proxy_list)
            if list_len > num:
                break
        res_list = [{"http": item,"https": item} for item in proxy_list]
        print("proxy_list:",len(proxy_list))
        return res_list

if __name__ == "__main__":
    data_list = Proxy.get_proxy(Proxy.Type.SOCKS5)
    print(data_list)
    # path = certifi.where()
    # print(path)
    # url = "https://httpbin.org/get"
    # check_res = requests.get(url,headers=Proxy.headers, timeout=5, verify=False)
    # if check_res.status_code == 200:
    #     pass