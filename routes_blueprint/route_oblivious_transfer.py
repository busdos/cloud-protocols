"""
Route (server-side actions) for the one-of-two and
one-of-n oblivious transfer algorithms.
"""
from flask import jsonify

import mcl

from .route_utils import mcl_to_str, mcl_from_str, generate_sample_messages

from db_model import ObliviousTransferDataPair
from protocols import oblivious_transfer as ot
import globals

_MESSAGES = generate_sample_messages(10)
TWO = 2

# [TODO] hardcoded strings can be references to global
# definition of the protocol flow
# (e.g. the PROTOCOLS variable)
def one_of_two_actions(ses_token,
                       action,
                       client_payload):
    if action == 'get_A':
        seph, peph = ot.OTCloud.gen_ephemerals(
            globals.GENERATOR)

        # (small a, big A)
        db_data = [(mcl_to_str(seph), mcl_to_str(peph))]
        response_payload = {
            'A': mcl_to_str(peph)
        }
    elif action == 'get_oo2_ciphertexts':
        ses_data = ObliviousTransferDataPair.query.filter_by(
            session_token=ses_token).first()
        
        seph = mcl_from_str(ses_data.left_val, mcl.Fr)
        peph = mcl_from_str(ses_data.right_val, mcl.G1)
        client_eph = mcl_from_str(client_payload.get('B'), mcl.G1)

        longest_msg_len = len(
            max(_MESSAGES,
            key=len))

        keys = ot.OTCloud.compute_keys(
            TWO,
            longest_msg_len,
            client_eph,
            seph,
            peph)

        ciphertexts = ot.OTCloud.encrypt_messages(
            longest_msg_len, keys, _MESSAGES[:2])

        db_data = None
        response_payload = {
            'ciphertexts': [cip.hex() for cip in ciphertexts]
        }
    
    return db_data, response_payload


def one_of_n_actions(ses_token,
                     action,
                     client_payload):
    if action == 'get_ciphertexts':
        longest_msg_len = len(longest_msg_len)

        keys = ot.OTCloud.compute_keys(
            len(_MESSAGES),
            longest_msg_len)

        ciphertexts = ot.OTCloud.encrypt_messages(
            longest_msg_len,
            keys,
            _MESSAGES)

        # db_data are all the key pairs for the messages
        db_data = [
            (mcl_to_str(k[0]), mcl_to_str(k[1]))
            for k in keys
        ]

        response_payload = {
            'ciphertexts': [cip.hex() for cip in ciphertexts]
        }
    else:
        db_data, response_payload = \
            one_of_two_actions(ses_token,
                               action,
                               client_payload)

    return db_data, response_payload