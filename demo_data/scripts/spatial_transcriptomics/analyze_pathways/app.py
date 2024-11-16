import decoupler as dc
import pandas as pd
import pegasus as pg
from pegasusio import UnimodalData
import os

def annotate_clusters(adata, marker_db, cluster_key='leiden', method='pegasus'):
    #Args:
    #adata: the data
    #cluster_key: which key in adata.obs tells you the cluster a cell belongs to
    #marker_db: Either a string for pegasus, or a DataFrame that labels source ('gene') to target ('cell-type').
    #method: Pegasus will use DEGs; scanpy data will use decouplr

    if method == 'pegasus':
        pdat = UnimodalData(adata)
        ctypes = pg.infer_cell_types(pdat,markers=marker_db)

        adata.obs['cell_type'] = 'Unknown'
        for cluster in ctypes:
            if len(ctypes[cluster]) == 0:
                continue
            try:
                adata.obs.loc[adata.obs[cluster_key] == cluster,'cell_type'] = ctypes[cluster][0].name
            except:
                cluster_key = 'louvain'
                adata.obs.loc[adata.obs[cluster_key] == cluster,'cell_type'] = ctypes[cluster][0].name

    else:
        dc.decouple(
            adata,
            marker_db,
            source='src',
            target='genesymbol',
            weight='wgt',
            min_n=3,
            verbose=False,
            methods=[method]
        )

        acts = dc.get_acts(adata,obsm_key=f'{method}_estimate')

    return adata



def analyze_pathways(adata, pathway_file=None):

    script_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_path, 'progeny.csv')
    markers = pd.read_csv(path)

    dc.run_mlm(adata,markers,source='pathway',target='genesymbol',weight='weight',min_n=3,verbose=True,use_raw=False)

    acts = dc.get_acts(adata,obsm_key='mlm_estimate')
    adata.obsm['pathway_scores'] = acts.to_df()

    mean_acts = dc.summarize_acts(acts,groupby='cell_type',min_std=0)

    return adata


def run(**kwargs):
    adata = kwargs.get('adata')

    adata = annotate_clusters(adata, marker_db='human_immune')
    adata = analyze_pathways(adata)

    return {'adata': adata}

