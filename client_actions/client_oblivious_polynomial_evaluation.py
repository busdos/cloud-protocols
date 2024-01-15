import mcl

import globals as gl

from protocols import oblivious_transfer as ot
from protocols import oblivious_polynomial_evaluation as ope
from protocols import protocol_utils as prot_ut
from routes_blueprint import route_utils as route_ut

from . import post_action

def ope_client(url):
    alpha = mcl.Fr()
    alpha.setInt(10)

    PROTOCOL_NAME = gl.Protocols.OPE.value
    PROTOCOL_ACTIONS = gl.PROTOCOL_SPECS[PROTOCOL_NAME]['actions']

    payload_to_post = {
        # [TODO] remove protocol_name later, needed only
        # for compatibility with another project
        'protocol_name': PROTOCOL_NAME,
        'payload': {}
    }

    ### Query point generatoin ### 
    ope_client = ope.OPEClient()
    query_polynomial = ope.OPEPolynomial(
        gl.OPE_QUERY_POLY_DEGREE,
        gl.OPE_DEFAULT_CLIENT_SEED
    )
    query_polynomial.set_val_at_zero(alpha)
    submerged_ids = ope_client.gen_submerged_points_indices(
        gl.OPE_SMALL_N,
        gl.OPE_BIG_N
    )
    # Write the points into a file to be able to read them
    # on server for verification
    with open('query_points.txt', 'w') as f:
        for i in range(len(submerged_ids)):
            f.write(f'{submerged_ids[i]}\n')

    from time import sleep
    sleep(1)

    query_x_values = ope_client.gen_query_x_values(
        gl.OPE_BIG_N
    )
    query_y_values = ope_client.produce_query_y_values(
        query_polynomial,
    )
    query_points = [
        (query_x_values[i], query_y_values[i])
        for i in range(len(query_x_values))
    ]

    payload_to_post['payload']['query_points'] = {}
    for (i, p) in enumerate(query_points):
        payload_to_post['payload']['query_points'][f'point_{i}_x'] = route_ut.mcl_to_str(p[0])
        payload_to_post['payload']['query_points'][f'point_{i}_y'] = route_ut.mcl_to_str(p[1])

    resp_data = post_action(
        url,
        PROTOCOL_NAME,
        PROTOCOL_ACTIONS[0],
        payload_to_post
    )

    token = resp_data.get('session_token')
    if token is None:
        raise Exception('No session token received')
    payload_to_post['session_token'] = token

    #### Generation of ephemerals for OT ####
    cloud_ephemerals = resp_data['payload']['pub_ephemerals']
    print(f'{len(cloud_ephemerals)=}')
    max_index_bit_len = gl.OPE_BIG_N.bit_length()

    decryption_key_indices = {}
    ot_ephemerals = []
    payload_to_post['payload'].pop('query_points')
    payload_to_post['payload']['ephemerals'] = {}
    for i, subm in enumerate(submerged_ids):
        ot_idx_rev_bits = format(subm, 'b').zfill(max_index_bit_len)[::-1]
        decryption_key_indices[subm] = [
            int(bit) for bit in ot_idx_rev_bits
        ]

        for j in range(max_index_bit_len):
            choice = decryption_key_indices[subm][j]
            (_, client_peph, enc_key) = \
                ot.OneOfTwoClient.gen_ephemerals_and_enc_key(
                    gl.GENERATOR,
                    route_ut.mcl_from_str(
                        cloud_ephemerals[i * max_index_bit_len + j],
                        mcl.G1
                    ),
                    choice
            )
            ot_ephemerals.append((enc_key, client_peph))
            payload_to_post['payload']['ephemerals'][f'ephemeral_{i}_{j}'] = \
                route_ut.mcl_to_str(client_peph)

    resp_data = post_action(
        url,
        PROTOCOL_NAME,
        PROTOCOL_ACTIONS[1],
        payload_to_post
    )

    ####
    #### Decryption of the selected polynomial points
    #### and their interpolation
    ####
    # Format of the message:
    # {
    #   'ciphertexts_<i>': set of ciphertexts for the i-th point
    #                      out of the small_n needed
    #
    #   'ciphertexts_<i>_<bit_index>': two keys, one if index's bit
    #                                  on position bit_index is 0
    #                                  and the other if it is 1
    # }

    interpolation_set = []
    print(f'Interested in points: {submerged_ids}')
    for i in range(gl.OPE_SMALL_N):
        ciphertexts = resp_data['payload'][f'ciphertexts_{i}']
        ciphertext_idx = submerged_ids[i]
        needed_point_ciphertext_bytes = bytes.fromhex(
            ciphertexts[ciphertext_idx]
        )
        print(f'Getting point number {ciphertext_idx}: {needed_point_ciphertext_bytes=}')

        keys = []
        # print(f'{ciphertexts=}')
        for j in range(max_index_bit_len):
            ciphertexts_keys = resp_data['payload'][f'ciphertexts_{i}_{j}']
            ciphertexts_keys_bytes = [bytes.fromhex(
                hex_string) for hex_string in ciphertexts_keys]
    
            # print(f'{ciphertexts_keys=}')
            key_idx = decryption_key_indices[ciphertext_idx][j]
            # print(f'{key_idx=}')
            (enc_key, client_peph) = ot_ephemerals[i * max_index_bit_len + j]
            # print(f'{enc_key=}')
            # print(f'{client_peph=}')
            print(f'{type(enc_key)=}, {type(ciphertexts_keys_bytes[key_idx])=}')
            decrypted_key = ot.OneOfTwoClient.decrypt_message(
                ciphertexts_keys_bytes[key_idx],
                [enc_key],
            )
            # print(f'key{decrypted_key=}')
            keys.append(decrypted_key)

        # Decrypt the individual point from ciphertexts
        # using the keys
        decrypted_point = ot.OneOfTwoClient.batch_decrypt(
            needed_point_ciphertext_bytes,
            keys
        )
        interpolation_set.append(decrypted_point)
    
    interpolation_set = [
        route_ut.mcl_from_bytes(point, mcl.Fr) for point in interpolation_set
    ]
    print(f'{len(interpolation_set)=}')
    print(f'{interpolation_set=}')

    result = ope_client.eval_result_polynomial(
        interpolation_set
    )
    print(f'Evaluation result: {result=}')
