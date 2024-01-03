from uuid import uuid4

###################
# Routing utilities
###################

def generate_sample_messages(num: int):
    return [f"This is message number {i}".encode('ascii') for i in range(num)]

def generate_token():
    return str(uuid4())

def mcl_to_str(mcl):
    return mcl.serialize().hex()

def mcl_from_str(mcl_str: str, val_type):
    mcl_val = val_type()
    mcl_val.deserialize(bytes.fromhex(mcl_str))
    return mcl_val