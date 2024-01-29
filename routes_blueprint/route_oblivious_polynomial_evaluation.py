"""
Route (server-side actions) for the oblivious
polynomial evaluation algorithm. The algorithm
uses 1-of-2 and 1-of-n oblivious transfers.
"""
from protocols import oblivious_polynomial_evaluation as ope
from db_model import temp_db
from protocols import oblivious_transfer as ot
from .route_oblivious_transfer import oblivious_transfer_encrypt_messages

from .route_utils import mcl_from_str, mcl_to_str
import globals as gl
import mcl

def ope_actions(
    ses_token,
    action,
    client_payload
):
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

        ### Test prints

        alpha = mcl.Fr()
        alpha.setInt(gl.OPE_TEST_ALPHA)
        print(f'\033[91m THE ANSWER SHOULD BE {main_polynomial(alpha)=}\033[0m')

        ### End of test prints

        query_points = client_payload.get('query_points')
        # print(f'{query_points=}')

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
        # print(f'{len(query_points).bit_length()=}')
        # print(f'{gl.OPE_SMALL_N=}')

        ephemerals = []
        for i in range(gl.OPE_SMALL_N):
            for j in range(len(query_points).bit_length()):
                seph, peph = ot.OTCloud.gen_ephemerals(gl.GENERATOR)
                ephemerals.append((seph, peph))

        db_data = {
            'masked_poly_points': [],
            'ot_ephemerals': [],
        }
        for i in range(len(query_points)):
            db_data['masked_poly_points'].append(
                (mcl_to_str(query_points[i][0]), mcl_to_str(masked_poly_values[i]))
            )

        # Read the points from the file
        with open('query_points.txt', 'r') as f:
            submerged_ids_file = [
                int(line.strip()) for line in f.readlines()
            ]

        print(f'\033[92m{[masked_poly_values[i] for i in submerged_ids_file]=}\033[0m')

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

        points = temp_db[ses_token]['get_server_ephemerals']['masked_poly_points']
        y_values_strs = [point[1] for point in points]
        # print(f'{y_values_strs=}')
        y_value_bytes = [bytes.fromhex(y) for y in y_values_strs]

        total_num_of_points = len(y_values_strs)
        max_bits_in_point_idx = total_num_of_points.bit_length()
        number_of_requested_points = gl.OPE_SMALL_N

        # Check that client_ephemerals is of the correct size.
        # Client ephemerals are a list of key-value pairs of the form:
        # {
        #   'ephemeral_<i>_<j>': <ephemeral_value>
        # }
        # where i is the index of the point and j is the index of the bit
        # of the point index.
        assert len(client_ephemerals) == \
            number_of_requested_points * max_bits_in_point_idx

        response_payload = {}
        for i in range(number_of_requested_points):
            i_keys, ciphertexts = \
                oblivious_transfer_encrypt_messages(y_value_bytes)
            response_payload[f'ciphertexts_{i}'] = \
                [cip.hex() for cip in ciphertexts]

            assert len(i_keys) == max_bits_in_point_idx
            for bit_i in range(max_bits_in_point_idx):
                seph, peph = temp_db[ses_token]['get_server_ephemerals']['ot_ephemerals'][i * max_bits_in_point_idx + bit_i]
                client_eph = client_ephemerals[f'ephemeral_{i}_{bit_i}']

                # print(f'{client_eph=}')
                # print(f'{seph=}')
                # print(f'{peph=}')

                _, k_ciphertexts = oblivious_transfer_encrypt_messages(
                    i_keys[bit_i],
                    mcl_from_str(seph, mcl.Fr),
                    mcl_from_str(peph, mcl.G1),
                    mcl_from_str(client_eph, mcl.G1)
                )

                response_payload[f'ciphertexts_{i}_{bit_i}'] = \
                    [cip.hex() for cip in k_ciphertexts]

        db_data = None
    else:
        db_data = None
        response_payload = None

    return db_data, response_payload
