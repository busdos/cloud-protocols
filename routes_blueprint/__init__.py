from flask import Blueprint, jsonify
from flask import current_app

from . import route_one_of_n

bp = Blueprint("protocols", __name__)

@bp.route("/")
def index(implemented_protocols):
    current_app.logger.info(
        f'Implemented protocols: {str(implemented_protocols)}')
    return jsonify({
        "protocols": implemented_protocols
    })

def add_protocol_routes(blueprint, routes):
    for r in routes:
        blueprint.add_url_rule(
            r['rule'],
            endpoint=r.get('endpoint', None),
            view_func=r['view_func'],
            **r.get('options', {})
        )

def create_routes() -> list:
    """
    A "static" function that returns a list of routes to be added to the
    Flask server.
    """
    routes = []
    routes.append(dict(
        rule='/one_of_n/get_A',
        view_func=route_one_of_n.one_of_n_send_A,
        options=dict(methods=['POST'])))

    return routes