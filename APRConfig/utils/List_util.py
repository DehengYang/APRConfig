from utils import File_util, Dir_util

import os

def get_intersection(src_list, dst_list):
    intersection = []
    for src in src_list:
        if src in dst_list:
            intersection.append(src)
    print(f"intersection: {len(intersection)}, src: {len(src_list)} {len(intersection)/len(src_list)}, dst: {len(dst_list)}  {len(intersection)/len(dst_list)}")
    print(intersection)
    return intersection

def get_union(src_list, dst_list):
    union = []
    for src in src_list:
        union.append(src)
    for dst in dst_list:
        if dst not in union:
            union.append(dst)
    return union

def get_uniq_in_src(src_list, dst_list):
    uniq = []
    for src in src_list:
        if src not in dst_list:
            uniq.append(src)
    print_list(uniq, "uniq")
    return uniq

def print_list(list, header=""):
    print(f"{header} list info:")
    for node in list:
        print(f"{node}")

def remove_empty_strings(list):
    new_list = []
    for node in list:
        if len(node) != 0:
            new_list.append(node)
    return new_list


if __name__ == "__main__":
    cur_dir = Dir_util.get_cur_dir(__file__)
    v1_list = File_util.read_file_to_list_strip(os.path.join(cur_dir, "v1.txt"))
    v2_list = File_util.read_file_to_list_strip(os.path.join(cur_dir, "v2.txt"))
    get_uniq_in_src(v1_list, v2_list)
    get_uniq_in_src(v2_list, v1_list)