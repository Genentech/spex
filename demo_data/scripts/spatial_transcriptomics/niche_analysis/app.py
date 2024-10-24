import numpy as np
import pandas as pd
import squidpy as sq
from scipy.sparse import issparse
import scanpy as sc
from anndata import AnnData
from sklearn.neighbors import KDTree
# Utilize complex numbers to vectorize permutation counts


# to not move all vitessce inside CLQ
def to_dense(arr):
    """
    Convert a sparse array to dense.

    :param arr: The array to convert.
    :type arr: np.array

    :returns: The converted array (or the original array if it was already dense).
    :rtype: np.array
    """
    if issparse(arr):
        return arr.todense()
    return arr


def to_uint8(arr, norm_along=None):
    """
    Convert an array to uint8 dtype.

    :param arr: The array to convert.
    :type arr: np.array
    :param norm_along: How to normalize the array values. By default, None. Valid values are "global", "var", "obs".
    :type norm_along: str or None

    :returns: The converted array.
    :rtype: np.array
    """
    # Re-scale the gene expression values between 0 and 255 (one byte ints).
    if norm_along is None:
        norm_arr = arr
    elif norm_along == "global":
        arr *= 255.0 / arr.max()
        norm_arr = arr
    elif norm_along == "var":
        # Normalize along gene axis
        arr = to_dense(arr)
        num_cells = arr.shape[0]
        min_along_genes = arr.min(axis=0)
        max_along_genes = arr.max(axis=0)
        range_per_gene = max_along_genes - min_along_genes
        ratio_per_gene = 255.0 / range_per_gene

        norm_arr = np.multiply(
            (arr - np.tile(min_along_genes, (num_cells, 1))),
            np.tile(ratio_per_gene, (num_cells, 1))
        )
    elif norm_along == "obs":
        # Normalize along cell axis
        arr = to_dense(arr)
        num_genes = arr.shape[1]
        min_along_cells = arr.min(axis=1)
        max_along_cells = arr.max(axis=1)
        range_per_cell = max_along_cells - min_along_cells
        ratio_per_cell = 255.0 / range_per_cell

        norm_arr = np.multiply(
            (arr.T - np.tile(min_along_cells, (num_genes, 1))),
            np.tile(ratio_per_cell, (num_genes, 1))
        ).T
    else:
        raise ValueError("to_uint8 received unknown norm_along value")
    return norm_arr.astype('u1')
# to not move all vitessce inside CLQ


def unique_perms(a):
    weight = 1j*np.arange(0,a.shape[0])
    b = a + weight[:, np.newaxis]
    u, cts = np.unique(b, return_counts=True)
    return u,cts

#Mapping functions for parallelization
def process_neighborhood(n):
    global t_perms,t_clust,tcell_perms
    ncv = np.zeros((t_perms+1,t_clust),dtype=np.float32)

    if len(n) == 0:
        return ncv

    j,cts = unique_perms(tcell_perms[:,n])
    ncv[np.imag(j).astype(np.int32),np.real(j).astype(np.int32)] = cts

    return ncv

def pool_ncvs(argperm,argclust,argcperms):
    global t_perms,t_clust,tcell_perms
    t_perms,t_clust,tcell_perms = argperm,argclust,argcperms


def cluster(adata, spatial_weight = 0.0, resolution=1.0, method='leiden'):
    #Args:
    #adata: The anndata after preprocessing and dimensionality reduction.
    #spatial_agg: Whether we include spatial neighbors in the adjacency calculation
    #resolution: The resolution of the modularity cost function. Lower is less clusters, higher is more clusters.
    #method: The method by which we cluster data. Louvain, Leiden, TODO:: spectral Louvain, spectral Leiden

    #Clustering
    adjacency = adata.obsp['connectivities']

    #Force spatial neighbors to be close.
    if spatial_weight > 0:
        if 'spatial_connectivities' in adata.obsp:
            adjacency += adata.obsp['spatial_connectivities']*spatial_weight

    #Pegasus
    #pdat = UnimodalData(adata)
    #pdat.obsp['W_pca'] = pdat.obsp['connectivities']
    #pg.cluster(pdat,algo=method)

    #Scanpy
    if method == 'leiden':
        sc.tl.leiden(adata, resolution=resolution, adjacency=adjacency)
    elif method == 'louvain':
        sc.tl.louvain(adata, resolution=resolution, adjacency=adjacency)

    return adata

def convert_df_columns_to_str(df):
    df.columns = df.columns.astype(str)
    return df

def convert_all_keys_to_str(adata):
    def convert_keys_to_str(mapping):
        return {str(key): value for key, value in mapping.items()}

    def convert_df_keys_to_str(df):
        df.columns = df.columns.astype(str)
        df.index = df.index.astype(str)
        return df

    for attr in ['obsm', 'varm', 'layers', 'obsp', 'uns']:
        mapping = getattr(adata, attr)
        converted_mapping = convert_keys_to_str(mapping)

        for key in converted_mapping:
            if isinstance(converted_mapping[key], pd.DataFrame):
                converted_mapping[key] = convert_df_keys_to_str(converted_mapping[key])

        setattr(adata, attr, converted_mapping)

    adata.obs = convert_df_keys_to_str(adata.obs)


def run(**kwargs):
    # after_phenograph_clusters on full data per image
    adata = kwargs.get('clq_adata')
    try:
        adata.obs['leiden'] = adata.obs['cluster_phenograph']
    except KeyError:
        print('not have cluster_phenograph')
    n_neighbors = kwargs.get('n_neighbors')
    resolution = kwargs.get('resolution')

    #Load neighborhoods
    ncv_dat = AnnData(adata.obsm['NCV'],obs=adata.obs)
    ncv_dat.obsm['spatial'] = adata.obsm['spatial']

    #Cluster neighborhoods
    sc.pp.neighbors(ncv_dat,n_neighbors=n_neighbors)
    ncv_dat = cluster(ncv_dat,resolution=resolution)

    #Put niche identities back into the AnnData object
    adata.obs['niche'] = ncv_dat.obs.leiden
    convert_all_keys_to_str(adata)

    return {'adata': adata}
