""" Plots the workflow's graph
"""
import os

EXPLORE_URL = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")

def get_aiida_link(node_dict, extra_tag):
    return "{}/details/{}".format(EXPLORE_URL,node_dict[extra_tag].uuid)

def get_graph(cof_group, node_dict):

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
    g.node("Original\nstructure", shape="oval",                  href=get_aiida_link(node_dict,"orig_cif"))
    g.node("geo1",label="Geometric\nproperties", shape="oval",   href=get_aiida_link(node_dict,"orig_zeopp_out"))
    g.node("DFT optimization", shape="box",                      href=get_aiida_link(node_dict,"dftopt_wc"))
    g.node("DFT output details", shape="oval",                    href=get_aiida_link(node_dict,"dftopt_out"))
    g.node("DDEC charges evaluation", shape="box",               href=get_aiida_link(node_dict,"ddec_wc"))
    g.node("Optimized structure\n W/DDEC charges", shape="oval", href=get_aiida_link(node_dict,"opt_cif_ddec"))
    g.node("geo2",label="Geometric\nproperties", shape="oval",   href=get_aiida_link(node_dict,"opt_zeopp_out"))
    g.node("Adsorption calculation\nCO2", shape="box",           href=get_aiida_link(node_dict,"isot_co2_wc"))
    g.node("Adsorption calculation\nN2", shape="box",            href=get_aiida_link(node_dict,"isot_n2_wc"))
    g.node("Results CO2", shape="oval",                          href=get_aiida_link(node_dict,"isot_co2_out"))
    g.node("Results N2", shape="oval",                           href=get_aiida_link(node_dict,"isot_n2_out"))
    g.node("CCS process\nperformances", shape="oval",            href=get_aiida_link(node_dict,"pe_out"))

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
