from globals import *
from mcl import G1

from protocols import designated_signature as desig
from . import route_utils as rout

def desig_verifier_actions(
    ses_token,
    action,
    client_payload
):
    print(f"verifier_actions, asked for action: {action=}")
    msg = client_payload['msg']
    sigma = [rout.mcl_from_str(a, G1) for a in  client_payload['sigma']]
    verifier = desig.Desig_Ver()

    verify = verifier.verify(sigma, msg, desig.PKI['signer'][1])
    print(f'{verify=}')

    response_payload = {
        "verify" : verify
    }
    db_data = None

    return db_data, response_payload
