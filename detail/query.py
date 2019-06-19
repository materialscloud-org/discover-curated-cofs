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


# def get_data_aiida(cif_uuid, plot_info):
#     """Query the AiiDA database"""
#     from aiida import load_dbenv, is_dbenv_loaded
#     from aiida.backends import settings
#     if not is_dbenv_loaded():
#         load_dbenv(profile=settings.AIIDADB_PROFILE)
#     from aiida.orm.querybuilder import QueryBuilder
#     from aiida.orm.data.parameter import ParameterData
#     from aiida.orm.data.cif import CifData

#     qb = QueryBuilder()
#     qb.append(CifData,
#               filters={'uuid': {
#                   '==': cif_uuid
#               }},
#               tag='cifs',
#               project='*')
#     qb.append(
#         ParameterData,
#         descendant_of='cifs',
#         project='*',
#     )

#     nresults = qb.count()
#     if nresults == 0:
#         plot_info.text = "No matching COF found."
#         return None
#     return qb.one()



def get_data_aiida(cif_uuid='3104b3fa-2f2f-40e7-9537-81f2e6b7ab08', link_label='cp2k_stepsfile'):
    """Query the AiiDA database"""
    from aiida import load_dbenv, is_dbenv_loaded
    from aiida.backends import settings
    if not is_dbenv_loaded():
        load_dbenv()
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import WorkCalculation, Node

    # For some reason, the combined query is very slow...
    # qb = QueryBuilder()
    # qb.append(Node, filters={ 'uuid': cif_uuid}, tag='cif')
    # qb.append(WorkCalculation, filters={ 'attributes.function_name': {'==': 'collect_outputs'} }, output_of='cif', tag='collect')
    # qb.append(Node, project=['*'], edge_filters={'label': 'cp2k_stepsfile'}, input_of='collect', )
    # qb.one()

    qb = QueryBuilder()
    qb.append(Node, filters={ 'uuid': cif_uuid}, tag='cif')
    qb.append(WorkCalculation, filters={ 'attributes.function_name': {'==': 'collect_outputs'} }, output_of='cif', tag='collect')
    wf_node = qb.one()[0]

    qb = QueryBuilder()
    qb.append(Node, filters={ 'uuid': wf_node.uuid}, tag='collect')
    qb.append(Node, project=['*'], edge_filters={'label': 'cp2k_stepsfile'}, input_of='collect')
    res_node = qb.one()[0]

    return res_node