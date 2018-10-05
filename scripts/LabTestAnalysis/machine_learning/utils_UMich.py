

def filter_nondigits(any_str):
    return ''.join([x for x in str(any_str) if x in '.0123456789'])

def filter_range(any_str): # contains sth like range a-b
    nums = any_str.strip().split('-')
    try:
        return (float(nums[0])+float(nums[1]))/2.
    except:
        return any_str

def remove_microsecs(any_str):
    try:
        return any_str.split('.')[0]
    except:
        return any_str

def line_str2list(line_str, skip_first_col=False):
    # Get rid of extra quotes
    if skip_first_col:
        # get rid of meaningless first col index
        return [x.strip()[1:-1] for x in line_str.split('|')][1:]
    else:
        return [x.strip()[1:-1] for x in line_str.split('|')]

import numpy as np
import random, string

def perturb_str(any_str, seed=None): #TODO: seeding
    str_len = len(any_str)
    ind_to_perturb = np.random.choice(str_len)
    chr_to_perturb = random.choice(string.letters + '-0123456789')
    any_str = any_str[:ind_to_perturb] + chr_to_perturb + any_str[ind_to_perturb+1:]
    return any_str

def perturb_a_file(raw_file, target_file, col_patid, my_dict):
    with open(raw_file) as fr:
        lines_raw = fr.readlines()
        fr.close()

    import os
    if not os.path.exists(target_file):
        fw = open(target_file,'w')
        fw.write(lines_raw[0]) # column name line
    else:
        fw = open(target_file,'a')
    for line_raw in lines_raw[1:]:
        line_as_list = line_str2list(line_raw)
        try:
            cur_pat_id = line_as_list[col_patid]
        except:
            # print 'raw_file:', raw_file
            # print 'line_as_list:', line_as_list
            # print 'col_patid:', col_patid
            continue

        perturbed_patid = my_dict[cur_pat_id]
        line_as_list[col_patid] = perturbed_patid # perturbing pat_id
        line_as_list = ["\"" + x + "\"" for x in line_as_list]
        line_perturbed = "|".join(line_as_list)
        line_perturbed += '\n'

        fw.write(line_perturbed)