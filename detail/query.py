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

def get_data_aiida(structure_label='13161N2', link_label='cp2k_stepsfile'):
    """Query the AiiDA database"""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import WorkFunctionNode, Node, StructureData

    qb = QueryBuilder()
    qb.append(StructureData, filters={ 'label': structure_label}, tag='structure')
    qb.append(WorkFunctionNode, filters={ 'attributes.function_name': {'==': 'collect_outputs'} }, with_incoming='structure', tag='collect')
    wf_node = qb.one()[0]

    qb = QueryBuilder()
    qb.append(Node, filters={ 'uuid': wf_node.uuid}, tag='collect')
    qb.append(Node, project=['*'], edge_filters={'label': link_label}, with_outgoing='collect')
    res_node = qb.one()[0]

    return res_node
