import collections
import yaml
from os.path import join, dirname

with open(join(dirname(__file__), "columns.yml"), 'r') as f:
    quantity_list = yaml.load(f)

quantities = collections.OrderedDict([(q['column'], q) for q in quantity_list])

bondtype_dict = collections.OrderedDict([
    ('amide', "#1f77b4"),
    ('amine', "#d62728"),
    ('imine', "#ff7f0e"),
    ('CC', "#2ca02c"),
    ('mixed', "#778899"),
])

with open(join(dirname(__file__), "filters.yml"), 'r') as f:
    filter_list = yaml.load(f)

with open(join(dirname(__file__), "presets.yml"), 'r') as f:
    presets = yaml.load(f)

for k in presets.keys():
    if 'clr' not in presets[k].keys():
        presets[k]['clr'] = presets['default']['clr']

max_points = 70000
