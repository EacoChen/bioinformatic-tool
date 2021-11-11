
cyano_new_gid = open(f'{HOME}/work/8_search_phyla/species/cyano_new_list.txt').read().split('\n')
hou_tem_topo = Tree('./work/hou/topology.contree')
hou_tem_topo.resolve_polytomy(recursive=True)

df = pd.read_csv('./work/calibration_table.tsv',
                 header=None,
                 sep='\t')
df = df.T

hou_cal_trees = []
for i,x in enumerate(df.index):
    if i > 0 :
        tmp_tree = hou_tem_topo.copy()
        for j in range(0,5):
            if j == 0:
                tmp_tree.name = df.iat[i,j]
            else:
                if df.iat[i,j] != '0':
                    ancestor = tmp_tree.get_common_ancestor(df.iat[0,j].split(','))
                    ancestor.name = df.iat[i,j]
        hou_cal_trees.append(tmp_tree)

modi_hou_cal_trees = []
for tree in hou_cal_trees:
    modi_hou_cal_trees.append(tree.write(format=8,format_root_node=True).replace('NoName',''))

count = 1
for _ in modi_hou_cal_trees:
    with open(f'./work/hou/cal_tree/set{count}.newick','w') as f:
        f.write('119\n'+_)
    count += 1


#分割线，后面这部分在看是什么taxonomy，最早的测试部分脚本
cal_template = Tree(thliao_tree,format=1)

cal_node = []
for node in cal_template.traverse():
    if node.name.startswith('>'):
        cal_node.append(node)

gids = []
for node in cal_node[-3].traverse():
    if node.is_leaf():
        gids.append(node.name)

r_search, f_search = edl.esearch(db='assembly', ids=gids,
                                 result_func=lambda x: [Entrez.read(io.BytesIO(x.encode('utf-8')))])

uids = r_search[0]['IdList']

r_ln, f_ln = edl.elink(dbfrom='assembly', ids=uids,db='taxonomy',
                        result_func=lambda x: Entrez.read(io.BytesIO(x.encode('utf-8'))))

taxids = []
for _ in r_ln:
    taxids.append(_['LinkSetDb'][0]['Link'][0]['Id'])

taxids_full_lineage = []
for _ in taxids:
    taxids_full_lineage+=ncbi.get_lineage(_)

for k,v in dict(Counter(taxids_full_lineage)).items():
    if v >= 2:
        print(ncbi.get_taxid_translator([k]),v)

# get the dict of calibration root and cyanobacteria

cal_table = {_:[] for _ in cal_node_gid}
for cal_tree in glob(join(HOME,'work','hou','cal_tree','*.newick')):
    with open(cal_tree,'r') as f:
        thliao_tree = f.read().split('\n')[-1]

    cal_template = Tree(thliao_tree,format=1)

    for k,v in cal_table.items():
        cal_table[k]=v+[0]

    for node in cal_template.traverse():
        if node.name.startswith(">") or node.name.startswith("<"):
            gid = tuple(_.name for _ in node if _.is_leaf())
            if gid in cal_node_gid:
                cal_table[gid] = cal_table[gid][:-1]+[node.name]