"""Querying the DB
"""
# pylint: disable=too-many-locals
data_empty = dict(x=[0], y=[0], uuid=['1234'], color=[0], name=['no data'])


def get_data_sqlite(projections, sliders_dict, quantities, plot_info):
    """Query the sqlite database.
    
    Note: For efficiency, this uses the the sqlalchemy.sql interface which does
    not go via the (more convenient) ORM.
    """
    from import_db import automap_table, engine
    from sqlalchemy.sql import select, and_

    Table = automap_table(engine)

    selections = []
    for label in projections:
        selections.append(getattr(Table, label))

    filters = []
    for k, v in sliders_dict.items():
        if not v.value == quantities[k]['range']:
            f = getattr(Table, k).between(v.value[0], v.value[1])
            filters.append(f)

    s = select(selections).where(and_(*filters))

    results = engine.connect().execute(s).fetchall()

    nresults = len(results)
    if not results:
        plot_info.text = "No matching COFs found."
        return data_empty

    plot_info.text = "{} COFs found. Plotting...".format(nresults)

    # x,y position
    x, y, clrs, names, filenames = zip(*results)
    x = list(map(float, x))
    y = list(map(float, y))

    if projections[2] == 'bond_type':
        #clrs = map(lambda clr: bondtypes.index(clr), clrs)
        clrs = list(map(str, clrs))
    else:
        clrs = list(map(float, clrs))

    return dict(x=x, y=y, filename=filenames, color=clrs, name=names)


def get_data_aiida(projections, sliders_dict, quantities, plot_info):
    """Query the AiiDA database"""
    from aiida import load_dbenv, is_dbenv_loaded
    from aiida.backends import settings
    if not is_dbenv_loaded():
        load_dbenv(profile=settings.AIIDADB_PROFILE)
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm.data.parameter import ParameterData

    filters = {}

    def add_range_filter(bounds, label):
        # a bit of cheating until this is resolved
        # https://github.com/aiidateam/aiida_core/issues/1389
        #filters['attributes.'+label] = {'>=':bounds[0]}
        filters['attributes.' + label] = {
            'and': [{
                '>=': bounds[0]
            }, {
                '<': bounds[1]
            }]
        }

    for k, v in sliders_dict.items():
        # Note: filtering is costly, avoid if possible
        if not v.value == quantities[k]['range']:
            add_range_filter(v.value, k)

    qb = QueryBuilder()
    qb.append(
        ParameterData,
        filters=filters,
        project=['attributes.' + p
                 for p in projections] + ['uuid', 'extras.cif_uuid'],
    )

    nresults = qb.count()
    if nresults == 0:
        plot_info.text = "No matching COFs found."
        return data_empty

    plot_info.text = "{} COFs found. Plotting...".format(nresults)

    # x,y position
    x, y, clrs, uuids, names, cif_uuids = zip(*qb.all())
    plot_info.text = "{} COFs queried".format(nresults)
    x = map(float, x)
    y = map(float, y)
    cif_uuids = map(str, cif_uuids)
    uuids = map(str, uuids)

    if projections[2] == 'bond_type':
        #clrs = map(lambda clr: bondtypes.index(clr), clrs)
        clrs = map(str, clrs)
    else:
        clrs = map(float, clrs)

    return dict(x=x, y=y, uuid=cif_uuids, color=clrs, name=names)
