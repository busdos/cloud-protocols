from uuid import uuid4

###################
# Routing utilities
###################

def generate_token():
    return str(uuid4())

def mcl_to_str(mcl):
    return mcl.serialize().hex()

def mcl_from_str(mcl_str: str, val_type):
    mcl_val = val_type()
    mcl_val.deserialize(bytes.fromhex(mcl_str))
    return mcl_val

def mcl_from_bytes(mcl_bytes: bytes, val_type):
    mcl_val = val_type()
    mcl_val.deserialize(mcl_bytes)
    return mcl_val