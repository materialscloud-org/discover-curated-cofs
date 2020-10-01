"""Provenance table"""

import panel as pn
# note: the table code was moved inside pipeline_config, since bokeh1 does not support "from . import ..." and
# select-figure is not a valid package name (also from select_figure import does not work).
from pipeline_config.table import get_table


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
        "https://archive.materialscloud.org/record/file?filename=cifs_cellopt_Jun20.zip&file_id=f1843d6a-06de-45c5-94d0-fd24925aa030&record_id=519",
        label="Optimized Structures (DDEC)",
        button_type="primary"))
buttons.append(fake_button(link="results", label="More Applications...", button_type="danger"))  # red button

pn.extension()

t = pn.Column()
t.append(buttons)
t.append(get_table().to_html(escape=False))
t.servable()
