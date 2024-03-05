import scanpy as sc


def run(**kwargs):

    path = kwargs.get('image_path')
    adata = sc.read_h5ad(path)

    return {'adata': adata}
