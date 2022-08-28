# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/15 23:28:10
@Author     : apr
'''

import argparse, sys, os, time
import logging

from utils import Logging_util, Yaml_util
from dataset import Dataset_factory
from localization import Localizer_factory
from apr import Apr_factory
import Config

logger = logging.getLogger()


def get_dataset(dataset_name):
    dataset = Dataset_factory.DatasetFactory().create_dataset(dataset_name)
    return dataset


def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def run_single_bug(tool_name, dataset_name, localizer_name, dataset, bug):
    bug_name = bug.get_proj_id()
    init_args = [
        "-d", dataset_name, "-b", bug_name, "-apr", tool_name, "-localizer",
        localizer_name
    ]

    args = init_parser(init_args)
    bug = dataset.get_bug(args.bug_id)

    parent_output_dir = Config.TMP_OUTPUT_DIR
    if args.output_dir is not None:
        parent_output_dir = args['output_dir']
    """
    parent_output_dir: results
    checkout: results/pool/bug.name
    copy: results/bug.name/bug.name
    logdir: results/bug.name/x.log
    aprdir: results/bug.name/apr_name
    """
    bug_pool_dir = os.path.join(parent_output_dir, "pool", bug.name)
    make_dir(bug_pool_dir)
    bug_copy_dir = os.path.join(parent_output_dir, bug.name, bug.name)
    make_dir(bug_copy_dir)
    args.working_dir = bug_copy_dir
    # init logger
    log_dir = os.path.join(parent_output_dir, bug.name, args.apr_name)
    make_dir(log_dir)
    log_file = os.path.join(log_dir, "execution_framework.log")
    logger = Logging_util.init_logger_with_file(log_file)
    # apr_dir = os.path.join(parent_output_dir, bug.name, tool_name.lower())
   
    # dataset module
    next_args = run_dataset_module(args, dataset, bug, parent_output_dir,
                                   bug_pool_dir)

    next_args = run_fl_module(args, next_args, dataset, bug)
    
    # deptest need dataset name
    next_args['dataset_name'] = dataset_name
    next_args['fault_localizer'] = args.fault_localizer
    

    # apr
    run_apr_module(args, next_args)


def init_parser(sys_args):
    parser = argparse.ArgumentParser(
        prog="Main",
        description='Run APR tools for repairing specific bugs/datasets.')
    parser.add_argument('-d',
                        '--dataset',
                        required=True,
                        help='e.g., defects4j')
    parser.add_argument('-b', '--bug_id', required=True, help='e.g., chart_1')
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
        help='available apr tool list: [nopol, simfix, tbar, dynamoth]')
    parser.add_argument(
        '-localizer',
        '--fault_localizer',
        required=True,
        help='available localizer list: [gzoltar_v0.1.1/gzoltar]'
    )  # gzoltar_v1.7.2
    args = parser.parse_args(sys_args)
    return args


def run_dataset_module(args, dataset, bug, parent_output_dir, bug_pool_dir):
    output_dir = os.path.join(parent_output_dir, bug.name, "dataset")
    make_dir(output_dir)

    dataset.clean_dir(bug, args.working_dir) #output_dir, 
    dataset.checkout_and_compile(bug, args.working_dir, bug_pool_dir)
    dataset.execute_and_save(bug, output_dir)

    # 2) pass args
    next_args = dataset.get_next_args(bug, args, output_dir)
    dataset.compile(bug)

    return next_args


def run_fl_module(args, fl_args, dataset, bug):
    start_time = time.time()
    localizer = Localizer_factory.LocalizerFactory().create_localizer(
        args.fault_localizer, fl_args)

    output_yaml = os.path.join(localizer.outputDir, "output_data.yaml")
    if len(os.listdir(localizer.outputDir)) >0 and os.path.exists(output_yaml):
        logger.info("Localization is already done. Skip localization.")
        pass
    else:
        localizer.clean_dir()
        localizer.localize()

    next_args = localizer.get_next_args(args, dataset, bug)

    logger.info(f"time_cost_of_fl: {(time.time()-start_time)}")

    output_yaml_file = os.path.join(localizer.outputDir, "output_data.yaml")
    if os.path.exists(output_yaml_file):
        output_dict = Yaml_util.read_yaml(output_yaml_file)
        # next_args["fl_time_cost"] = "{:.4f}".format(time.time() - start_time)
        next_args["fl_time_cost"] = "{:.4f}".format(
            float(output_dict['time_cost_in_total']) -
            float(output_dict['time_cost_in_replication']))
    else:
        logger.info(f"Fault localization: output_yaml_file does not exists! ({output_yaml_file})")

    return next_args


def run_apr_module(args, apr_args):
    if "fl_time_cost" not in apr_args:
        logger.info(f"Fault localization failed. Stop repairing this bug with {args.apr_name} now.")
        return 
        
    apr = Apr_factory.AprFactory().create_apr(args.apr_name, apr_args)

    apr.clean_dir()
    apr.repair()


def dataset_init(args):
    # 1) run operations
    dataset = Dataset_factory.DatasetFactory().create_dataset(args.dataset)
    bug = dataset.get_bug(args.bug_id)

    return dataset, bug


if __name__ == "__main__":
    pass

    # # create logger first
    # # logger = Logging_util.init_logger()

    # args = init_parser(sys.argv[1:])
    # dataset, bug = dataset_init(args)
    # if args.working_dir is None:
    #     args.working_dir = Config.TMP_OUTPUT_DIR

    # # set output dir
    # parent_output_dir = os.path.join(Config.TMP_OUTPUT_DIR, bug.name)
    # if args.output_dir is not None:
    #     parent_output_dir = args['output_dir']

    # # init logger
    # log_dir = os.path.join(parent_output_dir, args.apr_name)
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)
    # log_file = os.path.join(log_dir, "execution_framework.log")
    # logger = Logging_util.init_logger_with_file(log_file)

    # # dataset module
    # next_args = run_dataset_module(args, dataset, bug)

    # next_args = run_fl_module(args, next_args, dataset, bug)

    # # apr
    # run_apr_module(args, next_args)

    # pass