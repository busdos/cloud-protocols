import argparse

import client_actions.client_one_of_n as oon
import client_actions.client_one_of_two as oo2
import client_actions.client_oblivious_polynomial_evaluation as ope
import client_actions.client_designated_sig_signer as desig
import globals as gl

LIST_OF_CLIENTS = {
    gl.Protocols.ONE_OF_TWO.value: oo2.one_of_two_client,
    gl.Protocols.ONE_OF_N.value: oon.one_of_n_client,
    gl.Protocols.OPE.value: ope.ope_client,
    # gl.Protocols.GARBLED_CIRCUIT.value: gc.garbled_circuit_client,
    # "psi": psi.private_set_intersection,
    gl.Protocols.DESIG.value: desig.desig_client
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--p",
        dest="protocol",
        choices=gl.Protocols.get_as_list(),
        required=True)
    parser.add_argument("--u", dest="url", required=True)
    args = parser.parse_args()

    LIST_OF_CLIENTS[args.protocol](args.url)


if __name__ == "__main__":
    print("Starting client...")
    main()
