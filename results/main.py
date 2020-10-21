#!/usr/bin/env python
# coding: utf-8
import bokeh.plotting as bpl
import bokeh.models as bmd
from bokeh.io import curdoc
import panel as pn
from pipeline_config import myRdYlGn, get_data_aiida, quantities, applications
from aiida import load_profile
load_profile()


def get_mat_id():
    """Get structure label from URL parameter 'ml'"""
    try:
        name = curdoc().session_context.request.arguments.get('ml')[0]
        if isinstance(name, bytes):
            mat_id = name.decode()
    except (TypeError, KeyError, AttributeError):
        mat_id = None

    return mat_id


def rank_materials(x, y, wx, wy):
    """Rank materials according to the xy values and their weight: 1 top performer, len(x) worst"""
    scores = []
    for xval, yval in zip(x, y):
        s = xval * wx + yval * wy
        scores.append(s)
    sorted_scores = sorted(scores)
    return [len(scores) - sorted_scores.index(v) for v in scores]


def get_plot(appl):  #pylint: disable=too-many-locals
    """Make the bokeh plot for a given application.

    1. read important metrics from applications.yml
    2. read metadata for thes metricy in quantities.yml
    3. query the AiiDA database for values
    4. rank materials according to their performance
    5. generate the plot and return a message stating the number of found materials
    """

    # Query for results
    q_list = tuple([quantities[label] for label in [appl['x'], appl['y']]])
    results_wnone = get_data_aiida(q_list)  #[[id_material, name_material, class_material, xval, yval]]

    # Clean the query from None values projections
    results = []
    for l in results_wnone:
        if None not in l:
            results.append(l)

    # Prepare data for plotting
    nresults = len(results)
    if not results:
        results = [['none', 'none', 'none', 0, 0]]
        msg = "No materials found"
    else:
        msg = "{} materials shown".format(nresults)

    mat_id, name, class_mat, x, y = zip(*results)

    x = list(map(float, x))
    y = list(map(float, y))
    rank = rank_materials(x, y, appl['wx'], appl['wy'])

    # Setup plot
    hover = bmd.HoverTool()
    hover.tooltips = [
        ("name", "@name"),
        ("MAT_ID", "@mat_id"),
        (q_list[0]["label"], "@x {}".format(q_list[0]["unit"])),
        (q_list[1]["label"], "@y {}".format(q_list[1]["unit"])),
        ('ranking', '@color'),
    ]

    tap = bmd.TapTool()
    p = bpl.figure(
        plot_height=600,
        plot_width=600,
        toolbar_location="right",  # choose: above, below, right, left
        tools=[
            'pan',
            'wheel_zoom',
            'box_zoom',
            'save',
            'reset',
            hover,
            tap,
        ],
        active_drag='box_zoom',
        output_backend='webgl',
        x_axis_type=q_list[0]['scale'],
        y_axis_type=q_list[1]['scale'],
        x_axis_label="{} [{}]".format(q_list[0]["label"], q_list[0]["unit"]),
        y_axis_label="{} [{}]".format(q_list[1]["label"], q_list[1]["unit"]),
    )

    tap.callback = bmd.OpenURL(url="details?mat_id=@mat_id")

    cmap = bmd.LinearColorMapper(palette=myRdYlGn)
    fill_color = {'field': 'color', 'transform': cmap}

    source = bmd.ColumnDataSource(data={
        'mat_id': mat_id,
        'name': name,
        'class_mat': class_mat,
        'x': x,
        'y': y,
        'color': rank,
    })
    p.circle(x='x', y='y', size=10, source=source, fill_color=fill_color, muted_alpha=0.2)

    #cbar = bmd.ColorBar(color_mapper=cmap, location=(0, 0))
    #p.add_layout(cbar, 'right') #show colorbar

    return p, msg


def fake_button(link, label, button_type):
    return """<span><a href="{link}" target="_blank">
        <button class="bk bk-btn bk-btn-{bt}" type="button">{label}</button></a></span>""".format(link=link,
                                                                                                  label=label,
                                                                                                  bt=button_type)


def on_click_highlight(event):  # pylint: disable=unused-argument
    label = inp_label.value

    for _title, pmsg in plots.items():
        plot, _msg = pmsg
        source = plot.renderers[0].data_source
        index_list = []
        for i, x in enumerate(source.data['name']):
            if x.split()[0] == label:
                index_list.append(i)
        if index_list:
            source.selected.indices = index_list
            btn_label.button_type = 'success'
        else:
            btn_label.button_type = 'warning'
            source.selected.indices = []


pn.extension()

inp_label = pn.widgets.TextInput(name='Insert the name of a material', value="COF-5")
btn_label = pn.widgets.Button(name='Highlight', button_type='primary')
btn_label.on_click(on_click_highlight)

# Setting the layout of the page
head_hp = 160  # hp: height in px
appl_hp = 400
head_hg = 5  # hg: height in the grid
appl_hg = 10
marg_hg = 2
nappl = len(applications)
gspec = pn.GridSpec(height=head_hp + appl_hp * nappl, width=1200)

# head: title on the left, highlight button on the right
gspec[0:head_hg, 0:12] = pn.pane.HTML("""
<h2>Showing all the applications</h2>
<ul>
  <li>Color: from best materials (green) to worst (red)
  <li>Insert the name of any material in this box to see it highlighted
  <li>Read about the <a href="info">Info & Methods</a> used to produce these results
  <li>The project continues on <a href="https://matscreen.com/">MatScreen.com</a>
</ul>
""")
gspec[0:head_hg, 12:17] = pn.Column(inp_label, btn_label)

# applications: plot on the left, description on the right
plots = {title: get_plot(val) for title, val in applications.items()}
i = 0
for title, val in applications.items():
    plot, msg = plots[title]
    start_hg = head_hg + i * (appl_hg + marg_hg)
    gspec[start_hg:start_hg + appl_hg, 1:10] = plot
    html_text = """<h3>{title}</h3>{descr}<p><i>{msg}</i></p> """.format(title=val['title'],
                                                                         msg=msg,
                                                                         descr=val['descr'])
    gspec[start_hg:start_hg + appl_hg, 11:25] = pn.pane.HTML(html_text)
    gspec[start_hg + appl_hg:start_hg + appl_hg + marg_hg, :] = pn.pane.HTML()  #margin
    i += 1

gspec.servable()
