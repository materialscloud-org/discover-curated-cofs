import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('sqlite://', echo=False)
df = pd.DataFrame({'name': ['User 1', 'User 2', 'User 3']})
df.to_sql('users', con=engine)

print(engine.execute("SELECT * FROM users").fetchall())
