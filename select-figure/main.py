"""Provenance table"""

import panel as pn
# note: the table code was moved inside pipeline_config, since bokeh1 does not support "from . import ..." and
# select-figure is not a valid package name (also from select_figure import does not work).
from pipeline_config import get_table


def fake_button(link, label, button_type):
    return """<span><a href="{link}" target="_blank">
        <button class="bk bk-btn bk-btn-{bt}" type="button">{label}</button></a></span>""".format(link=link,
                                                                                                  label=label,
                                                                                                  bt=button_type)


buttons = pn.Row()
buttons.append(
    fake_button(link="https://github.com/danieleongari/CURATED-COFs", label="GitHub repository", button_type="primary"))
buttons.append(
    fake_button(
        link=
        "https://archive.materialscloud.org/deposit/records/file?file_id=e597475b-23cd-4bca-9f6b-005e706087e4&filename=cifs_cellopt_Feb21.zip",
        label="Optimized Structures (DDEC)",
        button_type="primary"))
buttons.append(fake_button(link="figure", label="Interactive Plot", button_type="primary"))
buttons.append(fake_button(link="results", label="More Applications...", button_type="danger"))  # red button

pn.extension()

t = pn.Column()
t.append(buttons)

html_table = get_table().to_html(escape=False, classes='table table-striped table-hover')

t.append(pn.pane.HTML(html_table, style={'border': '3px solid black', 'border-radius': '10px', 'padding': '0px'}))
t.servable()
