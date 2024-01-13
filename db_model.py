# import click
# from flask.cli import with_appcontext
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.dialects.sqlite import JSON
# from sqlalchemy.schema import PrimaryKeyConstraint

# db = SQLAlchemy()

# """
# Table containing indexed pairs of values bound to sessions.
# Depending on the moment in protocol execution it can be either
# a pair of keys (e.g. key corresponding to bit 0 and key
# corresponding to bit 1 in one-of-n transfer) or a
# private-public key pair.
# """
# class ObliviousTransferDataPair(db.Model):
#     __tablename__ = 'data_pairs'
#     __table_args__ = (
#         PrimaryKeyConstraint('session_token', 'val_idx'),
#     )
#     session_token = db.Column(db.String, nullable=False)
#     val_idx = db.Column(db.Integer, nullable=False)
#     left_val = db.Column(db.String)
#     right_val = db.Column(db.String)

# """
# Command line function to clean the database and recreate the tables
# """
# @click.command("reset-db")
# @with_appcontext
# def reset_db_command(database):
#     database.drop_all()
#     database.create_all()


def _generate_sample_messages(num: int):
    return [f"This is message number {i}".encode('ascii') for i in range(num)]


MESSAGES = _generate_sample_messages(10)
MESSAGES_ONE_OF_TWO = MESSAGES[:2]

# [TODO] temporary solution, probably should be a
# database; thread-unsafe so only one client at a time
# is currently supported at a time
# Filed struture:
# {
#   session_token: {
#       counter: int,
#       messages: [str],
#       action: str {
#           keys: [str],
#       }
#   }
# }
temp_db = {}
