# coding=utf-8

from tools.pytdx.parser.base import BaseParser
from tools.pytdx.helper import get_datetime, get_volume, get_price
from collections import OrderedDict
import six
import struct

class GetQuoteBars(BaseParser):
    """_summary_ setParams()
        0000   24 06 f2 1d ce 6e 18 31 bf bc ba 54 08 00 45 00   $....n.1...T..E.
        0010   00 68 aa 85 40 00 80 06 00 00 c0 a8 01 d2 3a fa   .h..@.........:.
        0020   b3 0b 91 35 1e 29 85 c1 11 83 bf 7c e0 87 50 18   ...5.).....|..P.
        0030   00 ff b0 da 00 00 
        						 01 47 08 d8 01 01 36 00 36 00   .......G....6.6.
        0040   89 24 
        			 1e 
        			    41 55 4c 38 00 00 00 00 00 00 00 00 00   .$.AUL8.........
        0050   00 00 00 00 00 00 00 00 00 00 
        									 02 00 
        										   01 00 
        												 00 00   ................
        0060   00 00 
        			 a4 01 00 00 
        						 00 00 00 00 00 00 00 00 00 00   ................
        0070   00 00 00 00 00 00                                 ......
    """

    """_summary_ parseResponse()
    count=3 data=127
    0000   18 31 bf bc ba 54 24 06 f2 1d ce 6e 08 00 45 00   .1...T$....n..E.
    0010   00 a7 a5 ae 40 00 31 06 a0 f8 3b 24 05 0c c0 a8   ....@.1...;$....
    0020   01 d2 1e 29 d2 3d 32 e8 62 9c d0 06 de f3 50 18   ...).=2.b.....P.
    0030   00 e5 6c bb 00 00 
                             b1 cb 74 00 11 46 08 d8 01 00   ..l.....t..F....
    0040   89 24 6f 00 8a 00 78 9c 93 73 0c f5 b1 64 c0 04   .$o...x..s...d..
    0050   2c 0c 8c 28 7c 66 86 23 ea a6 8c 22 7c b1 2e eb   ,..(|f.#..."|...
    0060   d4 e3 5c 66 ed 8c 76 61 78 10 eb 32 b7 86 85 61   ..\f..vax..2...a
    0070   0d 17 33 03 48 fc 28 50 be d5 3b ce e5 fa e3 64   ..3.H.(P..;....d
    0080   97 75 c7 63 5d 1e de 4a 76 99 f5 94 85 c1 ac 8e   .u.c]..Jv.......
    0090   95 41 3e 35 c1 e5 18 50 be 5f 29 c5 c5 63 61 96   .A>5...P._)..ca.
    00a0   0b 88 de 51 97 e1 32 43 80 95 81 6f 36 1b d8 06   ...Q..2C...o6...
    00b0   00 d8 56 20 24                                    ..V $

    count=1 data=90
    0000   18 31 bf bc ba 54 24 06 f2 1d ce 6e 08 00 45 00   .1...T$....n..E.
    0010   00 82 ad 35 40 00 31 06 99 96 3b 24 05 0c c0 a8   ...5@.1...;$....
    0020   01 d2 1e 29 d4 58 60 c7 3e 99 08 c9 bc b7 50 18   ...).X`.>.....P.
    0030   00 e5 24 71 00 00 
                             b1 cb 74 00 01 46 08 d8 01 00   ..$q....t..F....
    0040   89 24 4a 00 4a 00 1e 41 55 4c 39 00 00 00 00 00   .$J.J..AUL9.....
    0050   00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 00   ................
    0060   01 00 00 00 00 00 00 00 00 00 00 00 00 00 
                                                     01 00   ................
    
    0070   c6 27 35 01 8f 22 64 44 48 a1 6a 44 8f 22 64 44   .'5.."dDH.jD."dD
    0080   9a 99 68 44 eb 10 05 00 a1 a6 06 
                                            00 00 00 00 00   ..hD............

    
    '1e     41 55 4c 39 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    04 00       01 00   00 00 00 00 00 00 00 00 00 00 00 00      01 00       c6 27 35 01 8f 22 64 44 48 a1 6a 44 8f 22 64 44 9a 99 68 44 eb 10 05 00 a1 a6 06 00  00 00 00 00'

    quote: 28

    """

    def setup(self):
        pass
        #self.client.send(bytearray.fromhex('01 01 08 6a 01 01 16 00 16 00'))

    def setParams(self, category, market, code, start, count):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        pkg = bytearray.fromhex('01 46 08 d8 01 01 36 00 36 00')
        pkg.extend(bytearray.fromhex("89 24"))     
        pkg.extend(struct.pack('<B23sHHII', market, code, category, 1, start, count))
        pkg.extend(bytearray.fromhex("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        self.send_pkg = pkg
        self.category = category

    def parseResponse(self, body_buf):
        pos = 0

        (market, code) = struct.unpack("<B23s", body_buf[0: 24])
        pos += 40
        (ret_count, ) = struct.unpack('<H', body_buf[pos: pos+2])
        pos += 2

        klines = []

        for i in range(ret_count):
            year, month, day, hour, minute, pos = get_datetime(self.category, body_buf, pos)
            (open, high, low, close, position, trade, price) = struct.unpack("<ffffIIf", body_buf[pos: pos+28])
            if market in [31,27,71]: #HK
                (amount, ) = struct.unpack("f", body_buf[pos+16: pos+16+4])
                position = 0
            else:
                amount = position


            pos += 28
            kline = OrderedDict([
                ("open", open),
                ("high", high),
                ("low", low),
                ("close", close),
                ("position", position),
                ("trade", trade),
                ("price", price),
                ("year", year),
                ("month", month),
                ("day", day),
                ("hour", hour),
                ("minute", minute),
                ("datetime", "%d-%02d-%02d %02d:%02d" % (year, month, day, hour, minute)),
                ("amount", amount)
            ])


            klines.append(kline)

        return klines

