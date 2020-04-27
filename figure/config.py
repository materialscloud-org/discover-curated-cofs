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


def update_config():
    """Add AiiDA profile from environment variables, if specified"""
    from aiida.manage.configuration import load_config
    from aiida.manage.configuration.profile import Profile
    import os

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


AIIDA_CONFIG = update_config()
