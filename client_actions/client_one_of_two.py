import mcl

import globals as gl
from protocols import oblivious_transfer as ot
from routes_blueprint import route_utils

from . import post_action


def one_of_two_client(connection_url):
    message_to_get = 0
    generator = gl.GENERATOR

    PROTOCOL_NAME = gl.Protocols.ONE_OF_TWO.value
    PROTOCOL_ACTIONS = gl.PROTOCOL_SPECS[PROTOCOL_NAME]['actions']

    payload_to_post = {
        # [TODO] remove protocol_name later, needed only for compatibility
        # with another project
        'protocol_name': PROTOCOL_NAME,
        'payload': {}
    }

    resp_data = post_action(connection_url,
                            PROTOCOL_NAME,
                            PROTOCOL_ACTIONS[0],
                            payload_to_post)

    server_public_ephemeral = route_utils.mcl_from_str(
        resp_data.get('payload').get('A'), mcl.G1)

    (_, client_peph, enc_key) = \
        ot.OneOfTwoClient.gen_ephemerals_and_enc_key(
            generator,
            server_public_ephemeral,
            message_to_get
        )

    token = resp_data.get('session_token')
    payload_to_post['session_token'] = token
    payload_to_post['payload']['B'] = route_utils.mcl_to_str(
        client_peph)

    resp_data = post_action(connection_url,
                            PROTOCOL_NAME,
                            PROTOCOL_ACTIONS[1],
                            payload_to_post)
    
    ciphertexts_in_hex: list[str] = resp_data\
        .get('payload')\
        .get('ciphertexts')
    
    ciphertexts_in_bytes = [bytes.fromhex(
        hex_string) for hex_string in ciphertexts_in_hex]

    decrypted_hex_bytes = ot.OneOfTwoClient\
        .decrypt_message(
            ciphertexts_in_bytes[message_to_get],
            [enc_key])\
        .decode('utf-8')

    print(f'Message: {decrypted_hex_bytes}')