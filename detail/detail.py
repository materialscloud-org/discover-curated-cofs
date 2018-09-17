# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals
from __future__ import print_function

from bokeh.layouts import layout
import bokeh.models as bmd
from bokeh.models.widgets import RangeSlider, Select, Button, PreText
from bokeh.io import curdoc

# get structure uuid from arguments
args = curdoc().session_context.request.arguments
try:
    cif_uuid = args.get('cif_uuid')
except (TypeError, KeyError):
    cif_uuid = 'e2ea913a-1722-40ec-ae0d-5adc64a8ba7a'
cif_uuid = 'e2ea913a-1722-40ec-ae0d-5adc64a8ba7a'

info_block = PreText(text='', width=500, height=100)
plot_info = PreText(text='', width=300, height=100)
sizing_mode = 'fixed'
l = layout(
    [
        [info_block],
        [plot_info],
    ], sizing_mode=sizing_mode)


def get_data(cif_uuid):
    """Query the AiiDA database"""
    from aiida import load_dbenv, is_dbenv_loaded
    from aiida.backends import settings
    if not is_dbenv_loaded():
        load_dbenv(profile=settings.AIIDADB_PROFILE)
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm.data.parameter import ParameterData
    from aiida.orm.data.cif import CifData

    qb = QueryBuilder()
    qb.append(CifData, filters={'uuid': {'==': cif_uuid}})

    nresults = qb.count()
    if nresults == 0:
        plot_info.text = "No matching COF found."
        return ""
    else:
        cif = qb.one()[0]
        return cif.get_attr('filename')


def update():
    filename = get_data(cif_uuid=cif_uuid)
    info_block.text = filename


def tab_detail():
    # Make a tab with the layout
    update()
    tab = bmd.Panel(child=l, title='Detail view')
    return tab
