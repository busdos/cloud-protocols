from flask import current_app
from globals import *
from mcl import Fr

from protocols import designated_signature as desig
from . import route_utils as rout
import client_actions as clact

PROTOCOL_NAME = Protocols.DESIG.value
PROTOCOL_ACTIONS = PROTOCOL_SPECS[PROTOCOL_NAME]["actions"]
routes = []

def designator_actions(
    ses_token,
    action,
    client_payload
):
    msg = client_payload['msg']
    print(f"Received signature: {client_payload['sigma']}")

    sigma = [
        rout.mcl_from_str(a, Fr)
        for a in client_payload['sigma']
    ]
    forwarder = desig.Desig_Forward()

    verification_result = forwarder.verify(sigma, msg, desig.PKI['signer'][1])
    print(f'{verification_result=}')

    print(f'{current_app.config["url"]=}')
    url = current_app.config['url']

    # Create a designation and send it to the target verifier
    _PROTOCOL_NAME = Protocols.DEVER.value
    _PROTOCOL_ACTIONS = PROTOCOL_SPECS[_PROTOCOL_NAME]["actions"]
    init_dic = {
        "protocol_name": _PROTOCOL_NAME,
        "payload": {
            "msg" : msg,
            "sigma" : [rout.mcl_to_str(a) for a in forwarder.designation(sigma, desig.PKI['verifier'][1], desig.PKI['signer'][1])],
        }
    }
    print(url, _PROTOCOL_NAME, init_dic, _PROTOCOL_ACTIONS[0])
    resp_data = clact.post_action(
        url,
        _PROTOCOL_NAME,
        _PROTOCOL_ACTIONS[0],
        init_dic
    )

    print(f'{resp_data["payload"]=}')

    # Send verification result back to the signer
    response_payload = {
        "verify" : verification_result
    }
    db_data = None

    return db_data, response_payload