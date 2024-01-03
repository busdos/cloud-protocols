from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.schema import PrimaryKeyConstraint
from flask_sqlalchemy import SQLAlchemy

import click
from flask.cli import with_appcontext

db = SQLAlchemy()

"""
Table containing indexed pairs of values bound to sessions.
Depending on the moment in protocol execution it can be either
a pair of keys (e.g. key corresponding to bit 0 and key
corresponding to bit 1 in one-of-n transfer) or a
private-public key pair.
"""
class ObliviousTransferDataPair(db.Model):
    __tablename__ = 'data_pairs'
    __table_args__ = (
        PrimaryKeyConstraint('session_token', 'val_idx'),
    )
    session_token = db.Column(db.String, nullable=False)
    val_idx = db.Column(db.Integer, nullable=False)
    left_val = db.Column(db.String)
    right_val = db.Column(db.String)

"""
Command line function to clean the database and recreate the tables
"""
@click.command("reset-db")
@with_appcontext
def reset_db_command(database):
    database.drop_all()
    database.create_all()
