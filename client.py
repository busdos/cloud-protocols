import argparse

import protocols.oblivious_polynomial_evaluation as ope
import protocols.garbled_circuit as gc
import protocols.private_set_intersection as psi
import protocols.oblivious_transfer_one_of_n as otn

# [TODO] these should be bindings to client-side protocol functions
# (what client exectues as part of running the protocol with the server) and
# not protocols themselves
LIST_OF_PROTOCOLS = {
    "otn": otn.one_of_n,
    "ope": ope.oblivious_polynomial_evaluation,
    "gc": gc.garbled_circuit,
    "psi": psi.private_set_intersection,
}

PROTOCOL_CHOICE = list(LIST_OF_PROTOCOLS.keys())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        dest="protocol",
        choices=PROTOCOL_CHOICE,
        required=True)
    parser.add_argument("--u", dest="url", required=True)
    args = parser.parse_args()

    LIST_OF_PROTOCOLS[args.protocol](args.url)

if __name__ == "__main__":
    print("Starting client...")
    main()
