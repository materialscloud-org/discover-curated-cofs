# -*- coding: utf-8 -*-
from __future__ import print_function
import collections
from os.path import dirname, join

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
import bokeh.models as bmd
from bokeh.palettes import Viridis256, Spectral5
from bokeh.models.widgets import RangeSlider, Select, Button, PreText
from bokeh.io import curdoc

from config import quantities, bondtype_dict, presets

html = bmd.Div(
    text=open(join(dirname(__file__), "description.html")).read(), width=800)

# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals


def get_preset_label_from_url():
    # get preset for figure from arguments
    args = curdoc().session_context.request.arguments
    try:
        preset_label = args.get('preset')[0]
    except (TypeError, KeyError):
        preset_label = 'default'

    return preset_label


# pylint: disable=unused-argument
def load_preset(attr, old, new):
    """Load preset and update sliders/plot accordingly"""
    # get figure from arguments
    preset = presets[new]
    inp_x.value = preset['x']
    inp_y.value = preset['y']

    if 'clr' in preset.keys():
        inp_clr.value = preset['clr']

    slx = sliders_dict[preset['x']]
    if 'x_min' in preset.keys():
        slx.value = (preset['x_min'], slx.value[1])
    if 'x_max' in preset.keys():
        slx.value = (slx.value[0], preset['x_max'])


inp_preset = Select(
    title='Preset',
    options=list(presets.keys()),
    value=get_preset_label_from_url())
inp_preset.on_change('value', load_preset)

# quantities
nq = len(quantities)
bondtypes = list(bondtype_dict.keys())
bondtype_colors = list(bondtype_dict.values())


# range sliders
# pylint: disable=redefined-builtin
def get_slider(desc, range, default=None):
    if default is None:
        default = range
    return RangeSlider(
        title=desc, start=range[0], end=range[1], value=default, step=0.1)


sliders_dict = collections.OrderedDict()
for k, v in quantities.items():
    desc = "{} [{}]".format(v['label'], v['unit'])
    if 'default' not in v.keys():
        v['default'] = None

    sliders_dict[k] = get_slider(desc, v['range'], v['default'])

# quantity selectors
preset_url = presets[get_preset_label_from_url()]
plot_options = [(k, v['label']) for k, v in quantities.items()]
inp_x = Select(title='X', options=plot_options, value=preset_url['x'])
inp_y = Select(title='Y', options=plot_options, value=preset_url['y'])
#inp_clr = Select(title='Color', options=plot_options, value=preset_url['clr'])
inp_clr = Select(
    title='Color',
    options=plot_options + [('bond_type', 'Bond type')],
    value=preset_url['clr'])

# plot button, output, graph
btn_plot = Button(label='Plot')
info_block = PreText(text='', width=500, height=100)
plot_info = PreText(text='', width=300, height=100)

data_empty = dict(x=[0], y=[0], uuid=['1234'], color=[0], name=['no data'])
source = bmd.ColumnDataSource(data=data_empty)
hover = bmd.HoverTool(tooltips=[])
tap = bmd.TapTool()


def create_plot():
    """Creates scatter plot.

    This is needed to redraw the plot for the bond_type coloring,
    when the colormap needs to change and the colorbar is removed.
    """
    p_new = figure(
        plot_height=600,
        plot_width=700,
        toolbar_location='below',
        tools=[
            'pan', 'wheel_zoom', 'save', 'reset', 'zoom_in', 'zoom_out', hover,
            tap
        ],
        active_scroll='wheel_zoom',
        output_backend='webgl',
        title='',
        title_location='right',
    )
    p_new.title.align = 'center'
    p_new.title.text_font_size = '10pt'
    p_new.title.text_font_style = 'italic'

    if inp_clr.value == 'bond_type':
        from bokeh.transform import factor_cmap
        fill_color = factor_cmap('color', palette=Spectral5, factors=bondtypes)
        p_new.circle(
            'x',
            'y',
            size=10,
            source=source,
            fill_color=fill_color,
            legend='color')

    else:
        cmap = bmd.LinearColorMapper(palette=Viridis256)
        fill_color = {'field': 'color', 'transform': cmap}
        p_new.circle('x', 'y', size=10, source=source, fill_color=fill_color)
        cbar = bmd.ColorBar(color_mapper=cmap, location=(0, 0))
        #cbar.color_mapper = bmd.LinearColorMapper(palette=Viridis256)
        p_new.add_layout(cbar, 'right')

    return p_new


p = create_plot()

controls = [inp_preset] + [v for k, v in sliders_dict.items()
                           ] + [inp_x, inp_y, inp_clr, btn_plot, plot_info]

#def update_tap(source=source, window=None):
#    info_block.text = "here"
#    print("here")
#    print(source)
#    print(cb_obj.value)


def update_legends(ly):

    q_x = quantities[inp_x.value]
    q_y = quantities[inp_y.value]
    p = ly.children[0].children[1]

    #title = "{} vs {}".format(q_x["label"], q_y["label"])
    xlabel = "{} [{}]".format(q_x["label"], q_x["unit"])
    ylabel = "{} [{}]".format(q_y["label"], q_y["unit"])
    xhover = (q_x["label"], "@x {}".format(q_x["unit"]))
    yhover = (q_y["label"], "@y {}".format(q_y["unit"]))

    if inp_clr.value == 'bond_type':
        clr_label = "Bond type"
        hover.tooltips = [
            ("name", "@name"),
            xhover,
            yhover,
            ("Bond type", "@color"),
        ]
    else:
        q_clr = quantities[inp_clr.value]
        clr_label = "{} [{}]".format(q_clr["label"], q_clr["unit"])
        hover.tooltips = [
            ("name", "@name"),
            xhover,
            yhover,
            (q_clr["label"], "@color {}".format(q_clr["unit"])),
        ]

    p.xaxis.axis_label = xlabel
    p.yaxis.axis_label = ylabel
    p.title.text = clr_label

    url = "detail?name=@name"
    tap.callback = bmd.OpenURL(url=url)
    #tap.callback = bmd.CustomJS.from_py_func(update_tap)
    #tap.callback = bmd.CustomJS(code="""console.info("hello TapTool")""")

    #p.toolbar.active_hover = hover


def update(ly=None):

    if ly is None:
        ly = curdoc().roots[0]
    update_legends(ly)
    #source.data = get_data_aiida()
    source.data = get_data()

    if redraw_plot:
        ly.children[0].children[1] = create_plot()

    update_legends(ly)
    return


#@app.callback(
#    dash.dependencies.Output('hover_info', 'children'),
#    [dash.dependencies.Input('scatter_plot', 'hoverData')])
#def update_text(hoverData):
#    if hoverData is None:
#        return ""
#
#    uuid = hoverData['points'][0]['customdata']
#    rest_url = 'http://localhost:8000/explore/sssp/details/'
#
#    node = load_node(uuid)
#    attrs = node.get_attrs()
#    s = "[View AiiDA Node]({})\n".format(rest_url+uuid)
#    for k,v in attrs.items():
#        if 'units' in k:
#            continue
#        s += " * {}: {}\n".format(k,v)
#
#    return s


def get_data():
    """Query the database.
    
    Note: For efficiency, this uses the the sqlalchemy.sql interface which does
    not go via the (more convenient) ORM.
    """
    from import_db import automap_table, engine
    from sqlalchemy.sql import select

    Table = automap_table(engine)

    selections = []
    for label in [inp_x.value, inp_y.value, inp_clr.value, 'name', 'filename']:
        selections.append(getattr(Table, label))

    filters = None
    for k, v in sliders_dict.items():
        if not v.value == quantities[k]['range']:
            filter = getattr(Table, k).between(v.value[0], v.value[1])
            if filters is None:
                filters = filter
            else:
                filters = filters._and(filter)  # pylint: disable=protected-access

    s = select(selections).where(filters)

    results = engine.connect().execute(s).fetchall()

    nresults = len(results)
    if not results:
        plot_info.text = "No matching COFs found."
        return data_empty

    plot_info.text = "{} COFs found. Plotting...".format(nresults)

    # x,y position
    x, y, clrs, names, filenames = zip(*results)
    plot_info.text = "{} COFs queried".format(nresults)
    x = list(map(float, x))
    y = list(map(float, y))

    if inp_clr.value == 'bond_type':
        #clrs = map(lambda clr: bondtypes.index(clr), clrs)
        clrs = list(map(str, clrs))
    else:
        clrs = list(map(float, clrs))

    return dict(x=x, y=y, filename=filenames, color=clrs, name=names)


def get_data_aiida():
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
        project=[
            'attributes.' + inp_x.value, 'attributes.' + inp_y.value,
            'attributes.' + inp_clr.value, 'uuid', 'attributes.name',
            'extras.cif_uuid'
        ],
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

    if inp_clr.value == 'bond_type':
        #clrs = map(lambda clr: bondtypes.index(clr), clrs)
        clrs = map(str, clrs)
    else:
        clrs = map(float, clrs)

    return dict(x=x, y=y, uuid=cif_uuids, color=clrs, name=names)


btn_plot.on_click(update)


def tab_plot():
    # Create a panel with a new layout
    sizing_mode = 'fixed'
    inputs = widgetbox(*controls, sizing_mode=sizing_mode)
    ly = layout(
        [
            [inputs, p],
            [info_block],
        ], sizing_mode=sizing_mode)
    update(ly=ly)

    return bmd.Panel(child=ly, title='Scatter plot')


redraw_plot = False


# pylint: disable=unused-argument
def on_change_clr(attr, old, new):
    """Remember to redraw plot next time, when necessary.

    When switching between bond_type color and something else,
    the plot needs to be redrawn.
    """
    global redraw_plot
    if (new == 'bond_type' or old == 'bond_type') and new != old:
        redraw_plot = True


inp_clr.on_change('value', on_change_clr)

# Create each of the tabs
tabs = bmd.widgets.Tabs(tabs=[tab_plot()])
ly = layout([html, tabs])

# Put the tabs in the current document for display
curdoc().title = "Covalent Organic Frameworks"
curdoc().add_root(ly)
