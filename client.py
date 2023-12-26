import argparse

import protocols as pr

# [TODO] these should be bindings to protocol routes and
# not protcols themselves
LIST_OF_PROTOCOLS = {
    "one-of-n": pr.one_of_n,
    "oblivious-polynomial-evaluation": pr.oblivious_polynomial_evaluation,
    "garbled-circuit": pr.garbled_circuit,
    "private-set-intersection": pr.private_set_intersection,
}

PROTOCOL_CHOICE = list(LIST_OF_PROTOCOLS.keys())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--p",
        dest="protocol",
        choices=PROTOCOL_CHOICE,
        required=True)
    parser.add_argument("--u", dest="url", required=True)
    args = parser.parse_args()

    LIST_OF_PROTOCOLS[args.protocol](args.url)

if __name__ == "__main__":
    main()
