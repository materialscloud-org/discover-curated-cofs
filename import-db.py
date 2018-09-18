#!/usr/bin/env python
# coding: utf-8

# Import properties into sqlite database

from __future__ import print_function

import pandas as pd
import sqlalchemy

folder_db = '/project/cofs'
structure_folder = folder_db + '/structures/'
properties_csv = folder_db + '/properties.csv'
db_name = 'cofs'  # parameters will be put in this database
db_params = 'sqlite:///mydatabase.db'

data = None


def parse_csv(path):
    global data
    data = pd.read_csv(
        path, low_memory=False, verbose=1, skipinitialspace=True)
    print("Read {} data rows from .csv file".format(len(data)))


def add_filenames():
    fnames = [
        "{}_{}_{}_relaxed.cif".format(row['linkerA'], row['linkerB'],
                                      row['net'])
        for _index, row in data.iterrows()
    ]
    data['filename'] = fnames


engine = sqlalchemy.create_engine(db_params, echo=False)


def fill_db():
    data.to_sql(db_name, con=engine, if_exists='replace')

    with engine.connect() as con:
        test = pd.read_sql("SELECT * FROM {} LIMIT 5".format(db_name), con)
    print(test)


#def automap():
#    """Try to infer model from Database.
#    
#    This currently does not work because
#      1. sqlalchemy can only automap tables with a primary key
#      2. pd.to_sql cannot create tables with a primary key
#      3. sqlite does not allow table structure to be modified after creation
#      
#    See https://stackoverflow.com/a/35397969/1069467 for workarounds
#    """
#    from sqlalchemy.ext.automap import automap_base
#
#    Base = sqlalchemy.ext.automap.automap_base()
#    Base.prepare(engine, reflect=True)
#
#    # mapped classes are now created with names by default
#    # matching that of the table name.
#    Cof = Base.classes.cofs


if __name__ == "__main__":
    parse_csv(properties_csv)
    add_filenames()
    fill_db()
