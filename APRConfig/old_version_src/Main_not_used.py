# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/15 23:28:10
@Author     : apr
'''

import argparse, sys, os, time

from utils import Logging_util
from dataset import Dataset_factory
from localization import Localizer_factory
from apr import Apr_factory
import Config


def init_parser(sys_args):
    parser = argparse.ArgumentParser(prog="dataset.main.py",
                                     description='Process datasets.')

    # dataset module
    parser.add_argument('-d',
                        '--dataset',
                        required=True,
                        help='e.g., defects4j')
    parser.add_argument('-b', '--bug_id', required=True, help='e.g., chart_1')
    parser.add_argument('-w',
                        '--working_dir',
                        required=False,
                        help='e.g., ~/test')
    parser.add_argument('-od',
                        '--output_dir',
                        required=False,
                        help='output folder to save execution results.')
    parser.add_argument('-timeout',
                        '--timeout',
                        required=False,
                        help='repair time budget (in minutes)')
    parser.add_argument(
        '-apr',
        '--apr_name',
        required=True,
        #TODO
        help='available apr tool list: [nopol]')

    # fl module
    parser.add_argument(
        '-localizer',
        '--fault_localizer',
        required=True,
        help='available localizer list: [gzoltar_v0.1.1/gzoltar]'
    )  # gzoltar_v1.7.2

    args = parser.parse_args(sys_args)
    return args


def run_dataset_module(args, dataset, bug):
    output_dir = os.path.join(Config.TMP_OUTPUT_DIR, bug.name, "dataset")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    dataset.clean_dir(output_dir, bug, args)
    dataset.execute_and_save(bug, args, output_dir)

    # 2) pass args
    next_args = dataset.get_next_args(bug, args, output_dir)

    return next_args


def run_fl_module(args, fl_args, dataset, bug):
    start_time = time.time()
    localizer = Localizer_factory.LocalizerFactory().create_localizer(
        args.fault_localizer, fl_args)

    localizer.clean_dir()
    localizer.localize()

    next_args = localizer.get_next_args(args, dataset, bug)

    logger.info(f"time_cost_of_fl: {(time.time()-start_time)}")
    next_args["fl_time_cost"] = "{:.4f}".format(time.time() - start_time)

    return next_args


def run_apr_module(args, apr_agrs):
    apr = Apr_factory.AprFactory().create_apr(args.apr_name, apr_agrs)
    
    apr.clean_dir()
    apr.repair()


def dataset_init(args):
    # 1) run operations
    dataset = Dataset_factory.DatasetFactory().create_dataset(args.dataset)
    bug = dataset.get_bug(args.bug_id)

    return dataset, bug


if __name__ == "__main__":
    # create logger first
    # logger = Logging_util.init_logger()

    args = init_parser(sys.argv[1:])
    dataset, bug = dataset_init(args)
    if args.working_dir is None:
        args.working_dir = Config.TMP_OUTPUT_DIR

    # set output dir
    parent_output_dir = os.path.join(Config.TMP_OUTPUT_DIR, bug.name)
    if args.output_dir is not None:
        parent_output_dir = args['output_dir']

    # init logger
    log_dir = os.path.join(parent_output_dir, args.apr_name)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "execution_framework.log")
    logger = Logging_util.init_logger_with_file(log_file)

    # dataset module
    next_args = run_dataset_module(args, dataset, bug)

    next_args = run_fl_module(args, next_args, dataset, bug)

    # apr
    run_apr_module(args, next_args)

    pass