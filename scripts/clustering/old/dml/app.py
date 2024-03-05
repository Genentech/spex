import os
import pickle
import shutil
import time
import numpy as np
import umap
import hdbscan


def run(**kwargs):

    cluster = kwargs.get("cluster")
    z_score = kwargs.get("z_score")

    data_storage = kwargs.get('data_storage')  # , 'C:\\temp\\DATA_STORAGE'
    related_task = kwargs.get('related_task')  # "348554471")
    related_parent = kwargs.get('related_parent')

    def load_related_data():
        path = os.path.join(data_storage, "jobs", related_task, related_parent, "result.pickle")
        file_path = os.path.join(os.path.dirname(__file__), "related_data.pickle")
        if not os.path.isfile(path):
            return {}
        else:
            shutil.copyfile(
                path,
                file_path,
            )
            with open(file_path, "rb") as infile:
                data = pickle.load(infile)
                return data
    # 30
    n_neighbors = int(kwargs.get("knn"))
    # 0.3
    min_dist = float(kwargs.get("min_dist"))
    related_data = load_related_data()

    test_data_orig = np.array(list(related_data.get('transformed', []))).astype(float)
    test_data_zscore = np.array(list(related_data.get('z_score', []))).astype(float)
    if len(test_data_zscore) == 0:
        test_data_zscore = test_data_orig

    # 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27
    # marker_list = sys.argv[9].split(',')
    # markers = [int(x) for x in marker_list]
    markers = kwargs.get("markers")
    if not markers:
        markers = [1, 2]

    print(cluster)
    print(z_score)

    print(n_neighbors)
    print(min_dist)
    print(markers)

    length = 1
    # Переворачиваем массив т.е. колонку с кластерами в строку
    train_labels = cluster[:, -1]  # cluster_id in one row
    # обрезаем колонку
    cluster = cluster[:, :-1]  # without cluster column
    train_data_for_calc = z_score[:, markers]  # тут мы выводим данные z_score без координат, чисто по каналам
    t1 = time.time()
    # передаем в маппер строку со спискеом кластер id
    # передаем в маппер массив данных по каналам без координат
    min_dist = 0.5
    n_neighbors = 50

    mapper = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, random_state=42).fit(
        X=train_data_for_calc,
        y=train_labels
    )
    t2 = time.time()
    print("training umap done ", t2 - t1)

    result1 = np.column_stack(
        (cluster, mapper.embedding_, train_labels.astype(float))
    )

    # fig, ax = plt.subplots(1, figsize=(14, 10))
    # embedding = mapper.embedding_
    # plt.scatter(*embedding.T, s=0.1, cmap='Spectral', alpha=1.0)
    # cbar = plt.colorbar(boundaries=list(set(train_labels)))
    # cbar.set_ticks(list(set(train_labels)))
    # plt.show()

    (H, W) = cluster.shape
    res = {'dml': result1}

    print("training done")

    for i in range(length):

        test_data_for_calc = test_data_zscore[:, markers]
        test_embedding = mapper.transform(test_data_for_calc)
        test_labels = hdbscan.HDBSCAN(min_samples=10, min_cluster_size=50).fit_predict(
            test_embedding
        )

        result2 = np.column_stack((test_data_orig, test_embedding, test_labels))


        res.update({f'dml_{i}': result2})

    return res
