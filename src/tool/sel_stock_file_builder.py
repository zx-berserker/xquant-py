# -*- encoding:utf-8 -*-
"""
date: 2020/8/26
author: Berserker
"""
import os
from pathlib import *
import struct


class SelStockFileBuilder(object):
    flex_sz_bytes = struct.pack('>H', 0x0721)
    flex_sh_bytes = struct.pack('>H', 0x0711)

    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.sz_stock_code = []
        self.sh_stock_code = []

    def append_stock_code(self, stock_code):
        code_list = stock_code.split('.')
        if code_list[0] == 'sh':
            self.sh_stock_code.append(code_list[1])
        elif code_list[0] == 'sz':
            self.sz_stock_code.append(code_list[1])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.path:
            self.path = os.getcwd()
        else:
            path = Path(self.path)
            if not path.exists():
                os.makedirs(self.path, 0o755)
        if not self.name:
            self.name = 'temp'

        name = self.name + '.sel'
        full_name = str(PureWindowsPath(self.path, name))
        with open(full_name, 'wb+', False) as writer:
            length = len(self.sz_stock_code) + len(self.sh_stock_code)
            length_bytes = struct.pack('H', length)
            writer.write(length_bytes)
            for code in self.sh_stock_code:
                writer.write(self.flex_sh_bytes)
                code_bytes = bytes(code, encoding="utf-8")
                writer.write(code_bytes)
            for code in self. sz_stock_code:
                writer.write(self.flex_sz_bytes)
                code_bytes = bytes(code, encoding="utf-8")
                writer.write(code_bytes)


def main():
    with SelStockFileBuilder('.', 'test') as builder:
        for i in range(0, 32):
            builder.append_stock_code("sz.000001")
            builder.append_stock_code("sh.600001")


