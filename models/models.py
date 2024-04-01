from sqlalchemy import MetaData, Table, Column, Integer, String

metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('role', String, nullable=False),
)
