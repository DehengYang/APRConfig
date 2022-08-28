# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/14 21:59:03
@Author     : apr
'''

import logging

import Simfix, Nopol, Arja, Tbar, Deptest

logger = logging.getLogger()


class AprFactory():
    def __init__(self) -> None:
        self.name = "apr"
        pass

    def create_apr(self, apr_name, apr_args):
        if apr_name.lower().startswith("simfix_"):
            return Simfix.Simfix(apr_args, apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("tbar_"):
            return Tbar.Tbar(apr_args, apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("nopol_"):
            return Nopol.Nopol(apr_args, "nopol", apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("dynamoth_"):
            return Nopol.Nopol(apr_args, "dynamoth", apr_name.lower().split("_")[-1])
        elif apr_name.lower() == "deptest":
            return Deptest.Deptest(apr_args, "deptest")
        # elif apr_name.lower() == "kali":
        #     return Arja.Arja(apr_args)
        else:
            raise Exception(f"unknown {self.name} name: {apr_name}")