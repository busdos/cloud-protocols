"""
Simple one-of-2 oblivious transfer protocol.
"""
from secrets import SystemRandom

from mcl import G1, Fr

from . import protocol_utils as ut


class OTCloud():
    @staticmethod
    def gen_ephemerals(generator: G1) -> (Fr, G1):
        # Only needed for 2 messages
        secret_ephemeral = Fr.rnd()
        public_ephemeral = generator * secret_ephemeral

        # print(f"cloud public_ephemeral: {public_ephemeral}")
        return (secret_ephemeral, public_ephemeral)

    @staticmethod
    def compute_keys(number_of_messages:int,
                     longest_msg_len: int,
                     client_pub_eph: G1 = None,
                     secret_eph: Fr = None,
                     public_eph: G1 = None)-> list[(bytes, bytes)]:
        assert number_of_messages >= 2,\
            "Number of messages must be at least 2."
        # print(f"Number of messages: {number_of_messages}")

        if number_of_messages == 2:
            # Stringifying is important because implicit
            # conversion of an object to bytes for hashing might
            # not work the same on clinet and server side
            keys = [(
                (client_pub_eph * secret_eph).getStr(),
                ((client_pub_eph - public_eph) * secret_eph).getStr()
            )]
        else:
            rand = SystemRandom()
            keys = [(rand.randbytes(longest_msg_len),
                     rand.randbytes(longest_msg_len))
                     for _ in range(number_of_messages.bit_length())]

        return keys

    def _select_key_indices(no_of_messages: int,
                           message_idx: int)-> list[int]:
        selected_keys = list(map(
            lambda i: (message_idx >> i) & 1,
            range((no_of_messages - 1).bit_length())
        ))

        return selected_keys

    def _encrypt_message(minimal_encryption_key_len: int,
                         key_indices: list[int],
                         keys: list[(bytes, bytes)],
                         message: bytes):
        ciphertext = message

        # print(f"\033[91mMessage of the same length as the key! Should not happen unless already padded! \033[0m")
        # print(f"\033[91m{message_bytes=}\033[0m")


        # Print with blue color
        # print(f"\033[94mencrypt: {message_bytes=}\033[0m")
    
        # Adding one to enforce the padding on the original message
        minimal_enc_str_len = minimal_encryption_key_len + 1
        for i in range(len(keys)):
            # Selecte key_indices[i]th element of the pair keys[i]
            encryption_str = ut.concatenated_hashes(
                minimal_enc_str_len, keys[i][key_indices[i]])

            # Pad the initial message            
            if i == 0:
                # Append \x01 and then \x00 until
                # the length is the same as the key
                ciphertext = message + b"\x01" + b"\x00" * (
                    len(encryption_str) - len(message) - 1)

            ciphertext = ut.xor_bytes(ciphertext, encryption_str)

        return ciphertext

    @staticmethod
    def encrypt_messages(longest_msg_len: int,
                         keys: list[(bytes, bytes)],
                         messages: list[bytes]) -> list[bytes]:

        number_of_messages = len(messages)

        ciphertexts = []
        for i in range(number_of_messages):
            # [TODO] Could be a pre-defined matrix for small
            # number of messages
            m_i_key_indices = OTCloud._select_key_indices(
                number_of_messages, i)

            # print(f"m_i_key_indices: {m_i_key_indices}")

            ciphertexts.append(
                OTCloud._encrypt_message(
                    longest_msg_len,
                    m_i_key_indices,
                    keys,
                    messages[i])
            )

        return ciphertexts


class OneOfTwoClient():
    @staticmethod
    def gen_ephemerals_and_enc_key(
        generator: G1,
        cloud_pub_ephemeral: G1,
        choice_idx: int
    ) -> (Fr, G1, bytes):
        secret_ephemeral = Fr.rnd()
        public_ephemeral = generator * secret_ephemeral
        # If second message is chosen...
        if choice_idx == 1:
           public_ephemeral += cloud_pub_ephemeral

        # Stringifying is important because implicit conversion of and object to bytes
        # for hashing might not work the same on clinet and server side
        encryption_key = (cloud_pub_ephemeral * secret_ephemeral).getStr()

        return (secret_ephemeral, public_ephemeral, encryption_key)

    @staticmethod
    def decrypt_message(
        ciphertext: bytes,
        encryption_keys: list[bytes],
    ):
        for i in range(len(encryption_keys)):
            decryption_str = ut.concatenated_hashes(
                len(ciphertext),
                encryption_keys[i])

            ciphertext = ut.xor_bytes(ciphertext, decryption_str)

        ciphertext = ciphertext.rstrip(b"\x00")
        if ciphertext[-1:] == b'\x01':
            ciphertext = ciphertext[:-1]
        else:
            print(f"\033[91mDecrypted string did not have \\x01 at the end! This should NOT happen!\033[0m")
            print(f"\033[91m{ciphertext=}\033[0m")

        return ciphertext

    # [TODO] Change the structure of this clas to merge decrypt and batch_decrypt
    # into one method
    @staticmethod
    def batch_decrypt(ciphertext: bytes, keys: list[bytes]):
        plaintext = ciphertext
        for key in keys:
            decryption_str = ut.concatenated_hashes(
                len(ciphertext),
                key)

            plaintext = ut.xor_bytes(plaintext, decryption_str)

        plaintext = plaintext.rstrip(b"\x00")
        # Remove exactly one \x01 byte from the end
        # if it exists
        if plaintext[-1:] == b'\x01':
            plaintext = plaintext[:-1]
        else:
            print(f"\033[91m{plaintext=}\033[0m")
            print(f"\033[91mDecrypted string did not have \\x01 at the end! This should NOT happen!\033[0m")

        return plaintext