# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/12 16:39:58
@Author     : apr
'''

import logging

import Defects4j
import Bears
import Bugsdotjar
import Quixbugs

logger = logging.getLogger()


class DatasetFactory():
    def create_dataset(self, dataset_name):
        if dataset_name.lower() == "defects4j":
            return Defects4j.Defects4j()
        elif dataset_name.lower() == "bears":
            return Bears.Bears()
        elif dataset_name.lower() == "bugsdotjar":
            return Bugsdotjar.Bugsdotjar()
        elif dataset_name.lower() == "quixbugs":
            return Quixbugs.Quixbugs()
        else:
            raise Exception(f"unknown dataset name: {dataset_name}")