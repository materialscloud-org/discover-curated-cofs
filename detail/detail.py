# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals
from __future__ import print_function

from bokeh.layouts import layout
import bokeh.models as bmd
from bokeh.models.widgets import RangeSlider, Select, Button, PreText
from bokeh.io import curdoc

info_block = PreText(text='', width=500, height=100)
plot_info = PreText(text='', width=300, height=100)
sizing_mode = 'fixed'
l = layout(
    [
        [info_block],
        [plot_info],
    ], sizing_mode=sizing_mode)


def get_data(name):
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
        return ""
    return query.one()


def get_data_aiida(cif_uuid):
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


def update():
    # get structure uuid from arguments
    args = curdoc().session_context.request.arguments
    try:
        name = args.get('name')[0]
    except (TypeError, KeyError):
        name = 'e2ea913a-1722-40ec-ae0d-5adc64a8ba7a'

    from import_db import get_cif_content

    entry = get_data(name=name)

    if entry:
        info_block.text = entry.filename
        cif_str = get_cif_content(entry.filename)

        s = "\n"
        for k in entry.__dict__:
            s += "{}: {}\n".format(k, getattr(entry, k))

        info_block.text += s


def tab_detail():
    # Make a tab with the layout
    update()
    tab = bmd.Panel(child=l, title='Detail view')
    return tab
