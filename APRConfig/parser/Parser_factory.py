# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/14 21:59:03
@Author     : apr
'''

import logging

import Simfix_parser, Nopol_parser

logger = logging.getLogger()


class ParserFactory():
    def __init__(self) -> None:
        self.name = "parser"
        pass

    def create_parser(self, apr_name, apr_dir):
        if apr_name.lower().startswith("simfix_"):
            return Simfix_parser.SimfixParser(apr_dir, apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("tbar_"):
            return Simfix_parser.SimfixParser(apr_dir, apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("nopol_"):
            return Nopol_parser.NopolParser("nopol", apr_dir, apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("dynamoth_"):
            return Nopol_parser.NopolParser("dynamoth", apr_dir, apr_name.lower().split("_")[-1])
        # elif apr_name.lower() == "kali":
        #     return Arja.Arja(apr_args)
        else:
            raise Exception(f"unknown {self.name} name: {apr_name}")