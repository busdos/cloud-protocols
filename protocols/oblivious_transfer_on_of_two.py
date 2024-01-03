"""
Simple one-of-2 oblivious transfer protocol.
"""
from secrets import SystemRandom
from mcl import *
from enum import Enum

from . import protocol_utils as ut

class MessageChoice(Enum):
    FIRST = 0
    SECOND = 1

class OneOfTwoCloud():
    @staticmethod
    def gen_ephemerals(generator: G1):
        secret_ephemeral = Fr.rnd()
        public_ephemeral = generator * secret_ephemeral

        return (secret_ephemeral, public_ephemeral)

    @staticmethod
    def encrypt_messages(client_pub_eph: G1,
                         secret_eph: Fr,
                         public_eph: G1,
                         messages: list[bytes]):
        assert len(messages) == 2,\
            "Number of messages must be 2."
        key1 = ut.compute_hash(client_pub_eph * secret_eph)
        key2 = ut.compute_hash((client_pub_eph - public_eph) * secret_eph)

        longest_msg_len = len(max(messages, key=len))

        encryption_str1 = ut.concatenated_hashes(longest_msg_len,
                                                 key1)
        encryption_str2 = ut.concatenated_hashes(longest_msg_len,
                                                 key2)

        ciphertext1 = ut.encrypt(messages[0],
                                 encryption_str1)
        ciphertext2 = ut.encrypt(messages[1],
                                 encryption_str2)

        return [ciphertext1, ciphertext2]


class OneOfTwoClient():
    def __init__(self, generator: G1, choice: MessageChoice):
        self.choice = choice
        self.generator = generator
        self.secret_ephemeral = Fr()
        self.public_ephemeral = G1()

    def set_choice(self, choice: MessageChoice):
        self.choice = choice

    def gen_ephemerals(self, cloud_pub_ephemeral: G1):
        self.secret_ephemeral = Fr.rnd()
        self.public_ephemeral = self.generator * self.secret_ephemeral
        if self.choice == MessageChoice.SECOND:
            self.public_ephemeral *= cloud_pub_ephemeral
        
        self.encryption_key = ut.compute_hash(self.public_ephemeral * self.secret_ephemeral)
    
    def get_public_ephemeral(self):
        return self.public_ephemeral

    def decrypt(self, ciphertexts: list[bytes]):
        assert len(ciphertexts) == 2,\
            "Number of ciphertexts must be 2."

        encryption_str = ut.concatenated_hashes(len(ciphertexts[self.choice]),
                                                self.encryption_key)
        
        return ut.decrypt(ciphertexts[self.choice], encryption_str)
