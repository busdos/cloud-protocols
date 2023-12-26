"""
Flask server and the SQLAlchemy database of the application.
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

import logging
import os

import db_model

HOST = "0.0.0.0"
DEBUG = True
PORT = 8080
LOGGING_FORMAT = '%(message)s'


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT)
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)

    # Create the app; config is relative to the flask instance folder
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Create the database and marshmallow objects
    db = SQLAlchemy(app)
    ma = Marshmallow(app)

    # Default database url is the sqlite database in the instance folder
    db_url = f'sqlite:///{os.path.join(app.instance_path, "base.db")}'
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
    )

    # Load the instance config
    app.config.from_pyfile("config.py", silent=True)

    # Initialize the database and add the ability to reset it from
    # the command line
    app.cli.add_command(db_model.reset_db_command)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    # Register the blueprints
    # [TODO] Add the blueprints

    app.run(host=HOST, port=PORT, debug=DEBUG)
