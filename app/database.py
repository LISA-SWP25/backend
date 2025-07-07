import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'postgresql://lisa:lisa_password_2024@lisa_postgres_quick:5432/lisa_dev'

print(f'Database URL: {DATABASE_URL}')

try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('PostgreSQL connection successful!')
except Exception as e:
    print(f'PostgreSQL failed: {e}')
    DATABASE_URL = 'sqlite:///./fallback.db'
    engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
    print(f'Using SQLite: {DATABASE_URL}')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
