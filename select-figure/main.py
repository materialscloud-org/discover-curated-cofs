# coding: utf-8
"""Provenance table"""

import os
import pandas

from aiida import load_profile
load_profile()

try:
    this_dir = os.path.dirname(os.path.abspath(__file__)) + '/'
except:
    this_dir = ''


def provenance_link(uuid, label=None):
    """Return representation of provenance link."""
    import os

    if label is None:
        label = "Browse provenance\n" + str(uuid)

    logo_url = "select-figure/static/images/aiida-128.png"
    explore_url = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")
    return "<a href='{url}/details/{uuid}' target='_blank'><img src={logo_url} title='{label}' style='width: 20px;  height: auto;'></a>".format(
        url=explore_url, uuid=str(uuid), label=label, logo_url=logo_url)


def detail_link(label):
    """Return representation of provenance link."""
    logo_url = 'select-figure/static/images/co2-128.png'
    return "<a href='detail?id={l}' target='_blank'><img src='{u}' style='width: 20px;  height: auto;'></a>".format(
        l=label, u=logo_url)


def get_paper_link(label, name, df):
    """Return link of the article."""
    paper_id = "p{:s}".format(label[:4])
    paper_row = df.loc[df["CURATED-COFs paper ID"] == paper_id]
    link_paper = "https://doi.org/" + paper_row["DOI"].values[0]
    return "<a href='{}' target='_blank'>{}</a>".format(link_paper, name)


def get_table():
    """Get the entries for the right table of select-figure

    TODO: this section needs to be fixed if more version are present for the same COF!
    """

    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import WorkFunctionNode, Node, Group
    pandas.set_option('max_colwidth', 1000)

    # import cof-frameworks as DataFrame
    df = pandas.read_csv(this_dir + "../data/cof-frameworks.csv")
    df_papers = pandas.read_csv(this_dir + "../data/cof-papers.csv")

    # get nodes (once to make it efficient): load group, get uuid if existing, make a dicts label:uuid
    # note: this works for pe_out because if it has pe_out it has also the previous two!
    qb = QueryBuilder()
    qb.append(Group, project=['label'], filters={'label': {'like': 'curated-cof_%_v%'}}, tag='curated-cof')
    qb.append(Node, project=['uuid'], filters={'extras.curated-cof_tag': 'orig_cif'}, with_group='curated-cof')
    uuid_dict_orig = {v[0].split("_")[1]: v[-1] for v in qb.all()}
    version_dict = {v[0].split("_")[1]: v[0].split("_")[-1] for v in qb.all()}
    qb.append(Node, project=['uuid'], filters={'extras.curated-cof_tag': 'opt_cif_ddec'}, with_group='curated-cof')
    uuid_dict_opt = {v[0].split("_")[1]: v[-1] for v in qb.all()}
    qb.append(Node, project=['uuid'], filters={'extras.curated-cof_tag': 'pe_out'}, with_group='curated-cof')
    uuid_dict_pe = {v[0].split("_")[1]: v[-1] for v in qb.all()}

    # search if orig_cif (ref), opt_cif and pe_out are present in the aiida database as nodes and return a new df
    paper_link = []
    orig_cif = []
    opt_cif = []
    detail = []
    version = []

    for index, row in df.iterrows():
        label = row['CURATED-COFs ID']
        paper_link += [get_paper_link(label, row['Name'], df_papers)]

        try:
            orig_cif += [provenance_link(uuid_dict_orig[label])]
            version += [version_dict[label]]
        except KeyError:
            orig_cif += ["N/A"]
            version += ["N/A"]

        try:
            opt_cif += [provenance_link(uuid_dict_opt[label])]
        except KeyError:
            opt_cif += ["N/A"]

        try:
            uuid_dict_pe[label]  #will fail if absent
            detail += [detail_link(label)]
        except KeyError:
            detail += ["N/A"]
    df['Article'] = pandas.Series(paper_link, index=df.index)
    df['Original Structure'] = pandas.Series(orig_cif, index=df.index)
    df['Optimized Structure'] = pandas.Series(opt_cif, index=df.index)
    df['CCS Workflow'] = pandas.Series(detail, index=df.index)
    df['Vers.'] = pandas.Series(version, index=df.index)
    return df[['CURATED-COFs ID', 'Article', 'Original Structure', 'Optimized Structure', 'CCS Workflow', 'Vers.']]


"""Buttons"""
import panel as pn


def fake_button(link, label):
    return """<span><a href="{link}" target="_blank">
        <button class="bk bk-btn bk-btn-primary" type="button">{label}</button></a></span>""".format(link=link,
                                                                                                     label=label)


buttons = pn.Row()
buttons.append(fake_button(link="https://github.com/danieleongari/CURATED-COFs", label="GitHub repository"))
buttons.append(
    fake_button(link="https://archive.materialscloud.org/file/2019.0034/v2/cifs_cellopt_Dec19.zip",
                label="Optimized Structures (DDEC)"))

import panel as pn
from panel.interact import interact

pn.extension()

t = pn.Column()
t.append(buttons)
t.append(get_table().to_html(escape=False))
t.servable()
