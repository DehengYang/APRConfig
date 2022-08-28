import time

start_time = -1

def get_cur_time():
    return time.time() # in seconds

def update_start_time():
    global start_time
    start_time = time.time()

def cal_time_cost():
    assert start_time != -1
    time_cost = time.time() - start_time
    print(f"time cost: {time_cost}s.")