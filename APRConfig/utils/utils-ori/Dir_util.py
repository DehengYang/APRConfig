import os

def get_cur_dir(file_name):
    """
    file_name: __file__
    """
    cur_dir = os.path.dirname(os.path.abspath(file_name))
    return cur_dir