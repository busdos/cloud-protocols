from pprint import pformat

from flask import Blueprint, current_app, jsonify, request

from db_model import MESSAGES, MESSAGES_ONE_OF_TWO, temp_db
from globals import PROTOCOL_SPECS, Protocols

from .route_oblivious_transfer import one_of_n_actions, one_of_two_actions
from .route_oblivious_polynomial_evaluation import ope_actions
from .route_utils import generate_token

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
        messages = temp_db[ses_token]["messages"]
        return one_of_two_actions(
            ses_token,
            action,
            client_payload,
            messages
        )
    elif protocol == Protocols.ONE_OF_N.value:
        return one_of_n_actions(
            ses_token,
            action,
            client_payload
        )
    elif protocol == Protocols.OPE.value:
        return ope_actions(
            ses_token,
            action,
            client_payload
        )
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

    is_init = action == PROTOCOL_SPECS[protocol]["init_action"]
    current_app.logger.info(f"{protocol} Current action: {pformat(action)};"
                            f" is init action: {pformat(is_init)}")

    if action == PROTOCOL_SPECS[protocol]["init_action"]:
        session_token = generate_token()
        default_messages = MESSAGES_ONE_OF_TWO if \
            protocol == Protocols.ONE_OF_TWO.value else \
            MESSAGES if protocol == Protocols.ONE_OF_N.value else \
            None

        temp_db[session_token] = {
            "counter": 0,
            "messages": default_messages
        }
        # print(f"{session_token}: {temp_db[session_token]=}")
    else:
        session_token = data.get("session_token")

    # print(f"{temp_db[session_token]=}")
    temp_db[session_token][action] = {}

    # db_data is a list of pairs; pairs are defined differently
    # for each protocol
    db_data, response_payload = construct_db_data(
        session_token, protocol, action, payload)

    is_close_action = action == PROTOCOL_SPECS[protocol]["close_action"]
    if is_close_action:
        del temp_db[session_token]
    else:
        # [TODO] add to protocol specification whether an action
        # returns some data to be stored in the DB
        if db_data is not None:
            curr_counter = temp_db[session_token]["counter"]
            # db_data is a dict, so we just connect the node to the
            # general "graph"
            # Node is a { 'name': {values} } where values can be
            # anything (dict, list, etc.)
            # print(f"{db_data=}")
            temp_db[session_token][action].update(db_data)
            curr_counter += 1

            temp_db[session_token]["counter"] = curr_counter

    if not is_close_action:
        # print(f"{temp_db[session_token]=}")
        print(f"{temp_db[session_token][action]=}")

    response = {
        "session_token": session_token,
        "payload": response_payload
    }

    current_app.logger.info(
        f"{protocol} Sending response: {pformat(response)}")
    return jsonify(response)