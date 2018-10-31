# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals
from __future__ import print_function
from os.path import dirname, join
from copy import copy
from collections import OrderedDict
import json

from bokeh.layouts import layout, widgetbox
import bokeh.models as bmd
from bokeh.models.widgets import PreText, Button
from bokeh.io import curdoc

from jsmol import JSMol
from import_db import get_cif_content
from detail.query import get_sqlite_data as get_data

html = bmd.Div(
    text=open(join(dirname(__file__), "description.html")).read(), width=800)

download_js = open(join(dirname(__file__), "static", "download.js")).read()

script_source = bmd.ColumnDataSource()

plot_info = PreText(text='', width=300, height=100)

btn_download_table = Button(label="Download json", button_type="primary")
btn_download_cif = Button(label="Download cif", button_type="primary")


def get_name_from_url():
    args = curdoc().session_context.request.arguments
    try:
        name = args.get('name')[0]
        if isinstance(name, bytes):
            name = name.decode()
    except (TypeError, KeyError):
        name = 'linker91_CH_linker92_N_clh_relaxed'

    return name


def table_widget(entry):
    from bokeh.models import ColumnDataSource
    from bokeh.models.widgets import DataTable, TableColumn

    entry_dict = copy(entry.__dict__)
    for k, v in entry_dict.items():
        if k == 'id' or k == '_sa_instance_state':
            del entry_dict[k]

        # use _units keys to rename corresponding quantity
        if k[-6:] == '_units':
            prop = k[:-6]
            new_key = "{} [{}]".format(prop, entry_dict[k])
            del entry_dict[k]
            entry_dict[new_key] = entry_dict.pop(prop)

    # order entry dict
    entry_dict = OrderedDict(
        [(k, entry_dict[k]) for k in sorted(list(entry_dict.keys()))])

    data = dict(
        labels=[str(k) for k in entry_dict],
        values=[str(v) for v in entry_dict.values()],
    )
    source = ColumnDataSource(data)

    columns = [
        TableColumn(field="labels", title="Properties"),
        TableColumn(field="values", title="Values"),
    ]
    data_table = DataTable(
        source=source,
        columns=columns,
        width=500,
        height=570,
        index_position=None,
        fit_columns=False)

    json_str = json.dumps(entry_dict, indent=2)
    #btn_download_table.callback = bmd.CustomJS(
    #    args=dict(string=json_str, filename=entry_dict['name'] + '.json'),
    #    code=download_js)

    return widgetbox(data_table)


cof_name = get_name_from_url()
entry = get_data(cof_name, plot_info)


def get_cif_content(name):
    #name = "linker100_CH2_linker105_NH_pts_relaxed.cif"
    url =  "https://object.cscs.ch/v1/AUTH_b1d80408b3d340db9f03d373bbde5c1e/discover-cofs/structures/{}".format(name)
    import requests
    data = requests.get(url)
    return data.content



cif_str = get_cif_content(entry.filename)


# working url:
# https://object.cscs.ch/v1/AUTH_b1d80408b3d340db9f03d373bbde5c1e/discover-cofs/structures/linker100_CH2_linker105_NH_pts_relaxed.cif

def get_cif_url(name):
    name = "linker100_CH2_linker105_NH_pts_relaxed.cif"
    url =  "https://object.cscs.ch/v1/AUTH_b1d80408b3d340db9f03d373bbde5c1e/discover-cofs/structures/{}".format(name)
    return url

info = dict(
    height="100%",
    width="100%",
    use="HTML5",
    #serverURL="https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php",
    #j2sPath="https://chemapps.stolaf.edu/jmol/jsmol/j2s",
    #serverURL="https://www.materialscloud.org/discover/scripts/external/jsmol/php/jsmol.php",
    #j2sPath="https://www.materialscloud.org/discover/scripts/external/jsmol/j2s",
    serverURL="detail/static/jsmol/php/jsmol.php",
    j2sPath="detail/static/jsmol/j2s",
    #script='set antialiasDisplay ON; load cif::{};'.format(get_cif_url(entry.filename))
    script="""set antialiasDisplay ON;
load data "cifstring"
{}
end "cifstring"
""".format(cif_str)
)

#btn_download_cif.callback = bmd.CustomJS(
#    args=dict(string="", filename=entry.filename), code=download_js)

applet = JSMol(
    width=600,
    height=600,
    script_source=script_source,
    info=info,
    js_url="detail/static/jsmol/JSmol.min.js",
)

sizing_mode = 'fixed'
l = layout(
    [
        [
            [[applet], [btn_download_cif]],
            [[table_widget(entry)], []],
        ],
        [plot_info],
    ],
    sizing_mode=sizing_mode)

# We add this as a tab
tab = bmd.Panel(child=l, title=cof_name)
tabs = bmd.widgets.Tabs(tabs=[tab])

# Put the tabs in the current document for display
curdoc().title = "Covalent Organic Frameworks"
curdoc().add_root(layout([html, tabs]))
