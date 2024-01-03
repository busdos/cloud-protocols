from flask import Blueprint, jsonify
from flask import current_app, request, current_app

from pprint import pformat

from db_model import db, ObliviousTransferDataPair
from .route_utils import generate_token
from .route_oblivious_transfer import one_of_two_actions

# First value is the action called on server's side
# Second value is the reques (url) called on client's side
#
# The first element of the array is the initializing action,
# so when it occurs the server should generate a new session
# token
#
# The last element of the array is the closing action, so when
# it occurs the server should delete the session's data from
# the database
PROTOCOLS = {
    "one_of_two": {
        "actions": [
            ("send_A", "get_A"),
            ("send_ciphertexts", "get_ciphertexts"),
        ],
        "init_action": "get_A",
        "close_action": "get_ciphertexts"
    }
}

bp = Blueprint("protocols", __name__)

@bp.route("/")
def index(implemented_protocols):
    current_app.logger.info(
        f'Implemented protocols: {str(implemented_protocols)}')
    return jsonify({
        "protocols": implemented_protocols
    })

# [TODO] can be generic, just call what is passed in the
# protocol parameter
def construct_db_data(ses_token,
                      protocol,
                      action,
                      client_payload):
    if protocol == "one_of_two":
        return one_of_two_actions(ses_token,
                                  action,
                                  client_payload)
    else:
        current_app.logger.error(f"Unknown protocol {protocol=}")
        return None


@bp.route("/<protocol>/<action>", methods=["POST"])
def generic_protocol_route_post(protocol, action):
    if request.data and type(request.data) is dict:
        data = request.data
    else:
        data = request.json

    payload = data.get("payload")
    current_app.logger.info(f"{protocol} Received payload:\n{pformat(payload)}")

    if protocol not in PROTOCOLS:
        current_app.logger.error(f"Unknown protocol {protocol=}")
        return None
    
    if action not in PROTOCOLS[protocol]["actions"]:
        current_app.logger.error(f"Unknown action {action=}")
        return None
    
    if action == PROTOCOLS[protocol]["init_action"]:
        session_token = generate_token()
    else:
        session_token = data.get("session_token")

    # db_data is a list of pairs; pairs are defined differently
    # for each protocol
    db_data, response_payload = construct_db_data(
        protocol, action, payload)
    
    if action == PROTOCOLS[protocol]["close_action"]:
        ObliviousTransferDataPair.query.filter_by(
            session_token=session_token).delete()
        db.session.commit()
    else:
        db_data = [ObliviousTransferDataPair(
            session_token=session_token,
            key_idx=i,
            left_key_val=key0,
            right_key_val=key1,
        ) for i, key0, key1 in enumerate(db_data)]

        try:
            db.session.add_all(db_data)
            db.session.commit()
        except:
            db.create_all()
            db.session.rollback()
            db.session.add_all(db_data)
            db.session.commit()

    response = {
        "session_token": session_token,
        "payload": response_payload
    }

    current_app.logger.info(
        f"{protocol} Sending response: {pformat(response)}")
    return jsonify(response)