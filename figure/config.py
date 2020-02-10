import collections
import yaml
from os.path import join, dirname

static_dir = join(dirname(__file__), "static")

with open(join(static_dir, "quantities.yml"), 'r') as f:
    quantities_list = yaml.load(f, Loader=yaml.SafeLoader)

for item in quantities_list:
    if 'descr' not in item.keys():
        item['descr'] = 'Description to be added!'
    if 'scale' not in item.keys():
        item['scale'] = 'linear'

quantities = collections.OrderedDict([(q['label'], q) for q in quantities_list])
