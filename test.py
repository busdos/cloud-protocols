from protocols import oblivious_polynomial_evaluation as ope
from mcl import Fr
import globals as gl

def test_ope():
    alpha = Fr()
    alpha.setInt(10)

    query_polynomial = ope.OPEPolynomial(
        gl.OPE_QUERY_POLY_DEGREE,
        gl.OPE_DEFAULT_CLIENT_SEED
    )
    query_polynomial.set_val_at_zero(alpha)

    client = ope.OPEClient()
    _ = client.gen_submerged_points_indices(
        gl.OPE_SMALL_N,
        gl.OPE_BIG_N
    )
    query_x_values = client.gen_query_x_values(
        gl.OPE_BIG_N
    )
    query_y_values = client.produce_query_y_values(
        query_polynomial,
    )

    query_points = [
        (query_x_values[i], query_y_values[i])
        for i in range(len(query_x_values))
    ]
    print(f'{len(query_points)=}')

    ### Cloud ops ###

    main_polynomial = ope.OPECloud.gen_main_polynomial(
        gl.OPE_MAIN_POLY_DEGREE,
        gl.OPE_DEFAULT_SERVER_SEED
    )
    expected_result = main_polynomial(alpha)

    mask_polynomial = ope.OPECloud.gen_mask_polynomial(
        gl.OPE_MASK_POLY_DEGREE,
        gl.OPE_DEFAULT_SERVER_SEED + '1'
    )

    cloud_values = ope.OPECloud.compute_masked_polynomial_values(
        main_polynomial,
        mask_polynomial,
        query_points
    )

    print(f'{len(cloud_values)=}')

    # User ops
    result = client.eval_result_polynomial(
        cloud_values
    )

    print(f'{expected_result=}')
    print(f'{result=}')

    assert expected_result == result

if __name__ == '__main__':
    test_ope()