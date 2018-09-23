# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals
from __future__ import print_function
import collections
from os.path import dirname, join

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
import bokeh.models as bmd
from bokeh.palettes import Viridis256
from bokeh.models.widgets import RangeSlider, Select, Button, PreText
from bokeh.io import curdoc

from config import quantities, bondtype_dict, presets
from figure.query import get_data_sqlite as get_data
from figure.query import data_empty

html = bmd.Div(
    text=open(join(dirname(__file__), "description.html")).read(), width=800)

redraw_plot = False


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

    # reset all filters
    for q in quantities:
        sliders_dict[q].value = quantities[q]['range']

    # apply some filters
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


def on_slider_change(attr, old, new):
    btn_plot.button_type = 'primary'


# range sliders
# pylint: disable=redefined-builtin
def get_slider(desc, range, default=None):
    if default is None:
        default = range
    slider = RangeSlider(
        title=desc, start=range[0], end=range[1], value=default, step=0.1)

    slider.on_change('value', on_slider_change)
    return slider


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
btn_plot = Button(label='Plot', button_type='primary')
info_block = PreText(text='', width=500, height=100)
plot_info = PreText(text='', width=300, height=100)

source = bmd.ColumnDataSource(data=data_empty)
hover = bmd.HoverTool(tooltips=[])
tap = bmd.TapTool()


def create_plot():
    """Creates scatter plot.

    Note: While it is usually enough to update the data source, redrawing the
    plot is needed for bond_type coloring, when the colormap needs to change
    and the colorbar is removed.
    """
    global source
    p_new = figure(
        plot_height=600,
        plot_width=700,
        toolbar_location='below',
        tools=[
            'pan',
            'wheel_zoom',
            'box_zoom',
            'save',
            'reset',
            hover,
            tap,
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
        paper_palette = list(bondtype_dict.values())
        fill_color = factor_cmap(
            'color', palette=paper_palette, factors=bondtypes)
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


# pylint: disable=unused-argument
def check_uniqueness(attr, old, new):
    selected = [inp_x.value, inp_y.value, inp_clr.value]
    unique = list(set(selected))
    if len(unique) < len(selected):
        double = [i for i in selected if i in unique or unique.remove(i)]
        double_str = ", ".join([quantities[d]['label'] for d in double])
        plot_info.text = "Warning: {} doubly selected.".format(double_str)
        btn_plot.button_type = 'danger'

    else:
        plot_info.text = ""
        btn_plot.button_type = 'primary'


def update():
    global redraw_plot, source

    update_legends(l)

    projections = [inp_x.value, inp_y.value, inp_clr.value, 'name', 'filename']

    source.data = get_data(projections, sliders_dict, quantities, plot_info)

    #if redraw_plot:
    if True:  # pylint: disable=using-constant-test
        figure = create_plot()
        #TO DO: for some reason this destroys the coupling to source.data
        # to figure out why (and then restrict this to actual redrawing scenarios)
        l.children[0].children[1] = figure
        redraw_plot = False

    update_legends(l)
    plot_info.text += " done!"
    btn_plot.button_type = 'success'
    return


btn_plot.on_click(update)


# pylint: disable=unused-argument
def on_change_clr(attr, old, new):
    """Remember to redraw plot next time, when necessary.

    When switching between bond_type color and something else,
    the plot needs to be redrawn.
    """
    global redraw_plot
    if (new == 'bond_type' or old == 'bond_type') and new != old:
        redraw_plot = True

    check_uniqueness(attr, old, new)


inp_x.on_change('value', check_uniqueness)
inp_y.on_change('value', check_uniqueness)
inp_clr.on_change('value', on_change_clr)

# Create a panel with a new layout
sizing_mode = 'fixed'
inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout(
    [
        [inputs, p],
        [info_block],
    ], sizing_mode=sizing_mode)
update()

# Create each of the tabs
tab = bmd.Panel(child=l, title='Scatter plot')
tabs = bmd.widgets.Tabs(tabs=[tab])

# Put the tabs in the current document for display
curdoc().title = "Covalent Organic Frameworks"
curdoc().add_root(layout([html, tabs]))
