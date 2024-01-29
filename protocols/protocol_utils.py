import hashlib

#######################
# Hashing-related utils
#######################
_HASH_FUNCTION = hashlib.sha3_512
_HASH_LENGTH = _HASH_FUNCTION().digest_size


def compute_hash(msg: bytes) -> bytes:
    return _HASH_FUNCTION(msg).digest()


def _get_number_of_blocks(msg_len: int) -> int:
    num_of_blocks = (msg_len)//_HASH_LENGTH
    if msg_len % _HASH_LENGTH != 0:
        num_of_blocks += 1
    
    return num_of_blocks


def concatenated_hashes(msg_len: int, key: bytes) -> bytes:
    num_of_blocks = _get_number_of_blocks(msg_len)
    int_len = num_of_blocks.bit_length()
    return b''.join(
        compute_hash(key + idx.to_bytes(int_len, 'little'))
        for idx in range(num_of_blocks))

#######################
#### Byteops utils ####
#######################

def xor_bytes(ba1: bytes, ba2: bytes) -> bytes:
    assert len(ba1) == len(ba2), f'XOR {len(ba1)=} != {len(ba2)=}'
    # xored = bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])
    # print(f"_xor_bytes: {xored=}")
    # print(f"right side: {ba2=}")

    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

def is_power_of_two(n: int) -> bool:
    return n != 0 and (n & (n - 1)) == 0
