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
import time
import json
from quant.libs.log import XLog
requests.packages.urllib3.disable_warnings()


class Proxy(object):
    class Type(Enum):
        HTTP = "http"
        HTTPS = "https"
        SOCKS4 = "socks4"
        SOCKS5 = "socks5"
        ALL = "all"
        DEFAULT = "default"

    default_proxy_type_list= ["http", "https", "socks4"]

    # https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=cn&protocol=socks4&proxy_format=ipport&format=json&timeout=20000
    base_ulr = "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/countries/CN/data.json"
    params = {
        "request": "display_proxies",
        "protocol": "http",
        "format": "json",
        "country": "cn",
        "proxy_format": "ipport"
    }

    proxy_url_list = [
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/countries/CN/data.json",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/countries/HK/data.json",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/countries/SG/data.json",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/countries/US/data.json",
        # "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/countries/MO/data.json",
        # "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/countries/MY/data.json",
    ]

    headers = {                       
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Sec-Ch-Ua":  '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        # 'Referer': 'https://quote.eastmoney.com/center/gridlist.html',
    }

    east_url_list = [
        "https://push2.eastmoney.com/api/qt/ulist/get",
        "https://push2.eastmoney.com/api/qt/stock/get",
        "https://np-weblist.eastmoney.com/comm/web/getFastNews",
        "https://push2delay.eastmoney.com/api/qt/kamt/get",
        "https://push2delay.eastmoney.com/api/qt/ulist/get",
        "https://push2delay.eastmoney.com/api/qt/clist/get",
        "https://push2.eastmoney.com/api/qt/ulist/get",
    ]

    @classmethod
    def get_proxy(cls,type:Type=Type.DEFAULT, use_request=True, use_json_file=True) -> list:
        proxy_list = []
        json_file_path = os.path.join(root_dir, "config", "proxy_list.json")
        if use_json_file:
            try:
                
                with open(json_file_path,"r") as file:
                    data = json.load(file)
                    proxy_list.extend(data)
            except:
                pass
        
        if not use_request:
            res_list = []
            for item in proxy_list:
                res_list.append(item["proxy"])
            return res_list


        if len(proxy_list) < 20:
            for url in cls.proxy_url_list:       
                res = requests.get(url)#, params=cls.params)
                res_data = res.json()
                proxy_list.extend(res_data)
        
        request_proxy_list = []
        res_proxy_json_list = []

    
        index = 0
        for item in proxy_list:
            # proxy_str = "%s://%s" % (type.value, item["proxy"])
            index += 1
            proxy_str = item["proxy"]
            proxy_type = item["protocol"]
            if type != Proxy.Type.ALL:
                if (type == Proxy.Type.DEFAULT and proxy_type not in Proxy.default_proxy_type_list) or (type != Proxy.Type.DEFAULT and type.value != proxy_type):
                    continue

            proxy = {
                "http": proxy_str,
                "https": proxy_str,
            }
            
            try:
                # url = "https://httpbin.org/ip"
                # url = "https://jsonplaceholder.typicode.com/posts"
                # url = "https://httpbin.org/get"
                check_data = None
                check_res = None
                url = cls.east_url_list[index % len(cls.east_url_list)]
                check_res = requests.get(url,headers=cls.headers, proxies=proxy, timeout=5, verify=False)
                check_data = check_res.json()
            except Exception as e:
                # print("Proxy except:", e)
                time.sleep(1)
                continue
            if check_res.status_code == 200 and "data" in check_data.keys():
                request_proxy_list.append(proxy_str)
                res_proxy_json_list.append(item)
                XLog.info("proxy: ", proxy_str)
            time.sleep(1)

        with open(json_file_path,"w") as file:
            json.dump(res_proxy_json_list, file)

        return request_proxy_list

    @classmethod
    def get_requests_proxies_list(cls, num:int=1) -> list:
        proxy_list = []
        while(True):
            proxy_list.extend(cls.get_proxy())
            list_len = len(proxy_list)
            if list_len > num:
                break
        res_list = [{"http": item,"https": item} for item in proxy_list]
        XLog.info("proxy_list:",len(proxy_list))
        return res_list

if __name__ == "__main__":
    data_list = Proxy.get_proxy()
    print(data_list)
    # path = certifi.where()
    # print(path)
    # url = "https://httpbin.org/get"
    # check_res = requests.get(url,headers=Proxy.headers, timeout=5, verify=False)
    # if check_res.status_code == 200:
    #     pass