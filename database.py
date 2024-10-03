from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine=create_engine('postgresql://postgres:admin@127.0.0.1:5432/postgres',echo=True)

Base = declarative_base()
Session= sessionmaker()