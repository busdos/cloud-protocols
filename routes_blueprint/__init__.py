from flask import Blueprint, jsonify
from flask import current_app, request, current_app

from pprint import pformat

from db_model import db, ObliviousTransferDataPair
from .route_utils import generate_token
from .route_oblivious_transfer import one_of_two_actions, one_of_n_actions
from globals import Protocols, PROTOCOL_SPECS

bp = Blueprint("protocols", __name__)

@bp.route("/")
def index():
    current_app.logger.info(
        f'Implemented protocols: {str(Protocols.get_as_list())}')
    return jsonify({
        "protocols": list(Protocols.get_as_list())
    })

# [TODO] can be generic, just call what is passed in the
# protocol parameter
def construct_db_data(ses_token,
                      protocol,
                      action,
                      client_payload):
    if protocol == Protocols.ONE_OF_TWO.value:
        return one_of_two_actions(ses_token,
                                  action,
                                  client_payload)
    elif protocol == Protocols.ONE_OF_N.value:
        return one_of_n_actions(ses_token,
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
    current_app.logger.info(f"{protocol} Received payload: {pformat(payload)}")

    if not Protocols.has_value(protocol):
        current_app.logger.error(f"Unknown protocol {protocol=}")
        return None

    if action not in PROTOCOL_SPECS[protocol]["actions"]:
        current_app.logger.error(f"Unknown action {action=}")
        return None
    
    if action == PROTOCOL_SPECS[protocol]["init_action"]:
        session_token = generate_token()
    else:
        session_token = data.get("session_token")

    # db_data is a list of pairs; pairs are defined differently
    # for each protocol
    db_data, response_payload = construct_db_data(
        session_token, protocol, action, payload)
    
    if action == PROTOCOL_SPECS[protocol]["close_action"]:
        ObliviousTransferDataPair.query.filter_by(
            session_token=session_token).delete()
        db.session.commit()
    else:
        data_to_insert = [ObliviousTransferDataPair(
            session_token=session_token,
            val_idx=i,
            left_val=key0,
            right_val=key1,
        ) for i, (key0, key1) in enumerate(db_data)]

        try:
            db.session.add_all(data_to_insert)
            db.session.commit()
        except:
            db.create_all()
            db.session.rollback()
            db.session.add_all(data_to_insert)
            db.session.commit()

    response = {
        "session_token": session_token,
        "payload": response_payload
    }

    current_app.logger.info(
        f"{protocol} Sending response: {pformat(response)}")
    return jsonify(response)