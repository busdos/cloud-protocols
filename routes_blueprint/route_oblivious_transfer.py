"""
Route (server-side actions) for the one-of-two and
one-of-n oblivious transfer algorithms.
"""
import mcl
from flask import jsonify

import globals
from db_model import temp_db
from protocols import oblivious_transfer as ot

from .route_utils import mcl_from_str, mcl_to_str

# [TODO] probably has to be part of the Cloud class
def oblivious_transfer_encrypt_messages(
    messages: list[str],
    cloud_seph = None,
    cloud_peph = None,
    client_peph = None
) -> (list[bytes], list[bytes]):
    if len(messages) == 2:
        assert cloud_seph is not None
        assert cloud_peph is not None
        assert client_peph is not None

    longest_msg_len = len(
        max(messages,
        key=len))

    keys = ot.OTCloud.compute_keys(
        len(messages),
        longest_msg_len,
        client_peph,
        cloud_seph,
        cloud_peph)

    ciphertexts = ot.OTCloud.encrypt_messages(
        longest_msg_len, keys, messages)

    return keys, ciphertexts

# [TODO] hardcoded strings can be references to global
# definition of the protocol flow
# (e.g. the PROTOCOLS variable)
def one_of_two_actions(ses_token,
                       action,
                       client_payload,
                       messages):
    if action == 'get_A':
        seph, peph = ot.OTCloud.gen_ephemerals(
            globals.GENERATOR)

        # (small a, big A)
        db_data = [(mcl_to_str(seph), mcl_to_str(peph))]
        response_payload = {
            'A': mcl_to_str(peph)
        }
    elif action == 'get_two_ciphertexts':
        assert messages is not None
        # Get keys stored in the previous step
        ses_data = temp_db[ses_token]['get_A']['keys']
        
        print(f'{ses_data=}')
        seph = mcl_from_str(ses_data[0][0], mcl.Fr)
        peph = mcl_from_str(ses_data[0][1], mcl.G1)
        client_eph = mcl_from_str(client_payload.get('B'), mcl.G1)

        # Since we want two ciphertexts, number
        # of messages must be 2
        assert len(messages) == 2
        _, ciphertexts = oblivious_transfer_encrypt_messages(
            messages,
            seph,
            peph,
            client_eph)

        db_data = None
        response_payload = {
            'ciphertexts': [cip.hex() for cip in ciphertexts]
        }
    
    return db_data, response_payload


def one_of_n_actions(ses_token,
                     action,
                     client_payload):
    if action == 'get_ciphertexts':
        messages = temp_db[ses_token]['messages']
        print(f'{messages=}')

        keys, ciphertexts = \
            oblivious_transfer_encrypt_messages(messages)

        # db_data are all the key pairs for the messages
        db_data = [
            (k[0], k[1])
            for k in keys
        ]

        response_payload = {
            'ciphertexts': [cip.hex() for cip in ciphertexts]
        }
    else:
        # Get key_idx from client_payload and load it from the DB
        oo2_messages = None
        if action == 'get_two_ciphertexts':
            key_idx = client_payload.get('key_idx')
            oo2_messages = temp_db[ses_token]['get_ciphertexts']['keys'][key_idx]

        db_data, response_payload = \
            one_of_two_actions(ses_token,
                               action,
                               client_payload,
                               oo2_messages)

    return db_data, response_payload