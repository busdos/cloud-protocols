from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.schema import PrimaryKeyConstraint
import flask_sqlalchemy as fsqla

import click
from flask.cli import with_appcontext

"""
User sessions table
"""
class Session(fsqla.Model):
    __tablename__ = 'sessions'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
    )
    id = fsqla.Column(fsqla.String, nullable=False)
    data = fsqla.Column(JSON, nullable=False)

"""
User session keys table
"""
class SessionKeys(fsqla.Model):
    __tablename__ = 'session_keys'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'key_idx'),
    )
    id = fsqla.Column(fsqla.String, nullable=False)
    key_idx = fsqla.Column(fsqla.Integer, nullable=False)
    key0_val = fsqla.Column(fsqla.String)
    key1_val = fsqla.Column(fsqla.String)

"""
Command line function to clean the database and recreate the tables
"""
@click.command("reset-db")
@with_appcontext
def reset_db_command(db):
    db.drop_all()
    db.create_all()
