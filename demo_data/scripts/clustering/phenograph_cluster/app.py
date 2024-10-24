import phenograph
import anndata as ad
import re
from anndata import AnnData
import dill as pickle
import scanpy as sc
from scipy.stats import zscore
from scipy.stats.mstats import winsorize
import numpy as np
import pandas as pd


def parse_channel_list(channel_list, all_channels):

    new_all_channels = []
    for item in all_channels:
        if isinstance(item, str):
            item = re.sub("[^0-9a-zA-Z]", "", item).lower().replace("target", "")
        new_all_channels.append(item)

    new_channel_list = []
    for item in channel_list:
        if isinstance(item, str):
            item = re.sub("[^0-9a-zA-Z]", "", item).lower().replace("target", "")
        new_channel_list.append(item)

    channel_list_int = [
        new_all_channels.index(new_channel_list)
        for channel in channel_list
        if channel in all_channels
    ]
    if not channel_list_int:
        channel_list_int = new_channel_list

    return channel_list_int, all_channels


def get_absolute_relative(path_, absolute=True, ds=''):
    if absolute:
        return path_.replace('%DATA_STORAGE%', ds)
    else:
        return path_.replace(ds, '%DATA_STORAGE%')


def extract_image_id(path):
    pattern = re.compile(r'[\/\\]originals[\/\\](\d+)[\/\\]image\.tiff')
    match = pattern.search(path)
    if match:
        return match.group(1)
    else:
        return None


def phenograph_cluster(
        adata,
        knn,
        markers,
        transformation='arcsin',
        scaling='z-score',
        cofactor=5,
):
    expdf = adata.to_df()  # Get this anndata from feature extraction output or spex load file input

    data_for_calc = expdf.iloc[:, markers]  # marker selection in spex UI
    # data_for_calc = expdf.copy()

    # Dropdown selection for transformation. Options are 'arcsin', 'log', 'none'
    if transformation == 'arcsin':
        data_for_calc = np.arcsinh(data_for_calc / cofactor)
    if transformation == 'log':
        data_for_calc = data_for_calc.apply(lambda x: np.log10(x) if np.issubdtype(x.dtype, np.number) else x)

    # Dropdown selection for scaling. Options are 'z-score', 'winsorize', 'none'
    if scaling == 'z-score':
        data_for_calc = data_for_calc.apply(zscore)
    if scaling == 'winsorize':
        arr_data_frame_winsorized = winsorize(data_for_calc.to_numpy(), limits=(0, .01)).data
        data_for_calc.iloc[:, :] = arr_data_frame_winsorized

    # knn value selection from spex ui
    communities, graph, Q = phenograph.cluster(
        data_for_calc.values.tolist(),
        k=knn,
        clustering_algo='leiden'
    )

    bdata = ad.AnnData(data_for_calc)
    sc.pp.neighbors(bdata, n_neighbors=knn)
    sc.tl.umap(bdata, min_dist=0.5)
    adata.obsm['X_umap'] = bdata.obsm['X_umap']

    adata.obs['cluster_phenograph'] = [str(i) for i in communities]

    return adata


def combine_ann_data(fe_data):
    all_adatas = []
    all_obs_data = []
    for key, value in fe_data.items():
        adata = value.get('adata')

        im_id = value.get('im_id')

        if adata is not None and im_id is not None:
            adata.obs['image_id'] = [im_id] * adata.n_obs
            all_adatas.append(adata)
            all_obs_data.append(adata.obs)

    if len(all_adatas) > 0:
        combined_obs = pd.concat([adata.obs for adata in all_adatas])
        combined_X = np.vstack([adata.X for adata in all_adatas])
        combined_var = all_adatas[0].var
        combined_adata = AnnData(X=combined_X, obs=combined_obs, var=combined_var)

        return combined_adata
    else:
        return None


def run(**kwargs):
    adata = kwargs.get('adata')
    scaling = kwargs.get('scaling')
    transformation = kwargs.get('transformation')
    cofactor = kwargs.get('cofactor', 5)
    knn = kwargs.get('knn')
    channel_list, all_channels = parse_channel_list(kwargs.get("channel_list", []), kwargs.get("all_channels", []))
    if not channel_list:
        channel_list = list(range(len(all_channels)))

    if len(channel_list) > 0:
        channel_list: list[int] = [
            all_channels.index(channel)
            for channel in channel_list
            if channel in all_channels
        ]
    else:
        channel_list = list(range(len(all_channels)))

    feature_extraction_tasks = kwargs.get('tasks_list', '')
    fe_data = {}
    for task in feature_extraction_tasks:
        filename = get_absolute_relative(task.get('result', ''), True, ds=kwargs.get('data_storage', ''))
        try:
            with open(filename, "rb") as outfile:
                current_file_data = pickle.load(outfile)
                im_id = extract_image_id(current_file_data.get('image_path', ''))
                fe_data = {**fe_data, task.get('_key'): {**current_file_data, 'im_id': im_id}}
        except (FileNotFoundError, PermissionError) as e:
            print(e)
            continue

    combined_adata = combine_ann_data(fe_data)

    adata = phenograph_cluster(
        combined_adata,
        knn,
        markers=channel_list,
        scaling=scaling,
        transformation=transformation,
        cofactor=cofactor
    )

    return {'adata': adata}
