# -*- coding:utf-8 -*-
"""
date: 2020/8/11
author: Berserker
"""

import os
import configparser


class XConfigParser(configparser.ConfigParser):

    def __init__(self, defaults=None):
        super(XConfigParser, self).__init__(defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


class IniFileReader(object):

    def __init__(self, file_name, encoding='gb18030'):
        self.ini_file = XConfigParser()
        self.ini_file.read(file_name, encoding=encoding)
        self.sections_options = {}
        self.ini_infos = {}
        sections = self.ini_file.sections()
        for sec in sections:
            options = self.ini_file.options(sec)
            self.sections_options[sec] = options

    def get_sections_options(self, section):
        return self.sections_options[section]

    def get_ini_infos(self, section):
        ret_list = []
        for option in self.sections_options[section]:
            value = self.ini_file.get(section, option)
            key_value = {option: value}
            ret_list.append(key_value)
        return ret_list

    def get_option_values(self, section, option):
        value = self.ini_file.get(section, option)
        return value


def main():
    reader = IniFileReader('./database/file/industry.ini')
    info_list = reader.get_ini_infos('name')
    print(info_list)