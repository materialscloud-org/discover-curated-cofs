""" Queries to the DB
"""

from __future__ import absolute_import


def get_sqlite_data(name, plot_info):
    """Query the sqlite database"""
    from import_db import automap_table, engine
    from sqlalchemy.orm import sessionmaker

    # configure Session class with desired options
    Session = sessionmaker(bind=engine)
    session = Session()

    Table = automap_table(engine)

    query = session.query(Table).filter_by(name=str(name))

    nresults = query.count()
    if nresults == 0:
        plot_info.text = "No matching COF found."
        return None
    return query.one()

def get_data_aiida(structure_label='13161N2', link_label='dftopt_out'):
    """Query the AiiDA database"""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import WorkFunctionNode, Node

    qb = QueryBuilder()
    qb.append(Node, filters={'label': structure_label}, tag='cof')
    qb.append(WorkFunctionNode, filters={'attributes.function_name': {'==': 'link_outputs'}}, with_incoming='cof', tag='link')
    qb.append(Node, edge_filters={'label': link_label}, with_outgoing='link')
    return qb.all()[0][0]

def get_curated_cofs_version(structure_label='13161N2'):
    """Query the AiiDA database"""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import WorkFunctionNode, Node

    qb = QueryBuilder()
    qb.append(Node, filters={'label': structure_label}, tag='cof')
    qb.append(WorkFunctionNode, filters={'attributes.function_name': {'==': 'link_outputs'}}, with_incoming='cof', tag='link')
    return qb.all()[0][0].extras['curated_cofs_version']
