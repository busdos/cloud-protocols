from mcl import *
import globals as gl

PKI = {
    "signer" :      [sk_s := Fr(), G1()],
    "forwarder" :   [sk_f := Fr(), G1()],
    "verifier" :    [sk_v := Fr(), G1()],
}

PKI["signer"][0].deserialize(   bytes.fromhex('2321fb7b6c08399b0e6805b986af45f1d1eb6c744690167b4d973cf3d1a49360'))
PKI["forwarder"][0].deserialize(bytes.fromhex('9781e83419e5e1c53edaf3870f1ae65b58df8b15e385e59f9ed365e705d39822'))
PKI["verifier"][0].deserialize( bytes.fromhex('337c1366a4ee0c8b24704255d70b92230f4d2e83d2f4d19aa17ae52a9b50b642'))

PKI["signer"][1]     = gl.GENERATOR*PKI["signer"][0]
PKI["forwarder"][1]  = gl.GENERATOR*PKI["forwarder"][0]
PKI["verifier"][1]   = gl.GENERATOR*PKI["verifier"][0]

_SEC_PAR = b"test"
Q = G1.hashAndMapTo(_SEC_PAR)


class Desig_Sign():
    def __init__(self):
        self.sk = PKI['signer'][0]

    def sign(self, m):
        k = Fr.rnd()
        u = gl.GENERATOR * k
        r = Fr.setHashOf(f'{m}{u}'.encode())
        s = k + r * self.sk
        return (r, s)

class Desig_Forward():
    def __init__(self) -> None:
        self.sk = PKI['forwarder'][0]

    def verify(self, sigma, m, pk_sign) -> bool:
        r,s = sigma
        u = (gl.GENERATOR*s) - (pk_sign*r)
        return r == Fr.setHashOf(f'{m}{u}'.encode())

    def designation(self,sigma, pk_des, pk_sign):
        r,s = sigma
        u = (gl.GENERATOR*s) - (pk_sign*r)
        K = pk_des * s
        return (u, K)

class Desig_Ver():
    def __init__(self) -> None:
        self.sk = PKI['verifier'][0]


    def verify(self, sigma, m, pk_sign) -> bool:
        u,K = sigma
        r = Fr.setHashOf(f'{m}{u}'.encode())
        return K == (u + (pk_sign*r)) * self.sk