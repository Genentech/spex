import glob
import os
import time
import sys

import csv
import numpy as np

fn_in = sys.argv[1]
fn_out = sys.argv[2]

# 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27
marker_list = sys.argv[3].split(',')
markers = [int(x) for x in marker_list]

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
