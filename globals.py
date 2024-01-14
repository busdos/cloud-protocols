from enum import Enum

import mcl

_SEC_PAR = b'test'
GENERATOR = mcl.G1.hashAndMapTo(_SEC_PAR)

# Security paramters and contants for oblivious
# polynomial evaluation protocol. For meaning of
# the parameters see the OPEClient class comments.
#
# [TODO] move somewhere else or integrate with
# the protocol
OPE_MAIN_POLY_DEGREE = 4
OPE_QUERY_POLY_DEGREE = 3
OPE_MASK_POLY_DEGREE = OPE_QUERY_POLY_DEGREE * OPE_MAIN_POLY_DEGREE

OPE_SECURITY_PARAM_M = 2
OPE_SMALL_N = OPE_QUERY_POLY_DEGREE * OPE_MAIN_POLY_DEGREE + 1
OPE_BIG_N = OPE_SMALL_N * OPE_SECURITY_PARAM_M

OPE_DEFAULT_CLIENT_SEED = 'client_seed'
OPE_DEFAULT_SERVER_SEED = 'server_seed'

class Protocols(Enum):
    ONE_OF_TWO = 'one_of_two'
    ONE_OF_N = 'one_of_n'
    OPE = 'oblivious_polynomial_evaluation'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def get_values(cls):
        return cls._value2member_map_.keys()

    @classmethod
    def get_as_list(cls):
        return list(cls._value2member_map_.keys())


# Actions are an ordered list of the requests (urls)
# sent by the client to the server
#
# The first element of the array is the initializing
# action, so when it occurs the server should
# generate a new session token
#
# The last element of the array is the closing
# action, so when it occurs the server should delete
# the session's data from the database
PROTOCOL_SPECS = {
    Protocols.ONE_OF_TWO.value: {
        'actions': [
            'get_A',
            'get_two_ciphertexts',
        ],
        'init_action': 'get_A',
        'close_action': 'get_two_ciphertexts'
    },
    Protocols.ONE_OF_N.value: {
        'actions': [
            'get_ciphertexts',
            'get_A',
            'get_two_ciphertexts',
            'done',
        ],
        'init_action': 'get_ciphertexts',
        'close_action': 'done'
    },
    Protocols.OPE.value: {
        'actions': [
            'get_server_ephemerals',
            'perform_n_of_big_n_ot',
        ],
        'init_action': 'get_server_ephemerals',
        'close_action': 'perform_n_of_big_n_ot',
    }
}
