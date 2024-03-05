import pegasus as pg
from pegasusio import UnimodalData
import scanpy as sc

#Helper class that lets us convert between Pegasus and scanPy
class DEResult:
    def __init__(self,cdata,r_arr,mode='pegasus'):
        self.mode = mode

        if mode == 'pegasus':
            clusters = set(x.split(':')[0] for x in r_arr.dtype.names)

            self.cluster_dfs = {}
            for clust_id in clusters:
                pg_df = pd.DataFrame(index=cdata.var_names,columns=['pval','qval','log2fc','mean'])
                pg_df.loc[:,'mean'] = 2**(r_arr[clust_id + ':log2Mean'])
                pg_df.loc[:,'pval'] = r_arr[clust_id + ':mwu_pval']
                pg_df.loc[:,'qval'] = r_arr[clust_id + ':mwu_qval']
                pg_df.loc[:,'log2fc'] = r_arr[clust_id + ':log2FC']

                self.cluster_dfs[clust_id] = pg_df
        else:
            clusters = set(r_arr['names'].dtype.names)

            self.cluster_dfs = {}
            for clust_id in clusters:
                sc_df = pd.DataFrame(index=r_arr['names'][clust_id],columns=['pval','qval','log2fc','mean'])
                sc_df.loc[:,'log2fc'] = r_arr['logfoldchanges'][clust_id]
                sc_df.loc[:,'pval'] = r_arr['pvals'][clust_id]
                sc_df.loc[:,'qval'] = r_arr['pvals_adj'][clust_id]
                if np.count_nonzero(cdata.obs.leiden == clust_id):
                    sc_df.loc[:,'mean'] = cdata[cdata.obs.leiden == clust_id,sc_df.index].X.mean(axis=0)
                else:
                    sc_df.loc[:,'mean'] = 0

                self.cluster_dfs[clust_id] = sc_df
    
    def convert_to_pegasus(self):
        pfields = ['auroc','log2FC','log2Mean','log2Mean_other','mwu_U','mwu_pval','mwu_qval','percentage','percentage_fold_change','percentage_other']
        dfields = ['pval','log2fc','mean','mean','pval','pval','qval','pval','log2fc','log2fc']

        x = next(iter(self.cluster_dfs))
        test_res = np.recarray(
            (self.cluster_dfs[x].shape[0],),
            dtype=((np.record,[(':'.join([x,y]),'<f4') for x in self.cluster_dfs for y in pfields]))
        )
        for x in self.cluster_dfs:
            for y,c in zip(pfields,dfields):
                test_res[':'.join([x,y])] = self.cluster_dfs[x].loc[:,c]
        return test_res
    
    def convert_to_scanpy(self):
        rgg = {}
        
        x = next(iter(self.cluster_dfs))
        rgg['names'] = np.recarray(
            (self.cluster_dfs[x].shape[0],),
            dtype=((np.record,[(x, 'O') for x in self.cluster_dfs]))
        )
        rgg['pvals'] = np.recarray(
            (self.cluster_dfs[x].shape[0],),
            dtype=[(x, 'O') for x in self.cluster_dfs]
        )
        rgg['pvals_adj'] = np.recarray(
            (self.cluster_dfs[x].shape[0],),
            dtype=[(x, 'O') for x in self.cluster_dfs]
        )
        rgg['logfoldchanges'] = np.recarray(
            (self.cluster_dfs[x].shape[0],),
            dtype=[(x, 'O') for x in self.cluster_dfs]
        )
        rgg['scores'] = np.recarray(
            (self.cluster_dfs[x].shape[0],),
            dtype=[(x, 'O') for x in self.cluster_dfs]
        )

        for x in self.cluster_dfs:
            cdf = self.cluster_dfs[x]
            cdf = cdf.sort_values(by=['pval','log2fc'],ascending=[True,False])

            rgg['names'][x] = np.array(cdf.index)
            rgg['pvals'][x] = np.array(cdf.pval)
            rgg['pvals_adj'][x] = np.array(cdf.qval)
            rgg['logfoldchanges'][x] = np.array(cdf.log2fc)
            rgg['scores'][x] = np.zeros((self.cluster_dfs[x].shape[0],))
        
        return rgg
    
def differential_expression(adata, cluster_key='leiden', method='wilcoxon', mdl=None):
    #Args:
    #adata: the data
    #cluster_key: adata.obs[key] determines cell cluster membership
    #method: Significance test - currently support basic DEG from scanpy, pegasus and built-in scVI method.

    if method == 'scvi':
        if 'X_scvi' not in adata.obsm:
            print('Cannot run scVI method without first training model.')
            return adata
        if mdl is None:
            print('SCVI model not provided.')
            adata.uns['de_res'] = mdl.differential_expression(adata, groupby=cluster_key)
        
    elif method == 'pegasus':
        pdat = UnimodalData(adata)
        pg.de_analysis(pdat, cluster=cluster_key)

        #Convert from pegasus format to scanpy format and store.
        de_res = DEResult(adata, pdat.varm['de_res'],mode='pegasus')
        adata.varm['de_res'] = de_res.convert_to_pegasus()
        adata.uns['de_res'] = de_res.convert_to_scanpy()
        
    #ADD layer here for logarithmized, but not scaled counts.
    else:
        sc.tl.rank_genes_groups(adata,use_raw=False,groupby=cluster_key,method=method,key_added='de_res')
        de_res = DEResult(adata, adata.uns['de_res'],mode='scanpy')
        adata.varm['de_res'] = de_res.convert_to_pegasus()

    if method == 'scvi':
        return adata, mdl
    else:
        return adata

def run(**kwargs):
    adata = kwargs.get('adata')

    ckey = kwargs.get('cluster_key')
    m = kwargs.get('method')
    mdl = kwargs.get('mdl')

    out = differential_expression(adata,ckey,m,mdl)
    if m == 'scvi':
        return {'adata': out[0], 'vae': out[1]}
    else:
        return {'adata': out, 'vae': None}
    
    