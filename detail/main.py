# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals
from __future__ import print_function
from os.path import dirname, join

from bokeh.layouts import layout, widgetbox
import bokeh.models as bmd
from bokeh.models.widgets import PreText
from bokeh.io import curdoc

from jsmol import JSMol
from import_db import get_cif_content
from detail.query import get_sqlite_data as get_data

html = bmd.Div(
    text=open(join(dirname(__file__), "description.html")).read(), width=800)

script_source = bmd.ColumnDataSource()

plot_info = PreText(text='', width=300, height=100)


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

    data = dict(
        labels=[str(k) for k in entry.__dict__],
        values=[str(v) for v in entry.__dict__.values()],
    )
    source = ColumnDataSource(data)

    columns = [
        TableColumn(field="labels", title="Properties"),
        TableColumn(field="values", title="Values"),
    ]
    data_table = DataTable(
        source=source, columns=columns, width=400, height=280)

    return widgetbox(data_table)


cof_name = get_name_from_url()
entry = get_data(cof_name, plot_info)

cif_str = get_cif_content(entry.filename)

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
    script="""set antialiasDisplay ON;
load data "cifstring"
{}
end "cifstring"
""".format(cif_str))

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
        [applet],
        [table_widget(entry)],
        [plot_info],
    ],
    sizing_mode=sizing_mode)

# We add this as a tab
tab = bmd.Panel(child=l, title=cof_name)
tabs = bmd.widgets.Tabs(tabs=[tab])

# Put the tabs in the current document for display
curdoc().title = "Covalent Organic Frameworks"
curdoc().add_root(layout([html, tabs]))
