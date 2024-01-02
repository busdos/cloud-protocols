from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.schema import PrimaryKeyConstraint
from flask_sqlalchemy import SQLAlchemy

import click
from flask.cli import with_appcontext

db = SQLAlchemy()

"""
User sessions table
"""
class Session(db.Model):
    __tablename__ = 'sessions'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )
    id = db.Column(db.String, nullable=False)
    data = db.Column(JSON, nullable=False)

"""
User session keys table
"""
class SessionKeys(db.Model):
    __tablename__ = 'session_keys'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'key_idx'),
    )
    id = db.Column(db.String, nullable=False)
    key_idx = db.Column(db.Integer, nullable=False)
    key0_val = db.Column(db.String)
    key1_val = db.Column(db.String)

"""
Command line function to clean the database and recreate the tables
"""
@click.command("reset-db")
@with_appcontext
def reset_db_command(database):
    database.drop_all()
    database.create_all()
