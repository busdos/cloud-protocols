import logging

from protocols import oblivious_polynomial_evaluation as ope
from protocols import designated_signature as desig

from mcl import Fr
import globals as gl

def test_ope():
    alpha = Fr()
    alpha.setInt(1123124)

    query_polynomial = ope.OPEPolynomial(
        gl.OPE_QUERY_POLY_DEGREE,
        gl.OPE_DEFAULT_CLIENT_SEED
    )
    query_polynomial.set_val_at_zero(alpha)

    client = ope.OPEClient()
    submerged_indices = client.gen_submerged_points_indices(
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

    interpolation_y_values = [
        cloud_values[i]
        for i in submerged_indices
    ]

    print(f'{len(cloud_values)=}')

    # User ops
    result = client.eval_result_polynomial(
        interpolation_y_values
    )

    print(f'{expected_result=}')
    print(f'{result=}')

    assert expected_result == result

def test_desig():

    logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')
    signer = desig.Desig_Sign()
    forwarder = desig.Desig_Forward()
    verifier = desig.Desig_Ver()
    logging.info(f'{gl.GENERATOR=}')
    print(f'{gl.GENERATOR=}')

    assert desig.PKI["signer"][1]  == gl.GENERATOR*signer.sk
    assert desig.PKI["forwarder"][1]  == gl.GENERATOR*forwarder.sk


    m = "123"
    sigma = signer.sign(m)

    assert forwarder.verify(sigma,m,gl.GENERATOR*signer.sk)
    sigma_desig = forwarder.designation(sigma, desig.PKI['verifier'][1], desig.PKI['signer'][1])

    assert verifier.verify(sigma_desig, m, desig.PKI['signer'][1])

if __name__ == '__main__':
    # test_ope()
    test_desig()
