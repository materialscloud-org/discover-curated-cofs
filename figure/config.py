from __future__ import absolute_import
import collections
import yaml
from os.path import join, dirname

static_dir = join(dirname(__file__), "static")

with open(join(static_dir, "columns.yml"), 'r') as f:
    quantity_list = yaml.load(f)

quantities = collections.OrderedDict([(q['column'], q) for q in quantity_list])

plot_quantities = [
    q for q in quantities.keys() if quantities[q]['type'] == 'float'
]

bondtype_dict = collections.OrderedDict([
    ('amide', "#1f77b4"),
    ('amine', "#d62728"),
    ('imine', "#ff7f0e"),
    ('CC', "#2ca02c"),
    ('mixed', "#778899"),
])

with open(join(static_dir, "filters.yml"), 'r') as f:
    filter_list = yaml.load(f)

with open(join(static_dir, "presets.yml"), 'r') as f:
    presets = yaml.load(f)

for k in presets.keys():
    if 'clr' not in list(presets[k].keys()):
        presets[k]['clr'] = presets['default']['clr']

max_points = 70000
