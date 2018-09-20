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

html = bmd.Div(
    text=open(join(dirname(__file__), "description.html")).read(), width=800)

script_source = bmd.ColumnDataSource()

info_block = PreText(text='', width=500, height=100)
plot_info = PreText(text='', width=300, height=100)


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


entry = get_data(name=get_name_from_url())

info_block.text = entry.filename
cif_str = get_cif_content(entry.filename)

#s = "\n"
#for k in entry.__dict__:
#    s += "{}: {}\n".format(k, getattr(entry, k))
#info_block.text += s

info = dict(
    height="100%",
    width="100%",
    serverURL="https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php",
    use="HTML5",
    j2sPath="https://chemapps.stolaf.edu/jmol/jsmol/j2s",
    script="""
load data "cifstring"
{}
end "cifstring"
""".format(cif_str))

#    "background black;load https://dev-www.materialscloud.org/cofs/api/v2/cifs/febd2d02-5690-4a07-9013-505c9a06bc5b/content/download",
#)

applet = JSMol(
    width=600,
    height=600,
    script_source=script_source,
    info=info,
)

sizing_mode = 'fixed'
l = layout(
    [
        [applet],
        [table_widget(entry)],
        [info_block],
        [plot_info],
    ],
    sizing_mode=sizing_mode)

tab = bmd.Panel(child=l, title='Detail view')

# Create each of the tabs
tabs = bmd.widgets.Tabs(tabs=[tab])

# Put the tabs in the current document for display
curdoc().title = "Covalent Organic Frameworks"
curdoc().add_root(layout([html, tabs]))
