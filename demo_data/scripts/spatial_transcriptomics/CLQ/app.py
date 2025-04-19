import numpy as np
import pandas as pd
from anndata import AnnData
import squidpy as sq
from numba import njit, prange
import time

@njit(parallel=True, fastmath=True)
def _count_neighborhood_vectors(indices, indptr, cell_types, n_perms, n_clust):
    """
    Efficiently count cell types in neighborhoods.

    Parameters
    ----------
    indices
        scipy.sparse.csr_matrix.indices
    indptr
        scipy.sparse.csr_matrix.indptr
    cell_types
        Array of shape (n_perms+1, n_cells) with cell type assignments
    n_perms
        Number of permutations
    n_clust
        Number of cell types

    Returns
    -------
    Array of shape (n_perms+1, n_cells, n_clust) with neighborhood counts
    """
    n_cells = indptr.shape[0] - 1
    result = np.zeros((n_perms+1, n_cells, n_clust), dtype=np.float32)

    # For each permutation
    for perm in range(n_perms+1):
        # For each cell
        for i in prange(n_cells):
            # Get neighbors
            start, end = indptr[i], indptr[i+1]
            neighbors = indices[start:end]

            # Count cell types in neighborhood
            if len(neighbors) > 0:
                for neighbor in neighbors:
                    cell_type = cell_types[perm, neighbor]
                    result[perm, i, cell_type] += 1

    return result

@njit(parallel=True)
def _calculate_global_clq(local_clq, cell_types, n_perms, n_cells, n_clust):
    """
    Calculate global CLQ scores efficiently.

    Parameters
    ----------
    local_clq
        Array of shape (n_perms+1, n_cells, n_clust) with local CLQ values
    cell_types
        Array of shape (n_perms+1, n_cells) with cell type assignments
    n_perms
        Number of permutations
    n_cells
        Number of cells
    n_clust
        Number of cell types

    Returns
    -------
    Array of shape (n_clust, n_perms+1, n_clust) with global CLQ values
    """
    global_clq = np.zeros((n_clust, n_perms+1, n_clust), dtype=np.float32)

    # For each cell type
    for cell_type in range(n_clust):
        # For each permutation
        for perm in prange(n_perms+1):
            # Count cells of this type in this permutation
            count = 0
            sum_values = np.zeros(n_clust, dtype=np.float32)

            # Sum local_clq values for cells of this type
            for cell in range(n_cells):
                if cell_types[perm, cell] == cell_type:
                    sum_values += local_clq[perm, cell]
                    count += 1

            # Calculate mean if there are cells of this type
            if count > 0:
                global_clq[cell_type, perm] = sum_values / count

    return global_clq

def CLQ_vec_numba(adata, clust_col='leiden', clust_uniq=None, radius=50, n_perms=1000):
    """
    Highly optimized Cell-Cell Interaction Score calculation using Numba.

    Parameters
    ----------
    adata : AnnData
        AnnData object with spatial coordinates
    clust_col : str
        Column name in adata.obs containing cell type labels
    clust_uniq : list or None
        Optional list of unique clusters to consider
    radius : float
        Neighborhood search radius
    n_perms : int
        Number of permutations for significance testing
    """
    start_time = time.time()

    # Calculate spatial neighbors once
    adata.obsm['spatial'] = adata.obs[['x_coordinate', 'y_coordinate']].to_numpy()

    radius = float(radius)
    sq.gr.spatial_neighbors(adata, coord_type='generic', radius=radius)
    neigh_idx = adata.obsp['spatial_connectivities']

    # Convert to CSR format for efficient access
    if not neigh_idx.format == 'csr':
        neigh_idx = neigh_idx.tocsr()

    # Extract indices and indptr for Numba
    indices = neigh_idx.indices.astype(np.int32)
    indptr = neigh_idx.indptr.astype(np.int32)

    # Global frequencies
    global_cluster_freq = adata.obs[clust_col].value_counts(normalize=True)
    if clust_uniq is not None:
        null_clusters = global_cluster_freq.index.difference(pd.Index(clust_uniq))
        for c in null_clusters:
            global_cluster_freq[c] = 0

    # Map clusters to integers for Numba
    label_dict = {x: i for i, x in enumerate(global_cluster_freq.index)}
    reverse_label_dict = {i: x for x, i in label_dict.items()}
    n_clust = len(label_dict)
    n_cells = adata.shape[0]

    # Create cell type array for all permutations
    cell_types = np.zeros((n_perms+1, n_cells), dtype=np.int32)

    # Original data as first permutation
    cell_types[0] = np.array([label_dict[x] for x in adata.obs[clust_col]], dtype=np.int32)

    # Generate permutations
    for i in range(1, n_perms+1):
        cell_types[i] = np.random.permutation(cell_types[0])

    #print(f"Setup completed in {time.time() - start_time:.2f}s")
    start_time = time.time()

    # Calculate neighborhood content vectors using Numba
    ncv = _count_neighborhood_vectors(indices, indptr, cell_types, n_perms, n_clust)

    #print(f"NCVs calculated in {time.time() - start_time:.2f}s")
    start_time = time.time()

    # Normalize NCVs
    neighborhood_sizes = np.sum(ncv, axis=2, keepdims=True)
    norm_ncv = np.divide(ncv, neighborhood_sizes, out=np.zeros_like(ncv), where=neighborhood_sizes > 0)

    # Calculate local CLQ
    global_freqs = np.array([global_cluster_freq[x] for x in label_dict])
    global_freqs_adj = np.where(global_freqs > 0, global_freqs, 1.0)  # Avoid division by zero
    local_clq = norm_ncv / global_freqs_adj

    #print(f"Local CLQ calculated in {time.time() - start_time:.2f}s")
    start_time = time.time()

    # Calculate global CLQ using Numba
    global_clq = _calculate_global_clq(local_clq, cell_types, n_perms, n_cells, n_clust)

    #print(f"Global CLQ calculated in {time.time() - start_time:.2f}s")
    start_time = time.time()

    # Extract observed values
    idx = list(label_dict.keys())
    lclq = pd.DataFrame(local_clq[0], columns=idx, index=adata.obs_names)
    gclq = pd.DataFrame(global_clq[:, 0, :], index=idx, columns=idx)
    ncv_df = pd.DataFrame(ncv[0], index=adata.obs_names, columns=idx)

    # Permutation test
    clq_perm_attr = ((global_clq[:, 1:, :] >= global_clq[:, 0, :].reshape(n_clust, -1, n_clust)).sum(1) + 1) / (n_perms + 1)
    clq_perm_avoid = 1 - clq_perm_attr
     
    clq_perm_attr = pd.DataFrame(clq_perm_attr, index=idx, columns=idx)
    clq_perm_avoid = pd.DataFrame(clq_perm_avoid, index=idx, columns=idx)
 
    perm_test = pd.DataFrame('n.s.',index=idx,columns=idx)
    perm_test[clq_perm_attr < 0.05] = 'attractive'
    perm_test[clq_perm_avoid < 0.05] = 'avoidant'

    #print(f"Results processed in {time.time() - start_time:.2f}s")

    # Store results
    adata.obsm['NCV'] = ncv_df
    adata.obsm['local_clq'] = lclq
    adata.obs[clust_col] = adata.obs[clust_col].astype(str)
    adata.uns['CLQ'] = {'global_clq': gclq, 'p_attr': clq_perm_attr, 'p_avoid': clq_perm_avoid, 'perm_test': perm_test}

    # Create output AnnData object
    obs = pd.DataFrame(index=adata.obs[clust_col].unique(), columns=[], data=[])
    var = pd.DataFrame(index=adata.obs[clust_col].unique(), columns=[], data=[])

    bdata = AnnData(
        obs=obs,
        var=var
    )

    bdata.uns['local_clq'] = lclq
    bdata.layers['global_clq'] = gclq
    bdata.layers['p_attr'] = clq_perm_attr
    bdata.layers['p_avoid'] = clq_perm_avoid

    return bdata, adata


def run(**kwargs):
    print("Running CLQ vectorization...")
    # after_phenograph_clusters on full data per image
    adata = kwargs.get('adata')
    tasks_list = kwargs.get('tasks_list')

    adatas_list = []
    radius = kwargs.get('radius')
    n_perms = kwargs.get('n_perms')
    for task in tasks_list:
        omero_id = task['omeroId']
        filtered_adata = adata[adata.obs['image_id'] == omero_id].copy()

        clust_col = filtered_adata.obs.columns[-1:][0]
        clust_uniq = filtered_adata.obs['cluster_phenograph'].unique()

        processed_adata, _ = CLQ_vec_numba(filtered_adata, clust_col, clust_uniq, radius, n_perms)
        adatas_list.append({
            f"{task.get('_key')}-clq": processed_adata}
        )

    clust_col = adata.obs.columns[-1:][0]
    obs_df=adata.obs[clust_col]
    cluster_uniq=list(set(obs_df))
    bdata, adata = CLQ_vec_numba(adata, clust_col, cluster_uniq, radius, n_perms)

    return {
        'adatas_list': adatas_list,
        'clq_adata': adata,
        'adata': bdata
    }
