#!/usr/bin/env python
# coding: utf-8
import panel as pn
from os.path import join, dirname, realpath

THIS_DIR = dirname(realpath(__file__))


def fake_button(link, label, button_type):
    return """<span><a href="{link}" target="_blank">
        <button class="bk bk-btn bk-btn-{bt}" type="button">{label}</button></a></span>""".format(link=link,
                                                                                                  label=label,
                                                                                                  bt=button_type)


btn_goback = fake_button(link="results", label="Go Back to Results", button_type="primary")

info_md = open(join(THIS_DIR, "info.md")).read()

pn.extension()

t = pn.Column(width=700)
t.append(btn_goback)
t.append(pn.pane.Markdown(info_md))
t.servable()
