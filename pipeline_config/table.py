"""Provenance table"""

import os
import pandas as pd
from functools import lru_cache

TAG_KEY = "tag4"
GROUP_DIR = "discover_curated_cofs/"
EXPLORE_URL = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")
AIIDA_LOGO_URL = "select-figure/static/images/aiida-128.png"
CO2_LOGO_URL = 'select-figure/static/images/co2-128.png'


def provenance_link(uuid, label=None):
    """Return representation of provenance link."""

    if label is None:
        label = "Browse provenance\n" + str(uuid)

    return "<a href='{url}/details/{uuid}' target='_blank'><img class='provenance-logo' src={logo_url} title='{label}'></a>".format(  # noqa
        url=EXPLORE_URL, uuid=str(uuid), label=label, logo_url=AIIDA_LOGO_URL)


def detail_link(mat_id):
    """Return representation of workflow link."""
    return "<a href='detail?mat_id={}' target='_blank'><img class='provenance-logo' src='{}'></a>".format(
        mat_id, CO2_LOGO_URL)


def doi_link(mat_dict):
    """Return the DOI link of the article."""
    name = mat_dict['orig_cif'].extras['name_conventional']
    doi = mat_dict['orig_cif'].extras['doi_ref']
    return "<a href='https://doi.org/{}' target='_blank'>{}</a>".format(doi, name)


@lru_cache()
def get_db_nodes_dict():
    """Given return a dictionary with all the curated materials having the material label as key, and a dict of
    curated nodes as value."""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Node, Group
    from figure.config import load_profile
    load_profile()

    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': GROUP_DIR + "%"}}, tag='g', project=['label'])
    qb.append(Node, filters={'extras': {'has_key': TAG_KEY}}, with_group='g', project=['*'])

    db_nodes_dict = {}
    for q in qb.all():
        mat_label = q[0].split("/")[1]
        if mat_label not in db_nodes_dict:
            db_nodes_dict[mat_label] = {}
        n = q[1]
        db_nodes_dict[mat_label][n.extras[TAG_KEY]] = n

    return db_nodes_dict


@lru_cache()
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
