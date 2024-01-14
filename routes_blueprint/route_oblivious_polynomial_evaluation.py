"""
Route (server-side actions) for the oblivious
polynomial evaluation algorithm. The algorithm uses
uses 1-of-2 and 1-of-n oblivious transfers.
"""
from protocols import oblivious_polynomial_evaluation as ope
from db_model import temp_db
from protocols import oblivious_transfer as ot
from .route_oblivious_transfer import oblivious_transfer_encrypt_messages

from .route_utils import mcl_from_str, mcl_to_str
import globals as gl
import mcl

def ope_actions(ses_token,
                action,
                client_payload):
    if action == 'get_server_ephemerals':
        main_polynomial = \
            ope.OPECloud.gen_main_polynomial(
                gl.OPE_MAIN_POLY_DEGREE,
                gl.OPE_DEFAULT_SERVER_SEED
            )
    
        mask_polynomial = \
            ope.OPECloud.gen_mask_polynomial(
                gl.OPE_MASK_POLY_DEGREE,
                gl.OPE_DEFAULT_SERVER_SEED + '1'
            )
    
        query_points = client_payload.get('query_points')
        print(f'{query_points=}')
        # query_points is a dict of values looking like this:
        # {
        #   'point_0_x': x_0,
        #   'point_0_y': y_0,
        #   ...
        #   'point_<N-1>_x': x_n,
        #   'point_<N-1>_y': y_n,
        # }
        query_points = [
            (
                mcl_from_str(query_points[f'point_{i}_x'], mcl.Fr),
                mcl_from_str(query_points[f'point_{i}_y'], mcl.Fr)
            )
            for i in range(len(query_points) // 2)
        ]

        # Returns only y-values, so the order of the
        # points is assumed to be the same as in the
        # request
        masked_poly_values = \
            ope.OPECloud.compute_masked_polynomial_values(
                main_polynomial,
                mask_polynomial,
                query_points
            )

        assert len(query_points) == len(masked_poly_values)

        # Generate gl.OPE_SMALL_N*bit_length(number_of_queried_points) public
        # ephemerals for the client to use in the OT protocol
        ephemerals = []
        for i in range(gl.OPE_SMALL_N):
            for j in range(len(query_points).bit_length()):
                seph, peph = ot.OTCloud.gen_ephemerals(gl.GENERATOR)
                ephemerals.append((seph, peph))

        db_data = {
            'query_points': [],
            'ot_ephemerals': [],
        }
        for i in range(len(query_points)):
            db_data['query_points'].append(
                (mcl_to_str(query_points[i][0]), mcl_to_str(masked_poly_values[i]))
            )
        for i in range(len(ephemerals)):
            db_data['ot_ephemerals'].append(
                (mcl_to_str(ephemerals[i][0]), mcl_to_str(ephemerals[i][1]))
            )

        response_payload = {
            'pub_ephemerals': [
                mcl_to_str(ephemerals[i][1])
                for i in range(len(ephemerals))
            ]
        }
    elif action == 'perform_n_of_big_n_ot':
        client_ephemerals = client_payload.get('ephemerals')

        # comp_res = temp_db[ses_token]['get_masked_poly_points']['keys']
        # y_values = [point[1] for point in comp_res]
        # y_values_strs = [mcl_to_str(y) for y in y_values]
        y_values_strs = [mcl_to_str(y) for y in masked_poly_values]

        total_num_of_points = len(y_values_strs)
        max_bits_in_point_idx = total_num_of_points.bit_length()
        number_of_requested_points = gl.OPE_QUERY_POLY_DEGREE * \
            gl.OPE_MAIN_POLY_DEGREE + 1

        # Check that client_ephemerals is of the correct size
        #
        # client_ephemerals should be a dict of values looking like this:
        # {
        #   0: [eph_0_0, eph_0_1, ..., eph_0_max_bits_in_point_idx],
        #   1: [eph_1_0, eph_1_1, ..., eph_1_max_bits_in_point_idx],
        #   ...
        #   number_of_requested_points - 1: [eph_n_0, eph_n_1, ..., eph_n_max_bits_in_point_idx]
        # }
        #
        assert len(client_ephemerals) == number_of_requested_points
        for i in range(number_of_requested_points):
            assert i in client_ephemerals
            assert len(client_ephemerals[i]) == max_bits_in_point_idx
            for bit_i in range(max_bits_in_point_idx):
                assert client_ephemerals[i][bit_i] is not None

        response_payload = {}
        for i in range(number_of_requested_points):
            i_keys, ciphertexts = \
                oblivious_transfer_encrypt_messages(y_values_strs)
            response_payload[f'ciphertexts_{i}'] = \
                [cip.hex() for cip in ciphertexts]

            assert len(i_keys) == max_bits_in_point_idx
            for bit_i in range(max_bits_in_point_idx):
                seph, peph = ot.OTCloud.gen_ephemerals(gl.GENERATOR)
                client_eph = client_ephemerals[i][bit_i]
                str_i_keys = [mcl_to_str(k) for k in i_keys[bit_i]]
                _, k_ciphertexts = oblivious_transfer_encrypt_messages(
                    str_i_keys,
                    seph,
                    peph,
                    client_eph
                )

                response_payload[f'ciphertexts_{i}_{bit_i}'] = \
                    [cip.hex() for cip in k_ciphertexts]
        
        db_data = None

    else:
        db_data = None
        response_payload = None

    return db_data, response_payload
