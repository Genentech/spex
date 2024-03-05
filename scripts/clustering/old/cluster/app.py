import time
import numpy as np
import phenograph


def run(**kwargs):

    fn_in_orig = kwargs.get('dataframe').to_numpy()

    if kwargs.get('transformed') is None:
        fn_in = kwargs.get('z_score')
    else:
        fn_in = kwargs.get('transformed')
    fn_out = 'test'

    # 30
    knn = int(kwargs.get('knn'))

    # 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27
    markers = kwargs.get('markers')
    if not markers:
        markers = [1, 2]
    data_orig = fn_in_orig
    data = fn_in

    data_for_calc = data[:, markers]

    t0 = time.time()
    communities, graph, q = phenograph.cluster(data_for_calc, n_jobs=1, k=knn, clustering_algo='leiden')
    labels = communities.astype(int).astype(str)
    t1 = time.time()

    print('phenograph done', t1 - t0)

    result1 = np.column_stack((data_orig, labels.astype(float)))

    return {
        'cluster': result1
    }
