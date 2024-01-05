import argparse

import client_actions.client_one_of_two as oo2
import client_actions.client_one_of_n as oon
import globals as gl

LIST_OF_CLIENTS = {
    gl.Protocols.ONE_OF_TWO.value: oo2.one_of_two_client,
    gl.Protocols.ONE_OF_N.value: oon.one_of_n_client,
    # "ope": ope.oblivious_polynomial_evaluation,
    # "gc": gc.garbled_circuit,
    # "psi": psi.private_set_intersection,
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
