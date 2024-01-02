"""
One of n oblivious transfer protocol.
Uses one-of-2 oblivious transfer protocol.
"""
import sys

class OneOfNCloud():
    """
    Simple cloud which holds messages of the same size as long as
    it exists. Transaction key are generated every time a message
    is requested by the client.
    """
    def __init__(self, message_length) -> None:
        self.message_length = message_length
        self.messages = []
        self.transaction_keys = []