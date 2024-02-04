from mcl import G1
from globals import *

from routes_blueprint import route_utils as route_ut
from protocols import designated_signature as desig

from . import post_action

def desig_client(url):
    # _ELEMENTS = [x.to_bytes(2, 'big') for x in range(10)]
    MSG = "cloud"
    client = desig.Desig_Sign()


    _PROTOCOL_NAME = Protocols.DESIG.value
    _PROTOCOL_ACTIONS = PROTOCOL_SPECS[_PROTOCOL_NAME]["actions"]
    init_dic = {
        "protocol_name": _PROTOCOL_NAME,
        "payload": {
            "msg" : MSG,
            "sigma" : [route_ut.mcl_to_str(a) for a in client.sign(MSG)]
        }
    }
    print(url, _PROTOCOL_NAME, init_dic, _PROTOCOL_ACTIONS[0])
    resp_data = post_action(
        url,
        _PROTOCOL_NAME,
        _PROTOCOL_ACTIONS[0],
        init_dic
    )

    print(f'{resp_data["payload"]=}')