import collections
import yaml
from os.path import join, dirname

static_dir = join(dirname(__file__), "static")

with open(join(static_dir, "columns.yml"), 'r') as f:
    quantity_list = yaml.load(f)

for item in quantity_list:
    if 'scale' not in item.keys():
        item['scale'] = 'linear'


quantities = collections.OrderedDict([(q['column'], q) for q in quantity_list])

plot_quantities = [
    q for q in quantities.keys() if quantities[q]['type'] == 'float'
]

with open(join(static_dir, "presets.yml"), 'r') as f:
    presets = yaml.load(f)

for k in presets.keys():
    if 'clr' not in list(presets[k].keys()):
        presets[k]['clr'] = presets['default']['clr']
