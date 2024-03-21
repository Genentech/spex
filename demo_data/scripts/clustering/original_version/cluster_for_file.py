import glob
import os
import time
import sys

import csv
import numpy as np

import phenograph

import scipy.stats as stats

fn_in_orig = sys.argv[1]
fn_in = sys.argv[2]
fn_out = sys.argv[3]

# 30
kNN = int(sys.argv[4])

# 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27
marker_list = sys.argv[5].split(',')
markers = [int(x) for x in marker_list]

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
