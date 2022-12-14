import time
from datetime import datetime, timedelta

start_time = -1


def get_cur_time_str():
    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    return dt_string


def get_cur_time():
    return time.time()  # in seconds


def update_start_time():
    global start_time
    start_time = time.time()


def cal_time_cost():
    assert start_time != -1
    time_cost = time.time() - start_time
    print(f"time cost: {time_cost}s.")


def parse_time_for_hms(time_string):
    # parsed_time = time.strftime("%Y:%m:%d %H:%M:%S", time.strptime(time_string, "%H:%M:%S"))
    parsed_time = datetime.strptime(time_string, "%H:%M:%S")
    return parsed_time


def get_time_cost(src_time, dst_time):
    """
    input: parse_time_for_hms() output
    """
    timedelta = dst_time - src_time
    return timedelta.total_seconds()


def add_a_day(end_time):
    end_time = end_time + timedelta(days=1)
    return end_time