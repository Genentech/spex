import glob
import os
import time
import sys

import csv
import numpy as np

import scipy.stats as stats

folder_in = sys.argv[1]
folder_out = sys.argv[2]

# 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27
marker_list = sys.argv[3].split(',')
markers = [int(x) for x in marker_list]

fn_in_list = []

if not os.path.exists(folder_out):
    os.makedirs(folder_out)

for file in glob.glob(folder_in + '/*.csv'):
    fn_in_list.append(file)

length = len(fn_in_list)

bulk_data = None
bulk_data_for_calc = None

for i in range(length):
    fn_in = fn_in_list[i]

    with open(fn_in, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        headers = next(reader)
        data = np.array(list(reader)).astype(float)

    data_for_calc = data[:, markers]
    (H, W) = data.shape
    if bulk_data_for_calc is None:
        bulk_data_for_calc = data_for_calc
    else:
        bulk_data_for_calc = np.row_stack((bulk_data_for_calc, data_for_calc))
    file_ids = [os.path.basename(fn_in)] * H
    file_ids = np.array(file_ids)
    data = np.column_stack((file_ids, data))
    if bulk_data is None:
        bulk_data = data
    else:
        bulk_data = np.row_stack((bulk_data, data))

bulk_data_for_calc = stats.zscore(bulk_data_for_calc, axis=0)
bulk_data_for_calc = np.nan_to_num(bulk_data_for_calc)

bulk_file_ids = bulk_data[:, 0]

file_ids_list = list(set(bulk_file_ids))

for file_id in file_ids_list:
    fn_out = folder_out + '/' + file_id

    data_file = bulk_data[np.where(bulk_file_ids == file_id)]
    data_file = data_file[:, 1:]

    np.savetxt(fn_out, data_file,
               fmt='%s'
               , delimiter=',', header=','.join(headers), comments='')
    print('{0} done'.format(fn_out))
