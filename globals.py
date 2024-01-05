import mcl
from enum import Enum

_SEC_PAR = b'test'
GENERATOR = mcl.G1.hashAndMapTo(_SEC_PAR)

class Protocols(Enum):
    ONE_OF_TWO = 'one_of_two'
    ONE_OF_N = 'one_of_n'

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
    }
}
