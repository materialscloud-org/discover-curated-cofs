""" Queries to the DB
"""

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


def get_data_aiida(cif_uuid, plot_info):
    """Query the AiiDA database"""
    from aiida import load_dbenv, is_dbenv_loaded
    from aiida.backends import settings
    if not is_dbenv_loaded():
        load_dbenv(profile=settings.AIIDADB_PROFILE)
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm.data.parameter import ParameterData
    from aiida.orm.data.cif import CifData

    qb = QueryBuilder()
    qb.append(
        CifData, filters={'uuid': {
            '==': cif_uuid
        }}, tag='cifs', project='*')
    qb.append(
        ParameterData,
        descendant_of='cifs',
        project='*',
    )

    nresults = qb.count()
    if nresults == 0:
        plot_info.text = "No matching COF found."
        return None
    return qb.one()

