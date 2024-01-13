"""
Flask server and the SQLAlchemy database of the application.
"""
import logging
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# import db_model
import routes_blueprint as routes_bp

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

    # Register a simple hello world page as the root route
    # [TODO] remove later
    @app.route('/')
    def hello_world():
        return 'Hello, World!'

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

    # [TODO] temporary json structure is used for now
    # Initialize the database and add the ability to reset it from
    # the command line
    # db_model.db.init_app(app)
    # with app.app_context():
    #     db_model.db.create_all()
    # app.cli.add_command(db_model.reset_db_command)

    app.register_blueprint(routes_bp.bp, url_prefix='/protocols')

    app.run(host=HOST, port=PORT, debug=DEBUG)
