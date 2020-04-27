"""Provenance table"""

import os
import pandas as pd
import panel as pn
#from panel.interact import interact

from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Node, Group
from aiida import load_profile
load_profile()

try:
    this_dir = os.path.dirname(os.path.abspath(__file__)) + '/'
except:
    this_dir = ''

TAG_KEY = "tag4"


def provenance_link(uuid, label=None):
    """Return representation of provenance link."""

    if label is None:
        label = "Browse provenance\n" + str(uuid)

    logo_url = "select-figure/static/images/aiida-128.png"
    explore_url = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")
    return "<a href='{url}/details/{uuid}' target='_blank'><img src={logo_url} title='{label}' style='width: 20px;  height: auto;'></a>".format(  # noqa
        url=explore_url, uuid=str(uuid), label=label, logo_url=logo_url)


def detail_link(mat_id):
    """Return representation of provenance link."""
    logo_url = 'select-figure/static/images/co2-128.png'
    return "<a href='detail?id={}' target='_blank'><img src='{}' style='width: 20px;  height: auto;'></a>".format(
        mat_id, logo_url)


def doi_link(mat_dict):
    """Return the DOI link of the article."""
    name = mat_dict['orig_cif'].extras['name_conventional']
    doi = mat_dict['orig_cif'].extras['doi_ref']
    return "<a href='https://doi.org/{}' target='_blank'>{}</a>".format(doi, name)


def get_db_nodes_dict():
    """Given return a dictionary with all the curated materials having the material label as key, and a dict of
    curated nodes as value."""

    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': r'curated-cof%'}}, tag='curated_groups', project=['label'])
    qb.append(Node, filters={'extras': {'has_key': TAG_KEY}}, with_group='curated_groups', project=['*'])

    db_nodes_dict = {}
    for q in qb.all():
        mat_label = q[0].split("_")[1]
        if mat_label not in db_nodes_dict:
            db_nodes_dict[mat_label] = {}
        n = q[1]
        db_nodes_dict[mat_label][n.extras[TAG_KEY]] = n

    return db_nodes_dict


def get_table():
    """Get the entries for the right table of select-figure."""

    pd.set_option('max_colwidth', 1000)

    df = pd.DataFrame(columns=[  # Set the order of the columns
        'CURATED-COFs ID', 'Article', 'Original Structure', 'Optimized Structure', 'CCS Workflow', 'Vers.'
    ])

    db_nodes_dict = get_db_nodes_dict()

    for mat_id, mat_dict in db_nodes_dict.items():
        new_row = {
            'CURATED-COFs ID': mat_id,
            'Article': doi_link(mat_dict),
            'Original Structure': provenance_link(mat_dict['orig_cif'].uuid),
            'Vers.': mat_dict['orig_cif'].extras['workflow_version'],
        }

        if 'opt_cif_ddec' in mat_dict:
            new_row['Optimized Structure'] = provenance_link(mat_dict['opt_cif_ddec'].uuid)
        else:
            new_row['Optimized Structure'] = "N/A"

        if 'appl_pecoal' in mat_dict:
            new_row['CCS Workflow'] = detail_link(mat_id)
        else:
            new_row['CCS Workflow'] = "N/A"

        df = df.append(new_row, ignore_index=True)

    df = df.sort_values(by=['CURATED-COFs ID'])
    df = df.reset_index(drop=True)
    df.index += 1
    return df


def fake_button(link, label):
    return """<span><a href="{link}" target="_blank">
        <button class="bk bk-btn bk-btn-primary" type="button">{label}</button></a></span>""".format(link=link,
                                                                                                     label=label)


buttons = pn.Row()
buttons.append(fake_button(link="https://github.com/danieleongari/CURATED-COFs", label="GitHub repository"))
buttons.append(
    fake_button(link="https://archive.materialscloud.org/file/2019.0034/v2/cifs_cellopt_Dec19.zip",
                label="Optimized Structures (DDEC)"))

pn.extension()

t = pn.Column()
t.append(buttons)
t.append(get_table().to_html(escape=False))
t.servable()
