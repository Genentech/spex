import numpy as np
import pandas as pd
import squidpy as sq
from scipy.sparse import issparse
from anndata import AnnData
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

#Optimized CLQ using vectorized operations
def CLQ_vec(adata, clust_col='leiden', clust_uniq=None, radius=50, n_perms=1000):
    # Calculate spatial neighbors once.
    # adata.obsm['spatial'] = adata.obs[['x_coordinate', 'y_coordinate']].to_numpy()
    radius = float(radius)
    sq.gr.spatial_neighbors(adata, coord_type='generic', radius=radius)
    neigh_idx = adata.obsp['spatial_connectivities'].tolil()
    neighborhoods = [x + [i] for i, x in
                     enumerate(neigh_idx.rows)]  # Append self to match previous implementation? (x + [i])

    # Global frequencies.
    global_cluster_freq = adata.obs[clust_col].value_counts(normalize=True)
    if clust_uniq is not None:
        null_clusters = global_cluster_freq.index.difference(pd.Index(clust_uniq))
        for c in null_clusters:
            global_cluster_freq[c] = 0


    # Cluster identities for each cell
    cell_ids = adata.obs.loc[:, clust_col]

    # Map clusters to integers for fast vectorization in numpy
    label_dict = {x: i for i, x in enumerate(global_cluster_freq.index)}
    n_clust = len(label_dict)

    # Permute cluster identities across cells
    cell_id_perms = [[label_dict[x] for x in cell_ids]]  # 0th permutation is the observed NCV
    cell_id_perms.extend([[label_dict[x] for x in np.random.permutation(cell_ids)] for i in range(n_perms)])
    cell_id_perms = np.array(cell_id_perms)

    # Calculate neighborhood content vectors (NCVs) sequentially.
    ncv = np.zeros((n_perms+1, len(neighborhoods), n_clust), dtype=np.float32)
    for i, n in enumerate(neighborhoods):
        if len(n) == 0:
            continue
        j, cts = unique_perms(cell_id_perms[:, n])
        ncv[np.imag(j).astype(np.int32), i, np.real(j).astype(np.int32)] = cts

    norm_ncv = ncv / (ncv.sum(axis=2)[:, :, np.newaxis] + 1e-99)

    # Read out local CLQ from NCV vectors
    local_clq = norm_ncv / np.array([global_cluster_freq[x] for x in label_dict])

    # Average local_clq over clusters to get global CLQ
    global_clq = np.array(
        [np.nanmean(local_clq[cell_id_perms == label_dict[x], :].reshape(n_perms + 1, -1, n_clust), 1) for x in
         label_dict])

    #Read out the observed local and global CLQs
    idx = [x for x in label_dict]
    lclq = pd.DataFrame(local_clq[0, :, :], columns=idx, index=adata.obs_names)
    gclq = pd.DataFrame(global_clq[:, 0, :], index=idx, columns=idx)
    ncv = pd.DataFrame(ncv[0, :, :], index=adata.obs_names, columns=idx)

    # Permutation test
    clq_perm = (global_clq[:, 1:, :] < global_clq[:, 0, :].reshape(n_clust, -1, n_clust)).sum(1) / n_perms
    clq_perm = pd.DataFrame(clq_perm, index=idx, columns=idx)

    adata.obsm['NCV'] = ncv
    adata.obsm['local_clq'] = lclq
    #colormap by this column 'local_clq' expression'
    adata.obs[clust_col] = adata.obs[clust_col].astype(str)

    adata.uns['CLQ'] = {'global_clq': gclq, 'permute_test': clq_perm}
    obs = pd.DataFrame(index=adata.obs[clust_col].unique(), columns=[], data=[])
    var = pd.DataFrame(index=adata.obs[clust_col].unique(), columns=[], data=[])

    bdata = AnnData(
        obs=obs,
        var=var
    )

    bdata.uns['local_clq'] = lclq
    bdata.layers['global_clq'] = gclq
    bdata.layers['permute_test'] = clq_perm

    return bdata, adata


def run(**kwargs):
    adata = kwargs.get('adata')
    clust_col = adata.obs.columns[-1]
    obs_df = adata.obs[clust_col]
    cluster_uniq = obs_df.unique()

    radius = kwargs.get('radius')
    n_perms = kwargs.get('n_perms')

    # Process the combined data
    processed_adata, adata = CLQ_vec(adata, clust_col, cluster_uniq, radius, n_perms)

    # Split the processed data into separate Anndata objects
    adatas_dict = {}
    for filename in adata.obs['filename'].unique():
        adata_per_file = adata[adata.obs['filename'] == filename].copy()
        adatas_dict[filename] = adata_per_file

    return {
        'adata': processed_adata,  # The combined processed data
        'clq_adata': adata,                  # The combined data with CLQ results
        'adatas_dict': adatas_dict           # Dictionary of separate Anndata objects per file
    }
