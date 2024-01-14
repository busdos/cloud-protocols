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

    # print(f'{payload_to_post["payload"]["query_points"]=}')

    resp_data = post_action(
        url,
        PROTOCOL_NAME,
        PROTOCOL_ACTIONS[0],
        payload_to_post
    )

    print(f'{resp_data=}')

    # ### Generation of ephemerals for OT ###
    # max_index_bit_len = gl.OPE_BIG_N.bit_length()
    # num_of_ephemerals = gl.OPE_SMALL_N * max_index_bit_len

    # client = ot.OneOfTwoClient(gl.GENERATOR, 0)
    # decryption_key_indices = {}
    # for i, subm in enumerate(submerged_ids):
    #     ot_idx_rev_bits = format(subm, 'b').zfill(max_index_bit_len)[::-1]

    #     decryption_key_indices[f'{subm}'] = [int(bit) for bit in ot_idx_rev_bits]
    
    #     for j in range(max_index_bit_len):
    #         client.set_choice(decryption_key_indices[f'{subm}'][j])
    #         client.gen_ephemerals()
    #         client_ephemeral = client.get_public_ephemeral()
    #         payload_to_post['payload'][f'ephemeral_{i}_{j}'] = route_ut.mcl_to_str(client_ephemeral)

    # print(f'{payload_to_post["payload"]=}')
    # resp_data = post_action(
    #     url,
    #     PROTOCOL_NAME,
    #     PROTOCOL_ACTIONS[0],
    #     payload_to_post
    # )

    # print(f'{resp_data=}')

    