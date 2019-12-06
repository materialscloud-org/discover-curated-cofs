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


def get_group(label='13161N2'):
    """Query the AiiDA database to get the curated-cof group.
    If multiple version are available qb.all()[0][0] shuld take the last one computed.
    """
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Group
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': 'curated-cof_{}_v%'.format(label)}})
    return qb.all()[0][0]

def get_node_dict(group):
    """Give a group return a dictionary with tags as keys and nodes as values."""
    node_dict = {}
    for node in group.nodes:
        node_dict[node.extras['curated-cof_tag']] = node
    return node_dict

def get_version(group_node):
    """Given a group return the version as integer."""
    return int(group_node.label.split("_v")[-1])
