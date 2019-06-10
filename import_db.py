#!/usr/bin/env python
# coding: utf-8

# Import properties into sqlite database

from __future__ import print_function

from __future__ import absolute_import
import pandas as pd
import sqlalchemy
import re
import os

dirpath = os.path.dirname(os.path.realpath(__file__))

folder_db = dirpath + '/data/'
structure_folder = folder_db + '/structures/'
structure_extension = 'cif'
properties_csv = folder_db + '/properties.csv'
table_name = 'cofs'  # parameters will be put in this database
db_params = 'sqlite:///{}database.db'.format(folder_db)

# when storing structures on an object store
os_url = "https://object.cscs.ch/v1/AUTH_b1d80408b3d340db9f03d373bbde5c1e/discover-cofs/test_data/structures"

data = None

engine = sqlalchemy.create_engine(db_params, echo=False)
pandas_sql = pd.io.sql.pandasSQL_builder(engine, schema=None)

columns_json = {}


def parse_csv(path):
    data = pd.read_csv(path,
                       low_memory=False,
                       verbose=1,
                       skipinitialspace=True)
    print("Read {} data rows from .csv file".format(len(data)))
    return data


def add_filenames(data):
    print("Adding filenames")
    fnames = [
        "{}.{}".format(row['name'], structure_extension)
        for _index, row in data.iterrows()
    ]
    data['filename'] = fnames
    return data


# pylint: disable=too-many-arguments
def to_sql_k(self,
             frame,
             name,
             if_exists='fail',
             index=True,
             index_label=None,
             schema=None,
             chunksize=None,
             dtype=None,
             **kwargs):
    if dtype is not None:
        from sqlalchemy.types import to_instance, TypeEngine
        for col, my_type in dtype.items():
            if not isinstance(to_instance(my_type), TypeEngine):
                raise ValueError('The type of %s is not a SQLAlchemy '
                                 'type ' % col)

    table = pd.io.sql.SQLTable(name,
                               self,
                               frame=frame,
                               index=index,
                               if_exists=if_exists,
                               index_label=index_label,
                               schema=schema,
                               dtype=dtype,
                               **kwargs)
    table.create()
    table.insert(chunksize)


def rename_columns(data):
    """Rename columns.

    Need to rename columns to valid python variable names.
    """
    print("Renaming columns")
    labels = list(data.keys())
    #rep_dict = { l: l.replace(' ', '_') for l in labels }
    #data.rename(index=str, columns=rep_dict, inplace=True)

    unit_regex = re.compile('\[(.*?)\]')
    for label in labels:
        match = re.search(unit_regex, label)
        # provide units as separate column
        if match:
            units = match.group(1).strip()
            label_new = re.sub(unit_regex, '', label).strip().replace(' ', '_')
            data.rename(index=str, columns={label: label_new}, inplace=True)
            data[label_new + '_units'] = units
        else:
            label_new = label.replace(' ', '_')
            data.rename(index=str, columns={label: label_new}, inplace=True)

    return data


def fill_db():
    #data.to_sql(table_name, con=engine, if_exists='replace')
    print("Filling database")
    to_sql_k(pandas_sql,
             data,
             table_name,
             index=True,
             index_label='id',
             keys='id',
             if_exists='replace')

    with engine.connect() as con:
        test = pd.read_sql("SELECT * FROM {} LIMIT 5".format(table_name), con)
    print(test)


def automap_table(engine):
    """Try to infer model from Database.
    
    This currently does not work because
      1. sqlalchemy can only automap tables with a primary key
      2. pd.to_sql cannot create tables with a primary key
      3. sqlite does not allow table structure to be modified after creation
      
    See https://stackoverflow.com/a/35397969/1069467 for workarounds
    """
    from sqlalchemy.ext.automap import automap_base
    Base = automap_base()
    Base.prepare(engine, reflect=True)

    # mapped classes are now created with names by default
    # matching that of the table name.
    return Base.classes.get(table_name)


def get_cif_path(filename):
    from os.path import join, abspath
    return abspath(join(structure_folder, filename))


def get_cif_content_from_disk(filename):
    """Load CIF content from disk."""
    with open(get_cif_path(filename), 'r') as f:
        content = f.read()
    return content


def get_cif_content_from_os(filename):
    """Load CIF content via GET request from object store."""
    import requests

    url = "{}/{}".format(os_url, filename)
    print(url)
    data = requests.get(url)
    return data.content


if __name__ == "__main__":
    data = parse_csv(properties_csv)
    data = add_filenames(data)
    rename_columns(data)
    fill_db()
    automap_table(engine)
