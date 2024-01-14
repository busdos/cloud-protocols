import mcl

import globals as gl

# [TODO] batch decryption should probably be part of
# the protocol itself and not directly imported
from protocols import oblivious_transfer as ot
from protocols import protocol_utils as ut
from routes_blueprint import route_utils

from . import post_action


def one_of_n_client(connection_url):
    message_to_get = 6

    PROTOCOL_NAME = gl.Protocols.ONE_OF_N.value
    PROTOCOL_ACTIONS = gl.PROTOCOL_SPECS[PROTOCOL_NAME]['actions']

    payload_to_post = {
        # [TODO] remove protocol_name later, needed only
        # for compatibility with another project
        'protocol_name': PROTOCOL_NAME,
        'payload': {}
    }

    resp_data = post_action(connection_url,
                            PROTOCOL_NAME,
                            PROTOCOL_ACTIONS[0],
                            payload_to_post)

    token = resp_data.get('session_token')
    all_ciphertexts = resp_data\
        .get('payload')\
        .get('ciphertexts')
    num_of_messages = len(all_ciphertexts)
    max_bits = num_of_messages.bit_length()

    assert message_to_get < num_of_messages

    payload_to_post['session_token'] = token
    client_ciphertext = bytes.fromhex(
        all_ciphertexts[message_to_get])
    
    # Every bit of the message index (i.e. either
    # 0 or 1) is the index of the key to return from
    # one-of-two protocol
    #
    # So for e.g. index 3 (i.e. 0b011) with maximum
    # message index 7 the indices will return
    # keys[0][1], keys[1][1], keys[2][0]
    reversed_bits = format(message_to_get, 'b').zfill(max_bits)[::-1]
    key_indices = [int(bit) for bit in reversed_bits]

    print(f'key_indices: {key_indices}')

    keys = []

    for key_idx in range(max_bits):
        # One of two payload and steps but with different
        # protocol name
        one_of_two_payload = {
            'protocol_name': PROTOCOL_NAME,
            'payload': {},
            'session_token': token,
        }

        resp_data = post_action(
            connection_url,
            PROTOCOL_NAME,
            PROTOCOL_ACTIONS[1],
            one_of_two_payload)

        big_a = route_utils.mcl_from_str(
            resp_data['payload']['A'], mcl.G1)

        key_choice = key_indices[key_idx]
        (_, client_peph, enc_key) = \
            ot.OneOfTwoClient.gen_ephemerals_and_enc_key(
                gl.GENERATOR,
                big_a,
                key_choice
            )

        one_of_two_payload['payload']['B'] = route_utils.mcl_to_str(
            client_peph)
        one_of_two_payload['payload']['key_idx'] = key_idx

        resp_data = post_action(
            connection_url, PROTOCOL_NAME,
            PROTOCOL_ACTIONS[2], one_of_two_payload)

        ciphertext_bytes = [bytes.fromhex(
            hex_string) for hex_string in resp_data['payload']['ciphertexts']]
        
        key = ot.OneOfTwoClient.decrypt(
            ciphertext_bytes,
            enc_key,
            key_choice
        )
        print(f"key[{key_idx}]: {key}")
        keys.append(key)

    print(f"MSG: {ot.OneOfTwoClient.batch_decrypt(client_ciphertext, keys)}")


