"""
Route (server-side actions) for the one-of-two and
one-of-n oblivious transfer algorithms.
"""
from flask import jsonify

import mcl

from .route_utils import mcl_to_str, mcl_from_str, generate_sample_messages

from db_model import ObliviousTransferDataPair
from protocols import oblivious_transfer_on_of_two as oo2

_MESSAGES = generate_sample_messages(10)
_SEC_PAR = b"test"
GENERATOR = mcl.G1.hashAndMapTo(_SEC_PAR)

def one_of_two_actions(ses_token, action, client_payload):
    if action == "get_A":
        seph, peph = oo2.OneOfTwoCloud.gen_ephemerals()

        # (small a, big A)
        db_data = [(mcl_to_str(seph), mcl_to_str(peph))]
        response_payload = {
            "A": mcl_to_str(peph)
        }
    elif action == "get_ciphertexts":
        ses_data = ObliviousTransferDataPair.query.filter_by(
            session_token=ses_token).first()
        
        seph = mcl_from_str(ses_data.left_key_val, mcl.Fr)
        peph = mcl_from_str(ses_data.right_key_val, mcl.G1)
        client_eph = mcl_from_str(client_payload.get("B"), mcl.G1)
        
        ciphertexts = oo2.OneOfTwoCloud.encrypt_messages(
            client_eph, seph, peph, _MESSAGES[:2])

        db_data = None
        response_payload = {
            "ciphertexts": [cip.hex() for cip in ciphertexts]
        }
    return db_data, jsonify(response_payload)
