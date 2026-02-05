#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytdx 自动查找最快主站脚本
使用方法: python find_best_tdx_host.py
"""

# from tools.pytdx.hq import TdxHq_API
# from tools.pytdx.exhq import TdxExHq_API
# from tools.pytdx.config.hosts  import hq_hosts
from tools.pytdx.params import TDXParams
from quant.spider.tdx.lib.host import hq_hosts
import time
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import struct
import sys
import zlib
from collections import OrderedDict 
from tools.pytdx.hq import TdxHq_API
from tools.pytdx.exhq import TdxExHq_API
from tools.pytdx.helper import get_datetime, get_volume, get_price
import pandas as pd

class TdxHostSelector:
    def __init__(self, timeout=3):
        self.timeout = timeout
        self.api = TdxHq_API()
        
    def test_single_host(self, host_info):
        """测试单个主站"""
        name, host, port = host_info
        result = {
            'name': name,
            'host': host,
            'port': port,
            'connect_time': float('inf'),
            'response_time': float('inf'),
            'total_time': float('inf'),
            'status': 'unknown'
        }
        
        try:
            # 1. 测试 TCP 连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            conn_start = time.time()
            conn_result = sock.connect_ex((host, port))
            sock.close()
            
            if conn_result != 0:
                result['status'] = 'connection_failed'
                return result
            
            result['connect_time'] = time.time() - conn_start
            
            # 2. 测试 API 响应（获取上证指数实时数据）
            with self.api.connect(host, port, time_out=self.timeout):
                api_start = time.time()
                # 获取上证指数 000001 的 1 分钟线，1 条数据
                data = self.api.get_security_bars(8, 1, "000001", 0, 1)
                if not data:
                    result['status'] = 'no_data'
                    return result
                    
                result['response_time'] = time.time() - api_start
                result['total_time'] = result['connect_time'] + result['response_time']
                result['status'] = 'success'
                
        except socket.timeout:
            result['status'] = 'timeout'
        except Exception as e:
            result['status'] = f'error: {str(e)}'
            
        return result
    
    def find_best_host(self, max_workers=10, limit=None):
        """
        并发查找最快主站
        
        Args:
            max_workers: 并发线程数
            limit: 限制测试前 N 个主站，None 表示测试全部
            
        Returns:
            (best_host, best_port, sorted_results)
        """
        hosts_to_test = hq_hosts[:limit] if limit else hq_hosts
        total = len(hosts_to_test)
        
        print(f"开始并发测试 {total} 个主站 (线程数: {max_workers})...")
        print("-" * 70)
        
        results = []
        completed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_host = {
                executor.submit(self.test_single_host, host): host 
                for host in hosts_to_test
            }
            
            for future in as_completed(future_to_host):
                completed += 1
                result = future.result()
                results.append(result)
                
                progress = f"[{completed}/{total}]"
                if result['status'] == 'success':
                    print(f"{progress} {result['name']:<12} {result['host']:<15}:{result['port']:<5} "
                          f"✓ {result['total_time']:.3f}s")
                else:
                    print(f"{progress} {result['name']:<12} {result['host']:<15}:{result['port']:<5} "
                          f"✗ {result['status']}")
        
        # 排序：成功的按总耗时升序，失败的放最后
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] != 'success']
        successful.sort(key=lambda x: x['total_time'])
        
        # 打印结果表格
        print("\n" + "=" * 70)
        print(f"{'排名':<4} {'站点名称':<12} {'IP地址':<15} {'端口':<6} {'连接':<8} {'响应':<8} {'总耗时':<8}")
        print("-" * 70)
        
        for i, r in enumerate(successful[:15]):  # 显示前15个
            print(f"{i+1:<4} {r['name']:<12} {r['host']:<15} {r['port']:<6} "
                  f"{r['connect_time']:.3f}s  {r['response_time']:.3f}s  {r['total_time']:.3f}s")
        
        if len(successful) > 15:
            print(f"... 还有 {len(successful)-15} 个可用主站 ...")
            
        print("-" * 70)
        print(f"总计: {len(successful)} 个可用, {len(failed)} 个不可用")
        
        if successful:
            best = successful[0]
            print(f"\n最佳主站: {best['host']}:{best['port']} ({best['name']})")
            print(f"响应时间: {best['total_time']:.3f} 秒")
            return best['host'], best['port'], successful
        else:
            print("\n警告: 没有找到可用主站！")
            return None, None, []


def connect_best_host():
    """自动连接到最快的主站并返回 API 对象"""
    # selector = TdxHostSelector(timeout=3)
    
    # 测试前20个主站找最快的（测试全部可能耗时较长）
    # host, port, _ = selector.find_best_host(max_workers=10, limit=20)
    # host, port = ("113.96.40.130", 7721)  # 通达信接入主站1（已知最快）
    host, port = ("101.35.247.235", 7709)  # 通达信接入主站2（已知最快）
    # host, port = ("180.153.18.171", 7709)  # 通达信接入主站3（已知最快）
    # host = '47.103.120.159'
    # port = 7727
    if host:
        # api = TdxExHq_API(True)
        api = TdxHq_API(False)
        if api.connect(host, port):
            print(f"\n已连接到最快主站: {host}:{port}")
            return api
    return None


def parseResponse(body_buf):
    pos = 0
    (cnt, ) = struct.unpack("<H", body_buf[pos: pos + 2])
    pos += 2
    result = []
    for i in range(cnt):
        # 64byte for one
        (category, raw_name, market, raw_short_name, _, unknown_bytes) = struct.unpack("<B32sB2s26s2s", body_buf[pos: pos+64])
        pos += 64
        if category == 0 and market == 0:
            continue
        name = raw_name.decode("gbk")
        short_name = raw_short_name.decode("gbk")
        result.append(OrderedDict(
            [
                ("market", market),
                ("category", category),
                ("name", name.rstrip("\x00")),
                ("short_name", short_name.rstrip("\x00")),
                #('unknown_bytes', unknown_bytes)
            ]
        ))
    return result

def stock_parseResponse(body_buf):

    pos = 0
    (num, ) = struct.unpack("<H", body_buf[:2])
    pos += 2
    stocks = []
    for i in range(num):
        # b'880023d\x00\xd6\xd0\xd0\xa1\xc6\xbd\xbe\xf9.9\x04\x00\x02\x9a\x99\x8cA\x00\x00\x00\x00'
        # 880023 100 中小平均 276782 2 17.575001 0 80846648
        one_bytes = body_buf[pos: pos + 29]
        (code, volunit,
         name_bytes, reversed_bytes1, decimal_point,
         pre_close_raw, reversed_bytes2) = struct.unpack("<6sH8s4sBI4s", one_bytes)
        code = code.decode("utf-8")
        name = name_bytes.decode("gbk").rstrip("\x00")
        pre_close = get_volume(pre_close_raw)
        pos += 29
        one = OrderedDict(
            [
                ('code', code),
                ('volunit', volunit),
                ('decimal_point', decimal_point),
                ('name', name),
                ('pre_close', pre_close),
            ]
        )
        stocks.append(one)
    return stocks

def kline_parseResponse(body_buf):
    pos = 0
    (ret_count,) = struct.unpack("<H", body_buf[0: 2])
    pos += 2
    klines = []
    pre_diff_base = 0
    for i in range(ret_count):
        year, month, day, hour, minute, pos = get_datetime(9, body_buf, pos)
        price_open_diff, pos = get_price(body_buf, pos)
        price_close_diff, pos = get_price(body_buf, pos)
        price_high_diff, pos = get_price(body_buf, pos)
        price_low_diff, pos = get_price(body_buf, pos)
        (vol_raw,) = struct.unpack("<I", body_buf[pos: pos + 4])
        vol = get_volume(vol_raw)
        pos += 4
        (dbvol_raw,) = struct.unpack("<I", body_buf[pos: pos + 4])
        dbvol = get_volume(dbvol_raw)
        pos += 4
        open = _cal_price1000(price_open_diff, pre_diff_base)
        price_open_diff = price_open_diff + pre_diff_base
        close = _cal_price1000(price_open_diff, price_close_diff)
        high = _cal_price1000(price_open_diff, price_high_diff)
        low = _cal_price1000(price_open_diff, price_low_diff)
        pre_diff_base = price_open_diff + price_close_diff
        #### 为了避免python处理浮点数的时候，浮点数运算不精确问题，这里引入了多余的代码
        kline = OrderedDict([
            ("open", open),
            ("close", close),
            ("high", high),
            ("low", low),
            ("vol", vol),
            ("amount", dbvol),
            ("year", year),
            ("month", month),
            ("day", day),
            ("hour", hour),
            ("minute", minute),
            ("datetime", "%d-%02d-%02d %02d:%02d" % (year, month, day, hour, minute))
        ])
        klines.append(kline)
    return klines

def _cal_price1000(base_p, diff):
        return float(base_p + diff)/1000



def hq_test():
    RSP_HEADER_LEN = 0x10
    qh_hex_str = 'b1cb7400110248690000f4238703820f789c8d97d94f535110876f2d8542aba82fee1a7d306e7179316a0c092d2d9ba5ad2d5130ae718dfe530a12240a145adbcbbd8552a1a1a5d82bcb4521248645220653a348404ce494d053d299c1f3d44cee3773ce99dfcc9c16099aee4f318f1815d0a5713bb28ddaf42fa35aa74e44e3117f64acaf11e273ecb5b8f355defbb3fb35c5ebec25241f4d74d4517caedd45f2aa124cf62f61b420e4d92b368d2f46231ecc83dee9cc3666dc5ff4fbf818c5e7bb483e475af2744a53e118b6c102ab25db98c37f05a5b62f146fb05ea7789db82cc7d440ec2fc61baf95671bb7a47f697b1b8665b3dd6601a2a4d676b31de00b36f0553538bfa3aa86e4d597f25060d66cb2bb617ea7d904580bd37c622a301e4cf68d45c6a40588dfe5b88aec2cb58c9c87f3bfdb01e82fe3fe18bfa61f38fe1e4719c51b390fc7dfeb00f4c7791de3a9fcefb342f1f9fdadf70f8cdfef24fb8776bd7f601f1c7092fd43cbea17bb3bb60e3ac9feb12575fec5d619ec834395c0f9b5e9f3ebbb9afcbdb1a0b4144cc2fc616b75b691d75fbeb4e019540670fe8815d02fe70b3ae6c4d5fc79e6605a108e9695661b33f4c7ee9ecaff093750ff7c694c6274b4a90c9f4027cb80fdf3fea76178c237d08ef1a75c00cff76f60f99722d8ed09c269177dfef5f98129e88c19d0af867b62faf17a077d9882ce5602f1b97e523c9e7d413857093436cee78acb23cdc3f5fe178a02f3e74b81fec9ef5fffe19738d91fec91b13d5c7017671bb9fef47d2dd1b8dcd29108cdb74520fea29bd46f3ee3590d60fc25b799e2b5ea627703cb5e47625886f8cb3660ff7ce95445ada7f45f540be43f433fe2943a111f0dfdc114546c01f2cf578aa7fa97c949f2c6351e7bfd0882d94ef23aff6cd747eafc256ef2fc3aa989be3f8b89e643af46c4d699aeaf980f6b35c4a7f5bfcd171697d9fcc3e2979740efa734bff55d88e62baa81f9c1e3172a61792812c63d54b980f8daf4fb256f34164cc694f6e758fc1b5660fe71fde7b2ba1543aa0fe36f56d0fa63f39be9ef58a0f138f4c12dcbe6f39be26f5bfe6f7e63fc1d0b39bf33fa37ece1ae05787f65f46ff67a6af5f5c6b100f78ac9ff4f06ef72f85ba72ff103e3ef9b6dd946aeff9c8149694a55e469791ce61f5881f7e786f73b5d7f0f4be9fa5b8baff4603e1ed5d0bcaa8c3453f11fd742f5c3f9c0cadbcf91e9fe15ccc7131b19dfe057dfff8e35e03b785a43bebf0dac7e3adf84e6310fcf2aae50fc3fb68c08a3'

    hex_str = 'b1cb7400110248690000f423aa018206789c7d945d4b02411486675dd734fa057d5217dd1454375111411aae2461e276913fa01f96122191598aeeaa9450e2fac16e621b29dd14dd088150220a41aea41bec9c3357c3e13c33e79cf79d99244ceea5181365022e46383407d9d16e420b69af72399fccd70be734deea0bc287f7f9f857ee02e339df1ecacb8a14c2789b2f80f29a9a6d95ba104dc8986f1fe339e53dd5d052c51f2861caed31072da31d3b9c1fc44ffbd1f9b1c3f94109337e747eac3ebf7c3ddd861266fde8fc2c83fe3b571f50c29c97d2bfe11ffb6d24f950cca6bbd9169d9f771f9983d6d1ce916ec7aa6a05e617dc4e8c1f979a625fbf58934e13b2e8e1cd41433fc629cacf110ffc82963c94fb8dfe191d5712951b885f0e50f8fffef9f32fa4e08a8be21fc63849d72f1eaf26200557bd94fe8dfa073c3c7d42d6bc02c6dbc4ded3652d9c3c55553abfce1f63bcfdf15b7c2b65ef33500d1bc2ae3968e86f2f44e572262a29779fd7791abf29a0fe71e8bcee4188df125c18cf6a9ddc99ae9ea4d432347efb8052bfb1384dd5c2d8ffb313a4e86ff8c7926a887205f8fbf4c5f3e8fbe5c41e7eff098fdeff0b5b96d41a'
    

    hex_product = 'b1cb740011a0040b00008424f2140236789ccd5a09585347d79e84cd045044dc05b48882205851abd52cf7262121212ab8d6a2e2965ab58a6db57ea07ddcd06aa948dd4870276a55a4564583b228282a824b5b8b5a4451ab1670ab06ac0b7c73e67213ac977ef817fbfcf33c9333993be7dcf7bc7766ceccdc3bae0722c91fa96543c343d0eb49ea805051720915e376892a2c60653105d740c684b5403c5c0e786c1bbac2ce19ddd3d87358699cc4b3fcaee95d6c411173245130c8e32e95aafc88d4015a56e33c7d41c461e8a50d7adff20774585be1262ce1cf3bdebd79d2a508fd2a3e9375847650c0c52337bfd7d8dbf5d24039e38c13ca8eb5470f6a08735a8e9b8cc54073cd3ed2a0202fa9b0c84baad3b52219ae816c96cdf87366cb32d5acfe3c6458f48f09aa37f1c92fdcafb0b9bbd42db53541219a31d15155fabed433b65c0288002daba17d1127e6306403cc993cbca585051d70db8eb51e75948a84d8261806e6fa63e6d63519999d1e785ab6e9830bcab9033aab5cfa9d51fcbc1da199ce3c942f44680fc3dc408e9b04dac05309a40b0bfc69dfe2403a66b52f6dd0fbd3700d64cb663ce2d1c1f23e6abbd508b9c4342a59af246b9f1b77d8df8262617aa200a1603a227e0905758096d548899bcad5e778aff639ab2d2813b758e6345f8ab20e5fec2b838b93fcdba9233bdf564179ca2d84767743e805616e0817da605b8462cb07d1e1262d2d2c1a4c070569e8a2642db90fc869763628d709a1c7cbdb6b4aee22b4a203bf3148e24c56e6aa1e6b2d289edf0e112e2e1f4cebf50ea40ed0b21a630d1f70f539c21cb46333ab678c1a4813b780b935cbf0084dde97c557dd97f976c8533c1afe937a5a7ba53a1a5b7073e6a3922a84ae33cca9386ef2117e9ebadb46daf830994e3d69c4fd6e2b6df230126c448605a389b85cea79403b625d67b433bd9345b7226c33fd577b5b38ee51fa6cfb6bed0c7fcbdf7b7f246324c9446bccd1858e553efbe996010b083240cbb69de375f908870932cf450e37d286b646a2e3442793729117d605c32c7341578f88bf377a07dfca3eab8ab719adbd7c5ea8edea86d0443f3fd4bc797b186ec0dc208e9b7861a0c38ef948f0ec21d12eee2e4955762219ae810caa647a4249ea56e58e0b08c575e6d5eb73e324b01f497be339ad0b4111d8f38020c6edacc4a06f4b90015ab6ad9b2fe21aad35c0dc399db7e4c0078c1d90908fe563cfa00298735e823bc7a24ed93db5936563ef64d261e317287b172e0e5e852da4ade0a1721d428f489f1b4e71dc4483fb9c5bea2afc4456d13add2ada3376259e15126ae7b904da6e515fd40c97c38eccd7babbbe83ee46b57a0b6c31c91a2152f2132c285e36bf2d34b435d037a287903a40cb6a1c687e9e8b390732cfcdff966633b185a56963024ddc629933fce6239a38cb3db8a8c38be0a4ebfeda88f63b43d33182aa726f14bcc615dd27cc8de0423b1de7847b19f889a64b5ac6dd20d21875953c5590cfa53cd41f978f9faf52bac7e1be77a091e9aa93accc693cf32c289a6ff31256faac97c6e7a4913a40cb6af41ad92a8bc3507513cc9c4878481214b49fe894461fa8cd3f4b885bc09c2b662ee9e112a9a67802fd595253e57717772b074b9d159193106af50b1ea676086de711e6b8466b20ced83eee8ea93872a5513a5d0a551a9d42ba27c8c3b541aae5a7c9aa07bdf0eac4aeae768fd7baf1444e4e6c5f9be7b8da5923c4c241fb5eb1acd31da62a7de612640c5a26ed3222ce558910f5e1c4817b29a30bcc85e0a542e4ded8a3aa454ea4f2e2c8ad2ab4d989aced86bfcf401c5b0dcc8d0ce7b0e4c78348a090cc3f2495b8a52a25359d44929e5f88c85305d9d2c996b4f35251aa2a011f79f0df5e6cb5f639a762b1a4db4e1941d12b72a230c64d2c85390e10015a5623d5d02283c350358c56bf360a89b04826c9bc299764cf13592402c36c84d894f13473d6200ff90cf35245cdec205593766d83bbe3f968518e0d9a1444c0a865c35e7bee'

    hex_kline = 'b1cb74000c01086401002d0529002900020022253501bcaa01ee019a01ee01593cd04cf7ff8d4e6a2535014abe02920354911c884cbb633a4e'
    byte_data = bytes.fromhex(hex_kline)
    _, _, _, zipsize, unzipsize = struct.unpack("<IIIHH", byte_data[0:RSP_HEADER_LEN])
    body_buf = bytearray()
    recv_pkg_num = RSP_HEADER_LEN
    recv_pkg_bytes = RSP_HEADER_LEN
    last_api_recv_bytes = RSP_HEADER_LEN
    byte_body = byte_data[RSP_HEADER_LEN:]
    # zipsize = len(byte_body)
    while True:
        buf = byte_body[0:zipsize]
        byte_body = byte_body[zipsize:]
        len_buf = len(buf)
        recv_pkg_num += 1
        recv_pkg_bytes += len_buf
        last_api_recv_bytes += len_buf
        body_buf.extend(buf)
        if not(buf) or len_buf == 0 or len(body_buf) == zipsize:
            break
    last_api_recv_bytes = last_api_recv_bytes
    
    if len(buf) == 0:
        print("接收数据体失败服务器断开连接")
        return
    if zipsize == unzipsize:
        print("不需要解压")
    else:
        print("需要解压")
        if sys.version_info[0] == 2:
            unziped_data = zlib.decompress(buffer(body_buf))
        else:
            unziped_data = zlib.decompress(body_buf)
        body_buf = unziped_data

    print(f"Zipsize: {zipsize}, Unzipsize: {unzipsize}")

    print(body_buf.hex())

    data = kline_parseResponse(body_buf)
    data_df = pd.DataFrame(data)
    print(data_df)


def test():
    data = bytearray(b'x\x9c\xd5[\x0b\\\x13\xc7\xd6\x9f\x84g\x12D\xd4X\xb5*H)V\xaa\xb6H\xa4> dwCH\x08\x0f\x95\xfa6\xf5\xda~-z\xd5\n\xb4>\xe1\xd2*\x18Q@B}\xa0\xa0\xa0\x16Tj\x15\xadbK\xb1"\xe2\x03Q\xb0\xd6\xc7\xc5\xab\xd5\x8a\x8a\xd5\x82O\n>@\xb8sf\xdd$\xc8bi\x8b\xdf\xef\xfb\xe6\xf7\x9b\x9c\xddy\x9c\xfd\xcf\x7f\xcf\xcc\x9c3,\xef\xbb#\x92\x06 -\xcd\xa8F\xa0\x96Ii\x8d\x90\xce\xf0%u\xa8v#\x95\xe7\xb8\x99r\xd3m\xa04\x15_RP\x072\xdbW\x8c\xfa\xe1\xebs7Fh\xdd\xd6Y\xa1\xcf\xbf\xb24\xf6\x15\x97\xaf\xa4\x9e\xd7\xf7!\xcf34\x15\xbb\xdb\xd4\x8eM\x02\x9c\x17?\xdddDq\xd3\xb1\x8bd\xa1\xe6>\xd5\xb4;\x8a\x94\x01Z\xae\xed\xdc\xed]\xf6\xf3\xa9\xb0@\xc3\xd1\xc8\x86\x8d\xd4\xb4=\x1bI\x1f\xb8\x86,\x93eRdX\xaf\xb9z\n:,Ah}q7\xc5\xe9\xfb\xa1*\xf5g.*\xc1~\x996ArEc+D(\xfa\xaa-r\x99"@\xb7\x9b\x08s\xa3x\x1e2\x01g\x99\xac;\xa3\xaf\xea\xca\xb8\xe9\xba1e\xa5R\xc6P\xd4\x95\x81:\x90\xf3\xd6\xb3\xedJ6}\xeb\xff\xcf1\x08\xd9\xab[\x1d\xf2\xdfNBv\xd88\x0f\x99\xd1\x95q\xd2\xb3(\xfa\xef[+\x02\x84\xc5\x0154 \x82k\xaeG\xc9\xa4(9\x8f"K1\xean\xbc\x01=\x9c\xae\xd0P,\xe1\x06\x98\xbb\xba\x18\xa1q\x07\xe6\xfax8\xae&\x95\x16^\xbb\xfc\xfb\\\n$\x03lHA(\xca\n\x81\x1a`n,\xcfCz\x89\x809\x19\x059\xcf\xd1\x93*\xcft\xa7\xf4U\x83(\xa8\x039kk\x11\x0c\x05%\x1fK\x0f<\xae\xaeGY\xff(\xfe\xfb\x14\xbd0\xc1\xe3>\x1a.\xa3\x98),\nmR\x96D\x9a3\x84\xa2\xa7\x9cS\x00"@\xca\xb5U\xffh\xeb\xc3\xa3\xa2I\x80m\xae"r0U\xec\xe6A\x8d\x9e=\x18\xb7w\'2G\x8du\x82b\xce\xe6\xea?\x1f\xea\x93\xf2f\x92\xba\x83w\x85z\xfa\xb5\x94\xc0>G\xc7h\x05\x9b\x10\xba[\x9a#\xf8lX\x17\xf2|\x9a\xf1\x0b\xe4yH\x10\xce\xe2q+\x19y\xfc\nL\xfcJ&44\x999\xb76\x99\xbc\x04\x90\xef\xa9\xd8v\x0f\x03\xd2\xfd\xe7\xe1\xb9\x7fC\xda\x8e$=\x97L6\xf7\xe5\xeb_`;I6\xda\\\xc8\xd0U\xcc\xb6\x08\x1dA\x06h\xb9\x1e\xc7\x9b,\xda`s\xc9F]0:R\x00\xccmX\x86PB\xae\xc4g\xd3\x9c\xb7\xd8\x079\xac\xf7_\xd8\xdd\xd1\x0f\xae\x7f\xf2E(\x11K{\xc2\x1c\xef<k\xb2\x02\x9b\xfbX)\x93\xcdP\xcajf(\xa5\xb3\xa6*\r1\xd3\x95P\x072\xf7\xb6\x90\x8c\xe8\xa3%\xfd\x03\xe5\xab\x04h\xde\x04\xc1\xdf\xa7\xe8\x85\t\xf4\'\xab\xa7\x1bQ\xa4\xdf\xd9*\xcaQ\xafWJs\xfcI\x19\xa0\xe5\xda>\xd5gy\xf3\r\n\xd69\x84\xa0\x1d\x9bY]\x1f+C\xb7`\t7F\x9b\x1b\xe1\\\x90q\xbeH\x99\x16\xb7Nuf\xe7\x9d\x801[F\x06t\xc5]/\x88\x84\xe8\xc85\x84n\x91u\xce\x9f\x0f\xa7\r\xceu\xfd\x8e\xd1n\xba\xe6\x19\xea@\xda<kg\x1f\xfc\xb6\xd2\xe6\xb9\xbe\x11\xf2\x14\xfay}|+\x7f\x84\xfcI\x9b\xda\t\x8c\xbf2\xd91\xfa}\x0f\x16E\x9de\xb2\x08\x10z\xd8\x16\x11dp\xcd\xf5p\xb2x\x95\x8f9+s\x9b\x03=\x9c."\xe1\x07\x98\x8bX\x8aP\x8f\x9cL\xb9\xfd+\xab\x88\xe1>\x1d{\x8cqR\xa5\x10\xfb\x83m\xd0\x02g[bs\xfe|Fg\x0bX3\x04L\x8e\x9a\xcd[\x17 \x92\xa1\x0e\xa4\r\x1e\xc8\x02|\xed=\xce\xd2\xaf\x11K\x91Y_\x9daa\x0bF\x8e\xf1<\xc3PD1migb\xae)\x1e5\xeb\x91|\xdf\x82\xb1\xdd^L\x03"@\xcb\x95\x1f\xd1h\xf9\x98k4g\xce<\xa5\xa5>\xd3\x0b\xcc\xd1q\x08)\n\x8f\xee\xcf\xfd\xe50\x05e\x0b\xbc\x0c*\xaea\x12b\x87\xfd\x90\xd8\x1c\xdf2\xf7\x7f0\xb5\xc7j\xc0\xce\xd6\x17\xa4\xc9B\xcf6=\xe7<\xcb\x9c/O\x95#\xceY\xe1M\xb4\x93\xbe\x9e\xe4/\x1a\x1f\x93\x0cu \xefvb\xdb\xe9\'\xdai\xfe\x85\x1f\xf6\xa9\xc3\x9f\x19\xc1\x9fK\xa6\x1d"\xaf\xe4\t={/;\xc7\xe3\xf2\xd6\x8a\x00a\xe3\xd9}\x04\x19\\s=\x86\xde/\xfe\xc3\x1d\x02\xf4p\xba\x88\x84\x1f\xb09\n\xdb\xdc\xc4\xc4\x15\x05\x07\xbe\xa5H\xe5\r\x17;\r*\x9cH\x16\xd1\x9b\x9d\xd8\x85\xec:\xcb\x1c\xdfl\xed\x8c`=\xb3`\xb2\xc2\xf1l-\x16\x109l6;\x1f@\xae\x92\xb0\xed4S\xf6\xa9a\xa6&HL}\xd3R\x17\xb5i\xb6V\x8fb\xda4[M\xcc\x15,`\xd1\xc0=\xec\xad\x89\xdf[2\xdb{\x1d\xa0\x01\x11\xa0\xe5z\xec\xd2t\xe6c\xae\xc9\x9c9\xd0\xc3\xe9"\x12~\x80\xb9\x93\xf1\x08\xd5\xac_X\xb0h\xfb^2\x8c\xb3\x97\xf3\xd5h\xfe"\xc2\\\xa2\x84]\xc8n\xb2\xcc\x05\xfe\xbf\x98\xaf\xed1[\xc5\xa8\xdb\x8b\x1b\xb4u\xb6"\xb2C\x04\xbe\xcbS\x0e\x1b\xc8\xccG\xeb\xe9\xc1_4\xcfP\x07r:b\xc7R<\xcdB\xf5\x0e\x94\xb5\x1d\xfe\x9fN&\x9b\x9bf\x86\xe2\x93\xfb\x06\x91\\\xbc\x99\x9e\xe2\xf11)\x03\xb4\\\x8f\x02\xdb\xec\x1fx\x14=5\xb79\xf3\x11\x19\x0b\xc0\xe6\x1a\x13\xd8\xfb\xfcs\xf6FwZ\x91-0\xee\x12\xd3Y\x01\xcc\xf1\xc5\x10\xb0l\xf5.\xf1T\x18\x8a<\x15\x9b\x83)"\x87\xfd\xdbS\x01u \xc3{\xb0\xed\xbcN|\xa1\x12`8a/\xd1\x9d3\xed\xad!~C\x14\xcb\xfb\xc9\t\n\x98\xad:\xc3U\x85\\\xdc\x8d \x03\xb4\\\x8f\xc8\xb2Q\xbc\xb3\xd5\xd6l\x87\x00=\x9c."\xe1\x07\x98\xeb\x12\x83\x1f\xb4|~\xe1\xa8\xd9\x17\t\xado\x15~\xa1B\x85\xbbH\xc3Y=\xd8\x17\x19\xdd\xc827\xae\xe5C \xc0\xd8\x13\xf5\xc0\x9b\x99RI\xb2W\xf8I\x92\xa1\x0e\xa4\xb4\x17B\x12\xec-\xaf\xb2V*\xa7c\xb9\xed\x95\xf6\xe0\x88?\x99\x98s\xce\xbc\xd2\xcc\xdb\xe8\x101@\xde\xa9x8A\x06h\xb9re\xd25>\xafD\xe0\xd0\xca\xde\xca\x8d\x8cx%\xb3\xb0?\xf7mi\xa0\xe2\xf0\xf6\xcdd\x11\\\x8d\x87\xc85\x84aC\x1aIl.\x88O\xd7-\xccF\x94t\x08\x13!\x7f\x07\xc75C\x19M\xc5`\xa6\xae\xdfP\xa2\nd\xc9f1\xf1\xe1\xc2Jk\x02\x86\x89mP\xf2:\x8b\xb6\xd1\xf0\x97\x130\x171`\x88\x11\xc5\x0f\xea%\x92df\x1c#.w$e\x80\x96k\xdb;\xe8;>\x9b#g%\xd0\x0e2\xd7\x07r\xb9\x0b\xd6\t\x05\xc0\xdcp\xbc\xb76\xf8x\xf8<\x12\xfc\xe4+\x19w]\xb9\xd7ku\xc0A\'y\x80\x18kp\x8d\xb7Fi=-\xc1\xee0s\xc1-68\x9c\xd6bZ\x9c\x8eX(C\x1e\t\x95:\x83\x85R\xd7Q\xa0\xcc\x9b, \xe4\x83\x94~\xe6I6\x99\x15g\xce\x07\xad\xec\xd8\x05-\x9a\xf5\xdaK`\xeb\xd9\x80\x8d\xbf\xcc^\x13\x8a\xcf\xa7\xe0\x88\xff\x8e\x8b\xd2PT\xcc@\x19\xa0\xe5z$\xcc\xb8\xc3\xb7\xce\x11\xe64\x9b\xa0\x9dP\x89\n\x85dT \x89N\xf8\xe1f\xeb\x1b)\x1f\xcb\x0f\x0c\xb6\xf5\xeb\x9b"\xf0\x1f\xc6\xac\t:\x9c*\x0c\xfaOG\x84\xc6\xaa]Qe_\x07\x00\x03\xcc\xf1y%\xe0\xae\xe9\x0cqtZ\xaa\x9e\xe4\xe3\xca\x18\x92\xa1\x0e\xe4 ;l\xba\xf8:x\xb4\xbf:\to\xd5\x99\xedM\x97Y2\xed\x10\xd1\xce\x8b\x9b\xf9;\x07\xb5i\xf4l?\rA\x06h\xb9\xf2\xe8\x87\xf1\xbc\xe7s\xad\xc5\x10:\x03;2\xc4E_\xff^2\xb5\xe0@\\-\x05e\xd7~T\xa9Qn-y-O\xf0P]\xb0\xfc\x8dx%\xc1\x13xty\xe0\x1c1S\xc6,\xcfvo\x96\xa1\x0e\xe4\x82g;\xc2\xa3\x9d1~0\xb2y\xcdv\x88>-\xcc\xf8\xefo \xa0\xa1\xacT\xc6@\x86\xfbe\xd8\x13\xfe\xce\xf1\x13f\x87ZH\x90\x01Z\xae\xed\xae\xd2\x86?\xdc[\xcdu\x11\t?\xc0\\\'\x1c\xf1\xe7o\xf9\xe5\xc0\xa4\xc8\x18\n*\x9b\xd2\x17\xfa\xa1\xcf\x16\x13\xe6>\xc5(\xac\xb1\x0c!\xcc\x8d\xe0\xf3J\xfaZ\xc0\x9b\xf0 gr \xcbJ{Q\xa1\xa1}\x89*\x90{v\x8a\xd1M\xdcf\xa2\xc5e\xff\x99\xb5\xd6H\x9d\xff\xf2\xd69\x93\xcdY\x8c\xe8K\xd58\xbdFPx\xfe\xbeT\x92<HI\x9d\xfbu\xa2\x02\x10\x01J\xae\xc7P\xc1f\xde\xf39\x98\xadp\x8e\x17%}\x8b\n\xf1\x1f\x84G\xe7L\xa4\xa1\xc8\x95B\xa0\x18\x98;\x8e=am\xa2T\xd1\x98\xf3\xb6\x9fK\xca\x01\xbf\xfe\xebO\xfa\xcf\xebR\xa4.\xc4\xeb\x91e\x8d\x08\xd9\xa4 \xd8h\x80\xb9\xd1<\x0f\x81\xd5?\xd2\xb53S\xdf\xcb\xa1Y\x86:\x90\xdc\xaa\xb6}j\xaa/Dj\x96f}\xa3\xa4\xc9m\x8a!\xf2\x1c\xc7\xff\xc9\x18b\xdb\\\x07F_\xd5\x91\xf4\x8a\xc767\xfd\xb2\x0bswk\x15\r\x88\x00-\xd7C\xdci\t\xdflmfs\xa0\x87\xd3E$\xfc\x00s\x9d\xb1\xcd\x1d\x9d\'\xf2q\x9f\xfa\x1f\xb2\xcd\xa4\x89\xa2}\x17\xf6\x1fOl\x0e\xb6V\xb0\xb9\x0e\x84\xb9\x91<\xcf@K\xa1K\xeac\x85LV\xa3p;a\x87\xed\xed\x06\xf6\x9c\x1e\x12\xa7\x06\xe4\xf7q\xecX\xee~\xafW\xd7h\xf1\xa3\xf8\xbc\x80vM\xf04\xfa\x8dz#\n_U\x05~\xbdv\x8c4\xe7!)\x03\xb4\\\xdb\xc9\r\xa2\x03<*\x9e\x9d\xcf!JS\xf1D\x01\x19\xfa\x81\x0c\xc9kT\x90aq\'\x9b\xa5\xe9\xce\x85\xfa\xaa\x0f\x94\'\xba\xe6\xaavX\xccR\xe7~}\xc9\xf7=\xbc\xc6\x1d\x99\x8f\xd0\x1a<\xbb\xde!\xb3u\xe48\x1e\x7f\x0e\xb6\xe0\x0f6\x8d\xf5^\x15\xa7\'\xf9\x94\xefx\x92\xa1\x0e\xe4\xddw\xd8\x17p\xa3\xc0K\t\xd7/3\x99\xf6\xd6\xdf\x9f\x8en\xf6\x866\x07\x17\xcaow\xf0!\xc8\x00-W\x1em\x17\\\xc0\xa3\xa8\xa95\x7f\x8e\x1b\x19\xd9!\xba`\x9b\x1bV}Xa\xe9\xc0\x06\xc2M\xf9^\xc6M\x9b\x1bj\x1a\xb1\xb9\x10>]\xbdE\xe0\xb75P\xf8M\xe2\x15\xe4\t\x85\xd0=lwu\x14\xd4\x81\x1c*\x0e \xed&\xdf\xb2\x0f\\\xc1\x0c@[\x8a\x1d\xff\x98\x82\xbf\x98L\xb3\xb5kQ\r\xb5\xf0;\x16\x85\xf8\xdafI\xd4\x83\x11t\x84\xfc\x01A\x06h\xb9\x1e#t\xd1\xbc\x9e\xb0\x05\x1a`\x1c\x15\x95\xf5\x18\xafo\xb5D\x86\xe4a\x9d\xa0\x18\x98;\x88\xd7\xb9\xd1\x0ez\xf9k\xeb^\xf5\xab\xff\xcd]\x9d\xab\xab\tx\x12\x9d\xad]\x89\x9d\xfd2!\x85\xce\xdf\x13\xa3zbs!\x03y\x8e\x99\xe0\x10 44\x89\x0e\rM\xa4\xddtIx\xddJ\xa4\xc5\xe5\xcb\xc9\xfa\x05\xb2\xc9\x8dmw\xbc\xd30M*\xde\xa7C\xad\xdb\x91*\xde\x04\xcc\x9d\xa9H\xa4s\xd4,\x8a\x04\xbc\xce9\xe9\xd7\xe0\xeb%\x04\x19\xa0\xe5\xda\xda\r\x1c\xcc\xe7\t7\x8a\xccl\x0e\xf4p\xba\xac2\xb1\x84\x1b`n\x1d\x9e\xad\x13;\xdd\xf4\x19\xdbw0\xb1\xb9I\xdb\x06k\x16\xc6&\x92\xb8U\x80\x87\r\x07\xb9\xec\xdf!B\x06\xaaZ>\x04\x14FI\x93\xb0\x97\x94\x84q%\xd1\xe5\x99\x89\xb4L\xc6>\x07d\xaf\xael\xbb\xc8\x89\xf9\xea\x9f\xb1\x1e\xea%2g\xb2\xb9\x99\xda\xe5tYi\xa2\x919\xec\xb1c\xc6b\x082@\xcb\xf5\xe8\xbfl\x0co\xdcj\xce\x1c\xe8\xe1t59\xe3\x91\xc1\r0\xf7\x18G\xfc\x1d\xb2T>se,s\x97\xf6\x7f\xad.\xcc\xbdEH\x9a\x8d\xa3\xd2l\x8c\xc4\xea\x19s~-\x1f\xe2\x8a\xf3\xa1\xda\xdd4\x97\xd3R\xbf!\x12=+\x9f\xeb\xc2\xb6\xfb\xc7+~\x9a\xf9\xd8\x8c\x1b\xed\xfe6A\xad&\x13s\x9fD\xef\xa65\x15,\x8aD\xcc\xdc\x8e\xc8<\xcc\xda\x06#J\xae\xc7\xde\xcd\x95\xbc;\x969s\xa0\x87\xd3\x05\xa3#\x05\xc0\x9c\x03^\xe7\x14"_E\xdc\xa7\xf6\x84\xb9\xce~\xa9\xea\xed\x95\x0fH\xbc\xb0\x1fo\xaa\xdfw%\x7f\x1a\xc4\xcc\xbd\xcb\xf7\'\x9c\xa36\xb0W\xd3TV\xb8\x9c\x12\x97+\xa9\xeaQC)7\x9d\x82\x82:\x90\xfd-=H\xbb!\'\xbb\x04d\xb9\xf7@qg\xf8\xbd\xf3\x17%C\x91\x8az\xbeLj\xd5Zk`.A&\xc7k\x92\x0f\xe9\x95V\x1f)\xd1\x19\x8eS\xe5\x99\x88 \x03\xb4\\\xdb\xbb\x0f\xad\xf9v\x08\x12}A[\'\xbd\x17nKQ\xbb\xd3\xbdH\x96\xe6\xe0\x91\x81b`nl\x12\xdb:g\xc3=\x95\xc3\xe5n\x9a\x9e\x1bP\x80\xf5\xc2%\xfe\xff,\xc3!_J\x7f\xa4\xdcH0b\xe6\xf8\xdc9\xf4\x08\xcf\x04\xe9[g\x99<\xc7\xb3\x8c\xac\xe6\x02\xe3\xa6;\xc3\xa4\xa5^ /\x01\xa4K\x8cD\x00c\x99\x14~58\xec\xc7\x04\x94\xbb\xfb\xf36\xb1\xf5W\x92\xc9\xe6&\xe4\x9fg\x9c\xacX\x14\xe7\xfc\xb7J\xa2\xce\x8a\x95\xf2\xf8\xd3\x04\x19\xa0\xe5z\x8c\x8f\xef\xde*s\xd0\xae\xfa\xa73X\xcfE"!\xd7ec\x9d\xa0\x98\x8b\xf8\xcf\xe6y\xf9h~uWg\xf5p\x0b8\xe2\xba5\xb8\xfc\xe7_\x83$k\x05\xa8\x9b\xedQ\x84\xae*\xc1}\x05\xe6\x94<\x0f\xd9%\x02O\xf5\x08\xf6\x90\n\x15\xe2\xf2C\x8a\xac\xf0\xfd\x8a\x1c\xf5A\xe21\x81\xcc\xbd\xbe\x88\xb4\x93\xa8\x94\x01GV3\xe8n\xb0\x82GK\xfb$\x13sw\xc2\n\x15\xde\xc1,\n\x95\xcbVI\xf5\xa8i4\x87\x8cE\xcb\xa6\xe2\xc2B>O\xb8\x11\x98\xd3\x19\x8a\xb0\xffV@F\x05\x12\xb2\xbe\n\xeb\x04\xc5\xc0\xdc\xdb\xcb\xf1\x16\xf3$\xbb@8\xed\xb0_\xff\xb88\xcd\xc3\xb8\xa1\x01\xab\xf7\xfd\xa8\xa9)\x13\xa2\x8ac\x91\xe8J\x90%rf\x99\xe3\x8b\xbe`\x81\xad\x88L\xc4q\xca\x12\xec7\xc6\xe3}|\x01\xc9P\x07\xd2\xd6\x91\x8d\xf8\x9b\x16\xd7\xfa%wDh\xbe};\xd3e\x96L\xcc\xbd\xfbf\xac\x11\xc5\x80}kEy;\x07\xd2\xd2S\xdb\x15P\x06h\xb9\x1e\xe3zw\xe3\xb3\xb9\x06\xf3\x93\xcd\xe7GD~\xb8\xb3\x92I:\x87\xc2\xf7\xc3o\x92E\xf0\xb3O\x7f\xf7C\xa5\xd3\x88AW\xf6F\xa8#\xdb\x1f37\x86\x8f\xb9\xa9V\xe0\xcf-\xa6d\xb2X\xbc\xd6\xe91\x831\x14\xdcC\x1dHO}\x07\xa4\xc1\xd7\xebk&k\x7f~b\x8b&\xc4[\xf2hi\x9fd\xf2\x84\xe3o\xc4\x1aQt*l\x12\xc37Hy\x8e\x03I\x19W\x0e\xe9\xc2!\x07>\xe6\x88\xcdqm\xcdsy&\xee\x0b\x17\x9c?\xb7X\xf1H>\xe1\xa2D%\xdc\x93\xa5\xdc\xf1^7\xad\xdb\x1b\x06\x7f\x88\xb5\xf2\xde\x16\xa1\x81c,\x91\x1dan,\xdfl\xb5\x17\xc0l\xb5\xc2>\xa65\xc99j\x01\xc9PG\xae/\xb2\xb6 \xdb\xff\x8b\xfa#<q\xfd\'\xb6+Y<\t\x98S\x8e\x13\x1aQ\x80\xcd\xb9\xe9vRe\xa5\xa5>P\x06h\xb9\xb6=\x83\n[=\x9f\xa3\xb2l(.C?\x90:\x83\x90"\xc3\x02\xe6|\xf0:W\xfd$\xf2@\x9fG\xf5\x8c\xa4\xd1RU\xd5\xfd\xa4\xfa\xcd\x11\xe5\xaaj\x1cu-8\x8e\x87\x8a\xf7\xd70\xe2\t\x8f\xe5q\xe7\xd0\x10kS\xdcj(\xb2\xc2\xf8\xaa\x15\xb0\x8bA\x1d\xc8\x0c\xd5\xab\xa4\xdd\x0f\xde\xa3\xb4G3\xed\xd1\xf9M\x12\x1e-\xed\x93L\xb3\xd5\xd9\xabIq\xf8\x1b!A\x11V\xb7C\xa2\xaf\xfa\x89\xea\xd9a\xa1\x0f 2\x8f[/\xd9\xf8\xf3\x9d\x95\x10\x9b\x8b\x90\x8b\xf1^|\x17\x8f\xcc\x82:\x1dvW\x01\xd7\xd5\xa3\xf0\xc8@10\x17\x86cv\xd7\xcb\x01r\x9f\xad\x1bT\x8e\x95\xf9\x9a\xce\xa5\xafkc\\\xb35\xcb\xae\x08Q\x8f\xc3R\xd4\xb0\x11K\xd6\xe6T<q+\xfc\xbd\x15{"\x8a\xb1\xd1\xc1$\xa7\xa5\xf6 \x19\xea@\x06E\xe2u\x0e\xafu\xdf\x8d\xf9\xcao\x03\x8eAr<\xdb\x9b/S2\xcd\xd6\x0c[\xf7f\x1bQ]\xbfREX\xe7Xo@\x04h\xb9\xf2\xb9#\xe3\xf86\xac\xc6\xd6\xe2V\xec\xa1\xb0\xed\xb9\xf3\xb9\xc6\xa6\r\x07G\xb9\x0c \xb3q\xdc\xd1X\xa3\xc3;L\xc7\x0e{\xd0#\xc2\xdcx\x1eMkm \x86\xb8\xc6Hs\xae2e\x81\x95\xcc\xa1\xdaKX^f\xcf\x01\xb1|\x92\xcd~IR\xd2).\xb0\xf1\xa2%j(}y\xeb\x9c\xc9\xe6\x0e\xe7\xff\xc2\x0c\x8f\xfd\x85\xa0\xd8\x98\xbf\x03{%Rey\xe6Z\n\x10\x01Z\xae\x87\xd3\x05g\xbeu\xae\x1e\xbe\x9f\xcbQ_g\x0e\xcd\xb9\x82\xbd\x91\xabdD s\xd4xd\xa0\x18\x98S\xe0\xd9\xba\x7f\xc4\x91\x82\xc7\x1fvR\xe9\xaa\xac\xb5v\xee\x91\x81\x8bC\x86jg\xe2\x884\xe6\x81-\xb2\x9b\x8eP-\x99\xad|\xc4\xa1\x0eV\x10\x9f \x1c\xdb4\x82\xafI\xc7;\xdd\xc6\xeb\xdd\x1d\n\xea@\xca\xde\xb2Ek\xf0u\xd7\x01\xf3\xb4\xf6k-\x91k\xca\xff\xc6\xc9\xe6\xee\xdc\xfbF\x14\x0b*\xc2%u\xfd\xecqT\xfd\x90\x94\x01Z\xae\x87\xf7\xd2\xb0V\xbfv\xe5\x12\xf4\xe1tEI\xb1\x84\x1b`\xee\xfab\xb6\xc1\xdc+\x1f\x90\x80~\xf9\xa1\xd1\xda\xc3:\x11\x89\x17\xbe\xb5\xb6A7\xfar_\xbb\xb6<^D$\xa4E;]3\xe8\xec\xf2t\xfa\xedK\xe9F\tu \x05\xcf\x8e\xc7\x0b\x97g\xa8N`i~\xd0d(\x9a\xd3\xa6\xaf\xbb4\x15\xd5m:\x0151\xf7\xe9-@\x90Az-\'q\xebF:q\xd2:\x82\x0c\xd0r=\xa2\xa7\x89y\xcfJ\xe0d\xf3\xc1\xc1\x0c\x9a\xcb\xa0\x0b$\x8c\x0e\xc1\r\xf7w\x08;\xd7\x05\xde\xc7\xe6\xdb)\x1e\x1ctd\xbc\xb7\xa5\xaa\xe2NT3\x00\xe31bO6\xd9\xbf}\x8d\xe7\xfb8\x02\xce\xe7\xf0\xfa\x8b\xf5\x9d\xa2\x9d\xf4\xac4\x14\x9d\xa2YfN\xd1\x9e\xcf\xe2\xd48\xd1\x06\xb5\x06\xdb\xe7m\xb3\x88\xffPmA\x9b\x98s\xd3\xf5n\xf1\xd2\xf8\xda\x99\x98\xeb9\xe7T3\xcde\xa5\xa7qD}\x82 c\xd1\xb2)6\xff6\xef\x97\x87\xad}\x1d\xc1\x8d\xccx>\x07)\xea[\x1bR\x98Q\x97\xaeF\x9f\x88\x88\xfd\xf5\xc1\xc3~v\xd6\xa1\xa5\x95-F\ti\xb7%x\x1f\x958F\xb9\xca\x84\xe4U\xe2\x95\xa0\x82\xc9\xbaw\x9d\x8c\x14dr\x91%*\xc1ka\xd2\x1d\x9b@\xbf\xa5B\xa4\x1d.4\xf6\x8d\x92\xe6\xb6\x89\x11\x1c\x13\xb4h\'\xe6ie\xda!\xb6~r\xdd\x88\xe2\xb4G?\xb1\xfe\xeb\xdb\xcco?\xc5\x912@\xcb\xf5(\x0b\xda\xd4\xea\xdf[\x11\x82\xfe\x9c\x1e6\xbb\xfd\x8c%\x14\x00s\xab\x96!\xf4z\xacWA\xe5\x9a\x1bJ\xfd\x9e[\xaa\xee\x9a\xd4\x80\xd3\x92\x8f\x03@\xfb\xc0]B\xe4\xdcY\x88\x1e4\x11\xe6\xf8\xbe\x02\xcb\xb6\x81=\xb4\x8c\x0e\xc9+\xa5\xf3\x1cO\xd2\x15\x91\xc7h\xb9\xb8\x84\xb0\x0cr\xf1\xbc\xced,g+o\x06\xf4\xb9-A\x1f\xc6\xff\xf9c\xa6\xd0\xd0S-\xdeZ\xeb\x7f#\x83\x9a\xf4c%t\x94\x94\xfd\xce\xf2\xf2\xf5@qY\xe9U\xbc\x12\x8f%\xc8\x00-\xd76\xe4\xea\xab/X\xe7Ji.\xb3\xbaJ\xd9\x91\xc1\r\xf7\xb5kC\xc94\x9fp;?\x15\x9a-\xf1\xdb>\'#`\xc8\x01i\xc0d\x8c\xe0b\xbc\x1d\xd2VY\xb1\xe7sJ\xbee\x0e}d\x056\xac\xc71\xcdb\x12\x81\x19\x8a\x16Q\xfa\xaaE\x14\xd4\x81\xacug\xed\x9e~\xad@\xbbo\xb0\x18\ro0\x1d3i*b\xa8\xe7\xf5\r\xe0\xd9@\xc4\xe5\xb1-\xda\xc5\xf3\xb43\xd9\\\xec\x80X\x8a\xd3\xee4a\x99D\xd7\xe7\x12\xf5y\xfdD\x82\x0c\xd0r=B\x03{\xf2y\xc2\xd8\x9f\xb3D0\x1a\x08\x17@\xceH[D$\x19\x19(\xe6"~H\xbb\xd2%\xaa\x8b+^W\xcfY\xfa\xbd6\xe4\xd6\x19\xf5\xf47\xe0\x0f\x0c\xaf \xb7i\xcf\xf6V\xa5\x92o\x9dS\x0b\x80\xa1o\x14e\xa5\xdb\xb1\xcf\xb8G\x11\x1a\xba\x85d\x82\x0b\xcb\x0e?\xb0\xe3Y\x7fP\xaa\xb9X\x87\x90\xc7\x11\x1e%\x7f\x98\xfaP\xcf\x97\xf0\xf96&\xe6\xf4\xca\xaf\x15\xbf\xcfdQ\xfc\xfa\xe6<\xec|o\xa48d\x80\x96\xeb1\xe8\x7f\x1e\xf3y%O!n\xfd\xc0!\x8f\xb4\xdf"\xceQ\xe49nV8\xe9\xbffG\x06\x8a\xb9\xaf]\xc3f(\x0f\xac\xb9\xe2\xe8\xbb\xff^w\xb5\xc7;\'\xd4\x89\x1b\xec\xfd\xf6\x84\xe1\x00a\x90\x00\xb9\xf4\xc4F\xc52\xc7\xf7?8\xd8O\xc6\xdev$%\xcd\x99\x87\xed\xee_TH\xde\\\n\xee\xa1\x0e\xe4\xac\x8d6\xc8\xaa?xN\xb7\xfdG\xe0\xb8\xc4)\xf7\xe5y%&\xe6f%,0\xa2\xd8\x11\xb4M\xf4\xb0\xdfvJ]\xa1%e\\9\xa4\x84\xafT\xad\xaes\\[\x9d!\x922\xbf&\x15\xdc:\xb7\xfe\xa8\xb0`\xaf \xcdwj\xdfF\xe5\x9bI\xdf\xf9\xdb\xdf;\xaf\x89\xc1\x1a:_\xb7B\x17\xf6\t\xd0\xef,s|\x11\x7f\x0e\xf9"G\x8cW\x0f\x11\x1d!\xb7\xa7\xeb\xfa\xd9b)&+\t\xc8\xd5\xaf\xb3\xed*7e\xa8\xcb\xf0D=f\xb6ie\x85\xdf\xa6\x9e\xd7\xc7\xb7C\x88\xcb\xfb\xb7i\x0f6\xed\xad\xd2\x0f$x\xa7\x97\x90^k\xe2\r\xa2\xb4\xd41x\x8dzH\x01"@\xcb\xf5\xd0&\xacl\xf5\x94\x89K\xa0\x87\xd3\xa5\xa9\xc0}\xe1\x06\x98\x0b\xc7^I\xc9\xfd\xaa\x82>\x8f\xc6\x90\x85,\xb2n\x85\xfa^v>\x89Qo:\xe3W\x86\xf1\x9ciB\xff\x05g\xd7z\xa8')
    # data = data.hex()
    data_1 = bytearray(b'\x00\x00\x00\x00\x00\x00,\x00JABEO\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    print(data_1.hex())
    ret_data_unzip = zlib.decompress(data)
    print(len(ret_data_unzip))


    code = struct.unpack("<13s", bytes.fromhex('00 00 00 00 00 00 2c 00 4a 41 42 45 4f 00'))
    print(code)




# 使用示例
if __name__ == "__main__":
    # 方法1：仅查找最快主站
    # selector = TdxHostSelector()
    # host, port, results = selector.find_best_host(limit=30)  # 测试前30个
    # host, port, _ = selector.find_best_host(max_workers=10, limit=20)
    # host, port = ("113.96.40.130", 7721)  # 通达信接入主站1（已知最快）
    host, port = ("101.35.247.235", 7709)  # 通达信接入主站2（已知最快）
    # host, port = ("180.153.18.171", 7709)  # 通达信接入主站3（已知最快）
    host = '47.103.120.159'
    port = 7727

    api = TdxExHq_API(True)
    # api = TdxHq_API(False)
    api.connect(host, port)
    
    # 方法2：直接使用最快主站获取数据
    # api = connect_best_host()
    if api:
    #     # 获取深圳平安银行(000001)的实时行情
        data = api.get_instrument_bars(TDXParams.KLINE_TYPE_DAILY,33, "588200", 0, 10)  # 0=深圳, 1=上海
        print(data)
    #     # api.qh_connect_init()
    #     # data = api.get_markets()
    #     # data_pd = api.to_df(data)
    #     # data_pd.to_csv('./markets.csv', index=False, encoding='utf-8-sig')
    #     # print(data_pd)
    #     # data = api.get_instrument_count(0)
    #     # api.get_instrument_info(0, 100)
    #     # data = api.get_instrument_bars(TDXParams.KLINE_TYPE_1HOUR, 66, "SIL9", 0, 50)
    #     # print(api.to_df(data))
    #     data = api.get_security_list(74, 0)
    #     data_pd = api.to_df(data)
    #     print(data_pd)
        api.disconnect()
    # hq_test()
    # test()
    # (code, )= struct.unpack("<14s", bytes.fromhex('00 00 00 00 00 00 2c 00 4a 41 42 45 4f 00'))
    # code = code.decode("gbk")
    # print(code)
    # byte_data = bytes.fromhex('59 3c d0 4c')
    # # data = bytearray(byte_data)
    # (dbvol_raw,) = struct.unpack("<f", byte_data)
    # print(dbvol_raw)