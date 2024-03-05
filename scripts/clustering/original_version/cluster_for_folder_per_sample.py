import glob
import os
import time
import sys

import csv
import numpy as np

import phenograph

import scipy.stats as stats

folder_in_orig = sys.argv[1]
folder_in = sys.argv[2]
folder_out = sys.argv[3]

# 30
kNN = int(sys.argv[4])

# 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27
marker_list = sys.argv[5].split(',')
markers = [int(x) for x in marker_list]

fn_in_orig_list = []
fn_in_list = []
fn_out_list = []

if not os.path.exists(folder_out):
    os.makedirs(folder_out)

for file in glob.glob(folder_in + '/*.csv'):
    fn_in_list.append(file)
    fn_in_orig_list.append(folder_in_orig + '/' + os.path.basename(file))
    fn_out_list.append(folder_out + '/' + os.path.basename(file))

length = len(fn_in_list)

for i in range(length):
    fn_in_orig = fn_in_orig_list[i]
    fn_in = fn_in_list[i]
    fn_out = fn_out_list[i]

    with open(fn_in_orig, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        headers_orig = next(reader)
        data_orig = np.array(list(reader)).astype(float)
    with open(fn_in, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        headers = next(reader)
        data = np.array(list(reader)).astype(float)
    data_for_calc = data[:, markers]

    t0 = time.time()
    communities, graph, Q = phenograph.cluster(data_for_calc, n_jobs=1, k=kNN)
    labels = communities.astype(int).astype(str)
    t1 = time.time()
    print('phenograph done', t1 - t0)

    headers.append('cluster_id')
    result1 = np.column_stack((data_orig, labels.astype(float)))
    np.savetxt(fn_out, result1,
               fmt='%s',
               delimiter=',', header=','.join(headers), comments='')
    print('{0} done'.format(fn_out))
