import decoupler as dc
import pandas as pd

def analyze_pathways(adata, pathway_file=None):
    if pathway_file:
        markers = pd.read_csv(pathway_file)
    else:
        print('No marker set specified; defaulting back to PROGENy')
        markers = pd.read_csv('/app/progeny.csv')

    estimate,pvals = dc.run_mlm(
        adata.X,
        markers,
        source='pathway',
        target='genesymbol',
        weight='weight',
        verbose=True,
    )

    adata.obsm['pathways'] = estimate
    adata.obsm['pathway_pval'] = pvals
    
    return adata
