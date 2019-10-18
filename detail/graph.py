""" Plots the workflow's graph
"""

def get_aiida_link(cof_label, link_label):
    import os
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import  Node, StructureData, WorkFunctionNode

    explore_url = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")

    qb = QueryBuilder()
    qb.append(Node, filters={'label': cof_label}, tag='cof')
    qb.append(WorkFunctionNode, filters={'attributes.function_name': {'==': 'link_outputs'}}, with_incoming='cof', tag='link')
    qb.append(Node, edge_filters={'label': link_label}, with_outgoing='link')
    res_node = qb.all()[0][0]

    return "{}/details/{}".format(explore_url,res_node.uuid)

def get_graph(cof_label):

    from graphviz import Digraph
    import pandas as pd

    url = 'https://raw.githubusercontent.com/danieleongari/CURATED-COFs/additions/cof-papers.csv'#TODO: update!
    df = pd.read_csv(url)
    paper_id = "p{:s}".format(cof_label[:4])
    paper_row = df.loc[df["CURATED-COFs paper ID"] == paper_id ]
    link_paper = "https://doi.org/" + paper_row["DOI"].values[0]

    link_github = "https://github.com/danieleongari/CURATED-COFs/blob/additions/cifs/{}.cif".format(cof_label) #TODO: update!

    g = Digraph("Workflow's graph")

    g.attr(rankdir='TB')
    g.attr("node",style='filled', fillcolor='white:gray', gradientangle='45')

    g.node("Reference\npublication", shape="oval",                              href=link_paper)
    g.node("GitHub", shape="oval",                                              href=link_github)
    g.node("Original\nstructure", shape="oval",                                 href=get_aiida_link(cof_label,"orig_cif"))
    g.node("geo1",label="Geometrical\nproperties", shape="oval",                href=get_aiida_link(cof_label,"orig_zeopp_out"))
    g.node("DFT optimization\n& DDEC charges", shape="box")
    g.node("Optimized structure\n W/DDEC charges", shape="oval",                href=get_aiida_link(cof_label,"opt_cif_ddec"))
    g.node("geo2",label="Geometrical\nproperties", shape="oval",                href=get_aiida_link(cof_label,"opt_zepp_out"))
    g.node("Adsorption calculation\nCO2", shape="box")
    g.node("Adsorption calculation\nN2", shape="box")
    g.node("Results CO2", shape="oval",                                         href=get_aiida_link(cof_label,"isot_co2_out"))
    g.node("Results N2", shape="oval",                                          href=get_aiida_link(cof_label,"isot_n2_out"))
    g.node("CCS process\nperformances", shape="oval",                           href=get_aiida_link(cof_label,"pe_out"))

    g.edge("Reference\npublication",'GitHub')
    g.edge('GitHub', 'Original\nstructure')
    g.edge('Original\nstructure',"geo1")
    g.edge('Original\nstructure',"DFT optimization\n& DDEC charges")
    g.edge("DFT optimization\n& DDEC charges", "Optimized structure\n W/DDEC charges")
    g.edge("Optimized structure\n W/DDEC charges","geo2")
    g.edge("Optimized structure\n W/DDEC charges","Adsorption calculation\nCO2")
    g.edge("Optimized structure\n W/DDEC charges","Adsorption calculation\nN2")
    g.edge("Adsorption calculation\nCO2","Results CO2")
    g.edge("Adsorption calculation\nN2","Results N2")
    g.edge("Results CO2","CCS process\nperformances")
    g.edge("Results N2","CCS process\nperformances")
    return g
