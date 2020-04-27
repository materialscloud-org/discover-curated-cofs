""" Plots the workflow's graph
"""
import os
from graphviz import Digraph

EXPLORE_URL = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")


def get_aiida_link(mat_dict, extra_tag):
    return "{}/details/{}".format(EXPLORE_URL, mat_dict[extra_tag].uuid)


def get_graph(mat_dict):
    """Sketch a graph of the CO2 capture workflow (appl_pecoal).
    NOTE: dropped link to ProcessNodes because they are different depending from the workflow version, are not included 
    in groups, ansd would be difficult to maintain.
    """

    link_paper = "https://doi.org/" + mat_dict['orig_cif'].extras['doi_ref']
    link_github = "https://github.com/danieleongari/CURATED-COFs/blob/master/cifs/{}.cif".format(
        mat_dict['orig_cif'].label)

    g = Digraph("Workflow's graph")

    g.attr(rankdir='TB')
    g.attr("node", style='filled', fillcolor='white:gray', gradientangle='45')

    g.node("Reference\npublication", shape="oval", href=link_paper)
    g.node("GitHub", shape="oval", href=link_github)
    g.node("Original\nstructure", shape="oval", href=get_aiida_link(mat_dict, "orig_cif"))
    g.node("geo1", label="Geometric\nproperties", shape="oval", href=get_aiida_link(mat_dict, "orig_zeopp"))
    g.node("DFT optimization", shape="box")
    g.node("DFT output details", shape="oval", href=get_aiida_link(mat_dict, "dftopt"))
    g.node("DDEC charges evaluation", shape="box")
    g.node("Optimized structure\n W/DDEC charges", shape="oval", href=get_aiida_link(mat_dict, "opt_cif_ddec"))
    g.node("geo2", label="Geometric\nproperties", shape="oval", href=get_aiida_link(mat_dict, "opt_zeopp"))
    g.node("Adsorption calculation\nCO2", shape="box")
    g.node("Adsorption calculation\nN2", shape="box")
    g.node("Results CO2", shape="oval", href=get_aiida_link(mat_dict, "isot_co2"))
    g.node("Results N2", shape="oval", href=get_aiida_link(mat_dict, "isot_n2"))
    g.node("CCS process\nperformances", shape="oval", href=get_aiida_link(mat_dict, "appl_pecoal"))

    g.edge("Reference\npublication", 'GitHub')
    g.edge('GitHub', 'Original\nstructure')
    g.edge('Original\nstructure', "geo1")
    g.edge('Original\nstructure', "DFT optimization")
    g.edge("DFT optimization", "DDEC charges evaluation")
    g.edge("DFT optimization", "DFT output details")
    g.edge("DDEC charges evaluation", "Optimized structure\n W/DDEC charges")
    g.edge("Optimized structure\n W/DDEC charges", "geo2")
    g.edge("Optimized structure\n W/DDEC charges", "Adsorption calculation\nCO2")
    g.edge("Optimized structure\n W/DDEC charges", "Adsorption calculation\nN2")
    g.edge("Adsorption calculation\nCO2", "Results CO2")
    g.edge("Adsorption calculation\nN2", "Results N2")
    g.edge("Results CO2", "CCS process\nperformances")
    g.edge("Results N2", "CCS process\nperformances")
    return g
