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


def _xor_bytes(ba1: bytes, ba2: bytes) -> bytes:
    assert len(ba1) == len(ba2), f'XOR {len(ba1)=} != {len(ba2)=}'
    # xored = bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])
    # print(f"_xor_bytes: {xored=}")
    # print(f"right side: {ba2=}")

    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

#######################
# Encryption/decryption
#######################

# [TODO] If message contains x00 at the end,
# then the decryption will fail.
def encrypt(message_bytes: bytes, key_bytes: bytes) -> bytes:
    assert len(message_bytes) <= len(key_bytes),\
        f'encrypt: {len(message_bytes)=} > {len(key_bytes)=}'
    # Adjust to the length of the key since it has the length of the longest
    # message
    message_aligned = message_bytes.ljust(len(key_bytes), b"\x00")
    # Print with blue color
    # print(f"\033[94mencrypt: {message_bytes=}\033[0m")

    encrypted = _xor_bytes(message_aligned, key_bytes)

    # Decrypt the message here and check that it is the same as the original
    # message
    decrypted = decrypt(encrypted, key_bytes)
    # print(f"\033[94mencrypt: {message_bytes=}\033[0m")
    if decrypted != message_bytes:
        print("Decryption failed!")
        print(f"\033[91m{message_bytes=}\033[0m")
        print(f"\033[91m{decrypted=}\033[0m")

    return encrypted    


def decrypt(ciphertext_bytes: bytes, key_bytes: bytes) -> bytes:
    assert len(ciphertext_bytes) <= len(key_bytes),\
        f'{len(ciphertext_bytes)=} > {len(key_bytes)=}'

    # Print with pink color
    decrypted = _xor_bytes(ciphertext_bytes, key_bytes).rstrip(b"\x00")    
    # print(f"\033[95mdecrypt: {decrypted=}\033[0m")
    return decrypted


# [TODO]? make generic xor encryption and decryption functions
# One ciphertext with many keys
# def batch_decrypt(ciphertext_bytes: bytes, keys: list[bytes]) -> list[bytes]:
#     plaintext = ciphertext_bytes
#     for key in keys:
#         assert len(ciphertext_bytes) <= len(key),\
#             f'{len(ciphertext_bytes)=} > {len(key)=}'

#         plaintext = _xor_bytes(plaintext, key)

#     plaintext = plaintext.rstrip(b"\x00")
#     return plaintext

#######################
# Other utils
#######################
