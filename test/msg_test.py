# -*- coding:utf-8 -*-
"""
date: 2026/03/17
author: Berserker
"""
import struct


def test_msg_read():
    # code = b"159125"
    # name = "港股通科技ETF招商".encode('gb18030')

    # # print(code.)
    # data1 = struct.pack("<10s", name)
    # data2 = struct.pack(">10s", name)

    # print(data1.hex())
    # print(data2.hex())

    with open("./test/cache/0_159125.msg", "rb") as file:
        data = file.read()
        n = len(data)
        upck = struct.unpack(">h", data[16:18])[0]
        print(upck)
        # print(len(data))

#   code  struct.pack("<6s", b"159125") 88-8d
#  pct_change 



if __name__ == "__main__":
    test_msg_read()
