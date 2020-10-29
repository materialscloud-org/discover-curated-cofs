"""Defining my color palette for visualization."""
import re
import os
import collections
import yaml
import pandas as pd
from os.path import join, dirname, realpath
from frozendict import frozendict
from functools import lru_cache
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Node, Dict, Group, WorkChainNode

TAG_KEY = "tag4"
GROUP_DIR = "discover_curated_cofs/"
CONFIG_DIR = join(dirname(realpath(__file__)), "static")
EXPLORE_URL = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")
AIIDA_LOGO_URL = "select-figure/static/images/aiida-128.png"
CO2_LOGO_URL = 'select-figure/static/images/co2-128.png'

TAG_KEY = 'tag4'


# Load and update profile for dockers
def update_config():
    """Add AiiDA profile from environment variables, if specified"""
    from aiida.manage.configuration import load_config
    from aiida.manage.configuration.profile import Profile

    profile_name = os.getenv("AIIDA_PROFILE")
    config = load_config(create=True)
    if profile_name and profile_name not in config.profile_names:
        profile = Profile(
            profile_name, {
                "database_hostname": os.getenv("AIIDADB_HOST"),
                "database_port": os.getenv("AIIDADB_PORT"),
                "database_engine": os.getenv("AIIDADB_ENGINE"),
                "database_name": os.getenv("AIIDADB_NAME"),
                "database_username": os.getenv("AIIDADB_USER"),
                "database_password": os.getenv("AIIDADB_PASS"),
                "database_backend": os.getenv("AIIDADB_BACKEND"),
                "default_user": os.getenv("default_user_email"),
                "repository_uri": "file://{}/.aiida/repository/{}".format(os.getenv("AIIDA_PATH"), profile_name),
            })
        config.add_profile(profile)
        config.set_default_profile(profile_name)
        config.store()

    return config


def load_profile():
    import aiida

    update_config()
    aiida.load_profile()


load_profile()

# Get quantities and applications
with open(join(CONFIG_DIR, "quantities.yml"), 'r') as f:
    quantities_list = yaml.load(f, Loader=yaml.SafeLoader)


def _clean(string):
    """Cleaning function for id strings.

    See https://ericmjl.github.io/pyjanitor/_modules/janitor/functions.html#clean_names
    """
    # pylint: disable=import-outside-toplevel
    from janitor.functions import _change_case, _strip_accents, _normalize_1
    string = _strip_accents(string)
    string = _change_case(string, case_type='lower')
    string = _normalize_1(string)
    string = re.sub("_+", "_", string)
    return string


for item in quantities_list:
    if 'descr' not in item.keys():
        item['descr'] = 'Description to be added!'
    if 'scale' not in item.keys():
        item['scale'] = 'linear'
    item['id'] = _clean('{}_{}_{}'.format(item['key'], item['dict'], item['unit']))

quantities = collections.OrderedDict([(q['label'], frozendict(q)) for q in quantities_list])

# keys of all quantities (features & targets)
QUANTITY_IDS = [q['id'] for k, q in quantities.items()]

with open(join(CONFIG_DIR, "applications.yml"), 'r') as f:
    applications_list = yaml.load(f, Loader=yaml.SafeLoader)

applications = collections.OrderedDict([(q['title'], frozendict(q)) for q in applications_list])

# Get an orgered dict for appl>value connection
applications_value = []
for appl in applications_list:
    applications_value.append((appl['title'] + " - " + appl['y'], {
        'dict': quantities[appl['y']]['dict'],
        'key': quantities[appl['y']]['key'],
    }))
applications_value = collections.OrderedDict(applications_value)

with open(join(CONFIG_DIR, "gasses.yml"), 'r') as f:
    gasses_list = yaml.load(f, Loader=yaml.SafeLoader)

gasses = collections.OrderedDict([(q['label'], q) for q in gasses_list])


# Get queries
#@lru_cache(maxsize=128)
def get_data_aiida(quantitites):
    """Query the AiiDA database for a list of quantities (other appl results)."""

    qb = QueryBuilder()
    qb.append(Group,
              filters={'label': {
                  'like': GROUP_DIR + "%"
              }},
              tag='g',
              project=['extras.mat_id', 'extras.name_conventional', 'extras.class_material'])

    for q in quantitites:
        qb.append(Dict,
                  project=['attributes.{}'.format(q['key'])],
                  filters={'extras.{}'.format(TAG_KEY): q['dict']},
                  with_group='g')

    return qb.all()


def get_mat_dict(mat_id):
    """Given a curated-cof label, queries the group and returns a dictionary with tags as keys and nodes as values.
    If multiple version are available qb.all()[0][0] shuld take the last one computed.
    """

    mat_dict = {}

    # get all nodes
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': GROUP_DIR + mat_id}}, tag='group')
    qb.append(Node, project=['extras.{}'.format(TAG_KEY), '*'], with_group='group')

    for k, v in qb.all():
        mat_dict[k] = v

    # get extra info
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': GROUP_DIR + mat_id}}, project=['*'])
    g = qb.all()[0][0]
    mat_dict['mat_id'] = g.extras['mat_id']
    mat_dict['name_conventional'] = g.extras['name_conventional']
    mat_dict['doi_ref'] = g.extras['doi_ref']
    mat_dict['workflow_version'] = g.extras['workflow_version']

    return mat_dict


@lru_cache(maxsize=8)
def get_isotherm_nodes(mat_id):
    """Query the AiiDA database, to get all the isotherms (Dict output of IsothermWorkChain, with GCMC calculations).
    Returning a dictionary like: {'co2: [Dict_0, Dict_1], 'h2': [Dict_0, Dict_1, Dict_2]}
    """

    # Get all the Isotherms
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'==': GROUP_DIR + mat_id}}, tag='mat_group')
    qb.append(Dict, filters={'extras.{}'.format(TAG_KEY): {'like': r'isot\_%'}}, with_group='mat_group')

    gas_dict = {}
    for x in qb.all():
        node = x[0]
        gas = node.extras[TAG_KEY].split("_")[1]
        if gas in gas_dict:
            gas_dict[gas].append(node)
        else:
            gas_dict[gas] = [node]

    # Quite diry way to get all the isotherms from an IsothermMultiTemp
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'==': GROUP_DIR + mat_id}}, tag='mat_group')
    qb.append(Dict,
              filters={'extras.{}'.format(TAG_KEY): {
                           'like': r'isotmt\_%'
                       }},
              with_group='mat_group',
              tag='isotmt_out',
              project=['extras.{}'.format(TAG_KEY)])
    qb.append(WorkChainNode, with_outgoing='isotmt_out', tag='isotmt_wc')
    qb.append(WorkChainNode,
              edge_filters={'label': {
                  'like': 'run_isotherm_%'
              }},
              with_incoming='isotmt_wc',
              tag='isot_wc')
    qb.append(Dict, edge_filters={'label': 'output_parameters'}, with_incoming='isot_wc', project=['*'])

    for x in qb.all():
        node = x[1]
        gas = x[0].split("_")[1]
        if gas in gas_dict:
            gas_dict[gas].append(node)
        else:
            gas_dict[gas] = [node]

    return gas_dict


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
    name = mat_dict['name_conventional']
    doi = mat_dict['doi_ref']
    return "<a href='https://doi.org/{}' target='_blank'>{}</a>".format(doi, name)


@lru_cache()
def get_db_nodes_dict():
    """Given return a dictionary with all the curated materials having the material label as key, and a dict of
    curated nodes as value.
    IMPROVED FOR SPEED!
    """

    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': GROUP_DIR + "%"}}, tag='g', project=['extras'])
    qb.append(Node, filters={'extras': {'has_key': TAG_KEY}}, with_group='g', project=[f'extras.{TAG_KEY}', 'uuid'])

    db_nodes_dict = {}
    for q in qb.all():  # q = [group-label, group-extras, node-tag, node-uuid]
        mat_id = q[0]['mat_id']
        if mat_id not in db_nodes_dict:
            db_nodes_dict[mat_id] = {
                'name_conventional': q[0]['name_conventional'],
                'doi_ref': q[0]['doi_ref'],
                'workflow_version': q[0]['workflow_version'],
            }
        db_nodes_dict[mat_id][q[1]] = q[2]

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
            'Original Structure': provenance_link(mat_dict['orig_cif']),
            'Vers.': mat_dict['workflow_version'],
        }

        if 'opt_cif_ddec' in mat_dict:
            new_row['Optimized Structure'] = provenance_link(mat_dict['opt_cif_ddec'])
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


# Get color palette
myRdYlGn = (  # modified from Turbo256
    '#5dfb6f',
    '#61fc6c',
    '#65fc68',
    '#69fd65',
    '#6dfd62',
    '#71fd5f',
    '#74fe5c',
    '#78fe59',
    '#7cfe56',
    '#80fe53',
    '#84fe50',
    '#87fe4d',
    '#8bfe4b',
    '#8efe48',
    '#92fe46',
    '#95fe44',
    '#98fe42',
    '#9bfd40',
    '#9efd3e',
    '#a1fc3d',
    '#a4fc3b',
    '#a6fb3a',
    '#a9fb39',
    '#acfa37',
    '#aef937',
    '#b1f836',
    '#b3f835',
    '#b6f735',
    '#b9f534',
    '#bbf434',
    '#bef334',
    '#c0f233',
    '#c3f133',
    '#c5ef33',
    '#c8ee33',
    '#caed33',
    '#cdeb34',
    '#cfea34',
    '#d1e834',
    '#d4e735',
    '#d6e535',
    '#d8e335',
    '#dae236',
    '#dde036',
    '#dfde36',
    '#e1dc37',
    '#e3da37',
    '#e5d838',
    '#e7d738',
    '#e8d538',
    '#ead339',
    '#ecd139',
    '#edcf39',
    '#efcd39',
    '#f0cb3a',
    '#f2c83a',
    '#f3c63a',
    '#f4c43a',
    '#f6c23a',
    '#f7c039',

    # just orange
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f9bc39',
    '#f9ba38',
    '#fab737',
    '#fbb537',
    '#fbb336',
    '#fcb035',
    '#fcae34',
    '#fdab33',
    '#fda932',
    '#fda631',
    '#fda330',
    '#fea12f',
    '#fe9e2e',
    '#fe9b2d',
    '#fe982c',
    '#fd952b',
    '#fd9229',
    '#fd8f28',
    '#fd8c27',
    '#fc8926',
    '#fc8624',
    '#fb8323',
    '#fb8022',
    '#fa7d20',
    '#fa7a1f',
    '#f9771e',
    '#f8741c',
    '#f7711b',
    '#f76e1a',
    '#f66b18',
    '#f56817',
    '#f46516',
    '#f36315',
    '#f26014',
    '#f15d13',
    '#ef5a11',
    '#ee5810',
    '#ed550f',
    '#ec520e',
    '#ea500d',
    '#e94d0d',
    '#e84b0c',
    '#e6490b',
    '#e5460a',
    '#e3440a',
    '#e24209',
    '#e04008',
    '#de3e08',
    '#dd3c07',
    '#db3a07',
    '#d93806',
    '#d73606',
    '#d63405',
    '#d43205',
    '#d23005',
    '#d02f04',
    '#ce2d04',
    '#cb2b03',
    '#c92903',
    '#c72803',
    '#c52602',
    '#c32402',
    '#c02302',
    '#be2102',
    '#bb1f01',
    '#b91e01',
    '#b61c01',
    '#b41b01',
    '#b11901',
    '#ae1801',
    '#ac1601',

    # just red
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501')
