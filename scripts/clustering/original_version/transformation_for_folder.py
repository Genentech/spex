import glob
import os
import time
import sys

import csv
import numpy as np

folder_in = sys.argv[1]
folder_out = sys.argv[2]

# 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27
marker_list = sys.argv[3].split(',')
markers = [int(x) for x in marker_list]

fn_in_list = []
fn_out_list = []

if not os.path.exists(folder_out):
    os.makedirs(folder_out)

for file in glob.glob(folder_in + '/*.csv'):
    fn_in_list.append(file)
    fn_out_list.append(folder_out + '/' + os.path.basename(file))

length = len(fn_in_list)

for i in range(length):
    fn_in = fn_in_list[i]
    fn_out = fn_out_list[i]

    with open(fn_in, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        headers = next(reader)
        data = np.array(list(reader)).astype(float)

    data_for_calc = data[:, markers]
    data_for_calc = np.arcsinh(data_for_calc / 5)
    data[:, markers] = data_for_calc

    np.savetxt(fn_out, data,
               fmt='%s',
               delimiter=',', header=','.join(headers), comments='')
    print('{0} done'.format(fn_out))
