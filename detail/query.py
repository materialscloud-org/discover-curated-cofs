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
    """Query the AiiDA database to get the curated-cof group"""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Group
    qb = QueryBuilder()
    qb.append(Group, filters={'label': 'curated-cof_{}'.format(label)})
    return qb.all()[0][0]

def get_data_aiida(group_node, extra_tag):
    """Query the AiiDA database"""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Node, Group

    qb = QueryBuilder()
    qb.append(Group, filters={'uuid': group_node.uuid}, tag='group')
    qb.append(Node, filters={'extras.curated-cof_tag': extra_tag}, with_group='group')
    return qb.all()[0][0]
