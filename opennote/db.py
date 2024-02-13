import click
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database

engine = create_engine(
    url=URL.create(
        drivername="postgresql",
        host="localhost",
        database="opennote",
        username="user",
        password="password"
    ),
    isolation_level="READ COMMITTED"
)
if not database_exists(engine.url):
    create_database(engine.url)
    click.echo('Created database.')

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def close_db(exception=None):
    db_session.remove()


def init_db():
    import opennote.models
    Base.metadata.create_all(bind=engine)
    return engine
