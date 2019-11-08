""" Plots the workflow's graph
"""

def get_aiida_link(group_node, extra_tag):
    import os
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import  Node, Group

    explore_url = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")

    qb = QueryBuilder()
    qb.append(Group, filters={'uuid': group_node.uuid}, tag='group')
    qb.append(Node, filters={'extras.curated-cof_tag': extra_tag}, with_group='group')
    res_node = qb.all()[0][0]

    return "{}/details/{}".format(explore_url,res_node.uuid)

def get_graph(cof_group):

    from graphviz import Digraph
    import pandas as pd
    import os

    try:
        this_dir = os.path.dirname(os.path.abspath(__file__)) + '/'
    except:
        this_dir = '',

    df = pd.read_csv(this_dir + "static/cof-papers.csv")
    cof_label = cof_group.label.split("_")[1]
    paper_id = "p{:s}".format(cof_label[:4])
    paper_row = df.loc[df["CURATED-COFs paper ID"] == paper_id ]
    link_paper = "https://doi.org/" + paper_row["DOI"].values[0]

    link_github = "https://github.com/danieleongari/CURATED-COFs/blob/master/cifs/{}.cif".format(cof_label)

    g = Digraph("Workflow's graph")

    g.attr(rankdir='TB')
    g.attr("node",style='filled', fillcolor='white:gray', gradientangle='45')

    g.node("Reference\npublication", shape="oval",               href=link_paper)
    g.node("GitHub", shape="oval",                               href=link_github)
    g.node("Original\nstructure", shape="oval",                  href=get_aiida_link(cof_group,"orig_cif"))
    g.node("geo1",label="Geometric\nproperties", shape="oval",   href=get_aiida_link(cof_group,"orig_zeopp_out"))
    g.node("DFT optimization", shape="box",                      href=get_aiida_link(cof_group,"dftopt_wc"))
    g.node("DFT output details", shape="box",                    href=get_aiida_link(cof_group,"dftopt_out"))
    g.node("DDEC charges evaluation", shape="box",               href=get_aiida_link(cof_group,"ddec_wc"))
    g.node("Optimized structure\n W/DDEC charges", shape="oval", href=get_aiida_link(cof_group,"opt_cif_ddec"))
    g.node("geo2",label="Geometric\nproperties", shape="oval",   href=get_aiida_link(cof_group,"opt_zeopp_out"))
    g.node("Adsorption calculation\nCO2", shape="box",           href=get_aiida_link(cof_group,"isot_co2_wc"))
    g.node("Adsorption calculation\nN2", shape="box",            href=get_aiida_link(cof_group,"isot_n2_wc"))
    g.node("Results CO2", shape="oval",                          href=get_aiida_link(cof_group,"isot_co2_out"))
    g.node("Results N2", shape="oval",                           href=get_aiida_link(cof_group,"isot_n2_out"))
    g.node("CCS process\nperformances", shape="oval",            href=get_aiida_link(cof_group,"pe_out"))

    g.edge("Reference\npublication",'GitHub')
    g.edge('GitHub', 'Original\nstructure')
    g.edge('Original\nstructure',"geo1")
    g.edge('Original\nstructure',"DFT optimization")
    g.edge("DFT optimization", "DDEC charges evaluation")
    g.edge("DFT optimization", "DFT output details")
    g.edge("DDEC charges evaluation", "Optimized structure\n W/DDEC charges")
    g.edge("Optimized structure\n W/DDEC charges","geo2")
    g.edge("Optimized structure\n W/DDEC charges","Adsorption calculation\nCO2")
    g.edge("Optimized structure\n W/DDEC charges","Adsorption calculation\nN2")
    g.edge("Adsorption calculation\nCO2","Results CO2")
    g.edge("Adsorption calculation\nN2","Results N2")
    g.edge("Results CO2","CCS process\nperformances")
    g.edge("Results N2","CCS process\nperformances")
    return g
