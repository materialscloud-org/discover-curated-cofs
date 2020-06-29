#!/usr/bin/env python

import sys
import os
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group, CifData
from aiida.tools.importexport import export_zip

from figure.config import load_profile
load_profile()

TAG_KEY = "tag4"
GROUP_DIR = "discover_curated_cofs/"
EXPORT_NAME = "export_discovery_cof_23Jun20.aiida"
CIFS_DIR = "./cifs_cellopt/"

EXPORT = True
PRINT_OPT_CIFS = True
CLEAR = True

desired_nodes = ['orig_cif', 'orig_zeopp', 'dftopt', 'opt_cif_ddec', 'opt_zeopp', 'isot_co2', 'isot_n2', 'appl_pecoal']


def delete_old_groups():
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': GROUP_DIR + "%"}})
    if qb.all():
        print("Groups '{}' found, deleting...".format(GROUP_DIR))
        for q in qb.all():
            group = q[0]
            group.clear()
            Group.objects.delete(group.pk)


# Clear and delete old groups
delete_old_groups()

# Query for all the CURATED-COFs
qb = QueryBuilder()
qb.append(Group, filters={'label': {'like': r'curated-cof\_%\_v%'}})

# Create groups for each and fill them with desired nodes
print("Finding nodes with tag:", desired_nodes)

all_new_groups = []
for q in qb.all():
    ref_group = q[0]
    mat_id = ref_group.label.split("_")[1]
    new_group = Group(label=GROUP_DIR + mat_id).store()
    all_new_groups.append(new_group)
    left_nodes = desired_nodes.copy()
    for node in ref_group.nodes:
        if TAG_KEY not in node.extras:
            sys.exit("WARNING: node <{}> has no extra '{}'".format(node.id, TAG_KEY))
        if node.extras[TAG_KEY] in left_nodes:
            new_group.add_nodes(node)
            left_nodes.remove(node.extras[TAG_KEY])
    print(mat_id, "missing nodes: ", left_nodes)

# Export these groups
if EXPORT:
    print(" ++++++ Exporting Nodes ++++++ ")
    kwargs = {
        # general
        'outfile': EXPORT_NAME,
        'overwrite': True,
        'silent': False,
        'use_compression': True,
        # trasversal rules
        'input_calc_forward': False,  #cli default: False
        'input_work_forward': False,  #cli default: False
        'create_backward': True,  #cli default: True
        'return_backward': True,  #cli default: False
        'call_calc_backward': True,  #cli default: False
        'call_work_backward': True,  #cli default: False
        # include
        'include_comments': True,  #cli default: True
        'include_logs': True,  #cli default: True
    }
    export_zip(all_new_groups, **kwargs)

# Create a folder with optimized cifs to upload in the Archive
if PRINT_OPT_CIFS:
    os.mkdir(CIFS_DIR)

    qb = QueryBuilder()
    qb.append(Group, project=['label'], filters={'label': {'like': r"curated-cof\_%"}}, tag='group')
    qb.append(CifData, project=['*'], filters={'extras.{}'.format(TAG_KEY): 'opt_cif_ddec'}, with_group='group')
    for q in qb.all():
        mat_id = q[0].split("_")[1]
        ddec_cif = q[1]
        ddec_cif.label = mat_id + "_DDEC"
        filename = '{}_ddec.cif'.format(mat_id)
        cifile = open(os.path.join(CIFS_DIR, filename), 'w+')
        print(ddec_cif.get_content(), file=cifile)
        print("{},{}".format(mat_id, ddec_cif))

# Delete new groups after the export
if CLEAR:
    delete_old_groups()
