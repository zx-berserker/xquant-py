# coding=utf-8

from tools.pytdx.parser.base import BaseParser
from tools.pytdx.helper import get_datetime, get_volume, get_price
from collections import OrderedDict
import struct


class ExSetupCmd1(BaseParser):

    def __init__(self, client, lock=None):
        super(ExSetupCmd1, self).__init__(client, lock=None)

    def setup(self):
        self.send_pkg = bytearray.fromhex("01 01 48 65 00 01 52 00 52 00 54 24 1f 32 c6 e5"
                                            "d5 3d fb 41 1f 32 c6 e5 d5 3d fb 41 1f 32 c6 e5"
                                            "d5 3d fb 41 1f 32 c6 e5 d5 3d fb 41 1f 32 c6 e5"
                                            "d5 3d fb 41 1f 32 c6 e5 d5 3d fb 41 1f 32 c6 e5"
                                            "d5 3d fb 41 1f 32 c6 e5 d5 3d fb 41 cc e1 6d ff"
                                            "d5 ba 3f b8 cb c5 7a 05 4f 77 48 ea")

    def parseResponse(self, body_buf):
        pass

class ExSetupCmd2(BaseParser):

    def __init__(self, client, lock=None):
        super(ExSetupCmd2, self).__init__(client, lock)


    def setup(self):
        self.send_pkg = bytearray.fromhex("01 01 48 65 00 01 52 00 52 00 54 24 fc f0 0e 92 f3 c8 37 83 1f 32 c6 e5 d5 3d fb 41 cd 9c f2 07 fc d0 3c f6 f2 f7 a4 77 47 83 1d 59 c5 1f 77 82 0c 13 62 d0 a2 cd ac a7 78 a0 a1 92 1f 32 c6 e5 d5 3d fb 41 1f 32 c6 e5 d5 3d fb 41 61 ca 5b fe bc e9 ee 9b 33 5a 16 e4 ce 17 c1 bb")

    def parseResponse(self, body_buf):
        pass