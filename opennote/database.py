from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_utils import database_exists, create_database


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def init_db(app, url):
    app.config["SQLALCHEMY_DATABASE_URI"] = url
    if not database_exists(url):
        create_database(url)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db
