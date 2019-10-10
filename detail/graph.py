""" Plots the workflow's graph
"""

def get_aiida_link(cof_label, link_label, get_wf):
    import os
    from aiida import load_dbenv, is_dbenv_loaded
    if not is_dbenv_loaded():
        load_dbenv()
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import WorkCalculation, Node
    from aiida.orm.data.structure import StructureData
    explore_url = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")

    qb = QueryBuilder()
    qb.append(StructureData, filters={ 'label': cof_label}, tag='structure')
    qb.append(WorkCalculation, filters={ 'attributes.function_name': {'==': 'collect_outputs'} }, output_of='structure', tag='collect')
    wf_node = qb.one()[0]

    qb = QueryBuilder()
    qb.append(Node, filters={ 'uuid': wf_node.uuid}, tag='collect')
    qb.append(Node, project=['*'], edge_filters={'label': link_label}, input_of='collect')
    res_node = qb.one()[0]

    if get_wf:
        qb = QueryBuilder()
        qb.append(Node, filters={ 'uuid': res_node.uuid}, tag='param')
        qb.append(WorkCalculation, input_of='param')
        qb.order_by({WorkCalculation:{'ctime':'asc'}}) #Dirty trick: for opt_cif_ddec takes RobustCellOptDDEC instead of DDEC WorkChain
        res_node = qb.all()[0][0]

    return "{}/details/{}".format(explore_url,res_node.uuid)

def get_graph(cof_label):

    from graphviz import Digraph
    import pandas as pd

    df = pd.read_csv("detail/static/cof-papers.csv")
    paper_id = "p{:s}".format(cof_label[:4])
    paper_row = df.loc[df["CURATED-COFs paper ID"] == paper_id ]
    link_paper = paper_row["URL"].values[0]

    link_github = "https://github.com/danieleongari/CURATED-COFs/blob/master/cifs/{}.cif".format(cof_label)

    g = Digraph("Workflow's graph")

    g.attr(rankdir='TB')
    g.attr("node",style='filled', fillcolor='white:gray', gradientangle='45')

    g.node("Reference\npublication", shape="oval",                              href=link_paper)
    g.node("GitHub", shape="oval",                                              href=link_github)
    g.node("Original\nstructure", shape="oval",                                 href=get_aiida_link(cof_label,"ref_structure",False))
    g.node("geo1",label="Geometrical\nproperties", shape="oval",                href=get_aiida_link(cof_label,"ref_out_zeopp",False))
    g.node("DFT optimization\n& DDEC charges", shape="box",                     href=get_aiida_link(cof_label,"opt_cif_ddec",True))
    g.node("Optimized structure\n W/DDEC charges", shape="oval",                href=get_aiida_link(cof_label,"opt_cif_ddec",False))
    g.node("geo2",label="Geometrical\nproperties", shape="oval",                href=get_aiida_link(cof_label,"opt_out_zeopp",False))
    g.node("Adsorption calculation\nCO2", shape="box",                          href=get_aiida_link(cof_label,"iso_co2",True))
    g.node("Adsorption calculation\nN2", shape="box",                           href=get_aiida_link(cof_label,"iso_n2",True))
    g.node("Results CO2", shape="oval",                                         href=get_aiida_link(cof_label,"iso_co2",False))
    g.node("Results N2", shape="oval",                                          href=get_aiida_link(cof_label,"iso_n2",False))
    g.node("CCS process\nperformances", shape="oval",                           href=get_aiida_link(cof_label,"opt_out_pe",False))

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
