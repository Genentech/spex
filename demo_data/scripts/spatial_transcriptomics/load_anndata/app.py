import scanpy as sc

def run(**kwargs):
    files = kwargs.get('files', [])
    path = kwargs.get('image_path')

    if files:
        adatas = []
        for file in files:
            adata = sc.read_h5ad(file)
            adata.obs['filename'] = file.split('\\')[-1]
            adatas.append(adata)
        combined_adata = sc.concat(adatas, axis=0, join='outer', label='filename', index_unique='-')
        print('combined')
        return {'adata': combined_adata}
    else:
        adata = sc.read_h5ad(path)
        return {'adata': adata}
