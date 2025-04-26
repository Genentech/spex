import numpy as np
import pandas as pd
from anndata import AnnData
import squidpy as sq
from numba import njit, prange
import time

@njit(parallel=True, fastmath=True)
def _count_neighborhood_vectors(indices, indptr, cell_types, n_clust):
    n_cells = indptr.shape[0] - 1
    result = np.zeros((n_cells, n_clust), dtype=np.float32)

    for i in prange(n_cells):
        start, end = indptr[i], indptr[i+1]
        neighbors = indices[start:end]

        if len(neighbors) > 0:
            for neighbor in neighbors:
                cell_type = cell_types[neighbor]
                result[i, cell_type] += 1

    return result

@njit(parallel=True)
def _calculate_global_clq(local_clq, cell_types, n_clust):
    global_clq = np.zeros((n_clust, n_clust), dtype=np.float32)

    for cell_type in prange(n_clust):
        count = 0
        sum_values = np.zeros(n_clust, dtype=np.float32)

        for cell in range(local_clq.shape[0]):
            if cell_types[cell] == cell_type:
                sum_values += local_clq[cell]
                count += 1

        if count > 0:
            global_clq[cell_type] = sum_values / count

    return global_clq

def CLQ_vec_numba(adata, clust_col='leiden', clust_uniq=None, radius=50, n_perms=1000):
    start_time = time.time()

    # Preprocess spatial neighbors
    radius = float(radius)
    sq.gr.spatial_neighbors(adata, coord_type='generic', radius=radius)
    neigh_idx = adata.obsp['spatial_connectivities'].tocsr()
    indices = neigh_idx.indices.astype(np.int32)
    indptr = neigh_idx.indptr.astype(np.int32)

    # Map and prepare cell types
    global_cluster_freq = adata.obs[clust_col].value_counts(normalize=True)
    label_dict = {x: i for i, x in enumerate(global_cluster_freq.index)}
    n_clust = len(label_dict)
    n_cells = adata.shape[0]
    cell_types = np.array([label_dict[x] for x in adata.obs[clust_col]], dtype=np.int32)

    # Calculate observed neighborhood vectors and local CLQ
    observed_ncv = _count_neighborhood_vectors(indices, indptr, cell_types, n_clust)
    neighborhood_sizes = np.sum(observed_ncv, axis=1, keepdims=True)
    norm_ncv = np.divide(observed_ncv, neighborhood_sizes, out=np.zeros_like(observed_ncv), where=neighborhood_sizes > 0)
    global_freqs = np.array([global_cluster_freq[x] for x in label_dict])
    global_freqs_adj = np.where(global_freqs > 0, global_freqs, 1.0)
    local_clq = norm_ncv / global_freqs_adj

    # Calculate observed global CLQ
    global_clq = _calculate_global_clq(local_clq, cell_types, n_clust)

    # Initialize permutation test results
    permute_counts = np.zeros((n_clust, n_clust), dtype=np.int32)

    # Process permutations in batches
    batch_size = 100  # Adjust batch size based on available memory and performance
    for batch_start in range(0, n_perms, batch_size):
        batch_end = min(batch_start + batch_size, n_perms)
        for perm in range(batch_start, batch_end):
            permuted_cell_types = np.random.permutation(cell_types)
            permuted_ncv = _count_neighborhood_vectors(indices, indptr, permuted_cell_types, n_clust)
            perm_neighborhood_sizes = np.sum(permuted_ncv, axis=1, keepdims=True)
            perm_norm_ncv = np.divide(permuted_ncv, perm_neighborhood_sizes, out=np.zeros_like(permuted_ncv), where=perm_neighborhood_sizes > 0)
            perm_local_clq = perm_norm_ncv / global_freqs_adj

            # Calculate global CLQ for this permutation
            perm_global_clq = _calculate_global_clq(perm_local_clq, permuted_cell_types, n_clust)

            # Update permutation counts
            for cell_type in range(n_clust):
                permute_counts[cell_type] += (perm_global_clq[cell_type] < global_clq[cell_type]).astype(np.int32)

    # Normalize permutation counts
    clq_perm = permute_counts / n_perms

    # Prepare results
    idx = list(label_dict.keys())
    lclq = pd.DataFrame(local_clq, columns=idx, index=adata.obs_names)
    gclq_df = pd.DataFrame(global_clq, index=idx, columns=idx)
    ncv_df = pd.DataFrame(observed_ncv, index=adata.obs_names, columns=idx)
    clq_perm_df = pd.DataFrame(clq_perm, index=idx, columns=idx)

    # Store results
    adata.obsm['NCV'] = ncv_df
    adata.obsm['local_clq'] = lclq
    adata.obs[clust_col] = adata.obs[clust_col].astype(str)
    adata.uns['CLQ'] = {'global_clq': gclq_df, 'permute_test': clq_perm_df}

    # Create output AnnData object
    obs = pd.DataFrame(index=adata.obs[clust_col].unique(), columns=[], data=[])
    var = pd.DataFrame(index=adata.obs[clust_col].unique(), columns=[], data=[])

    bdata = AnnData(obs=obs, var=var)
    bdata.layers['global_clq'] = gclq_df
    bdata.layers['permute_test'] = clq_perm_df

    return bdata, adata


def run(**kwargs):
    print("Running CLQ vectorization...v2")
    adata = kwargs.get('adata')
    clust_col = adata.obs.columns[-1]
    obs_df = adata.obs[clust_col]
    cluster_uniq = obs_df.unique()

    radius = kwargs.get('radius')
    n_perms = kwargs.get('n_perms')

    # Process the combined data
    processed_adata, adata = CLQ_vec_numba(adata, clust_col, cluster_uniq, radius, n_perms)

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
