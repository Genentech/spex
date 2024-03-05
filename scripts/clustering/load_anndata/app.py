import anndata


def run(**kwargs):

    adata = anndata.read(kwargs.get('image_path'))

    return {'adata': adata}
