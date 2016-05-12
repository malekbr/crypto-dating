# circuit-related functions go here
from hashlib import sha256
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# takes a bytearray as input for a seed, deterministically returns
# a list of 6 random byte strings
def generate_keys(seed):
    seed = bytearray(seed)
    keys = []
    for i in xrange(6):
        current_seed = bytearray()
        for c in seed:
            current_seed.append(c^i)
        keys.append(sha256(current_seed).digest())
    return keys


def generate_circuit(seed, choice, first):
    """ seed is a bytearray, choice is boolean, first is boolean """

    circuit = {}
    keys = generate_keys(seed)
    w = keys[0:2]
    x = keys[2:4]
    y = keys[4:6]

    # kept as a secret
    circuit['false'] = base64.b64encode(w[0])
    circuit['true'] = base64.b64encode(w[1])

    r = []
    r.append(encrypt(x[0], y[0], w[0]))
    r.append(encrypt(x[0], y[1], w[0]))
    r.append(encrypt(x[1], y[0], w[0]))
    r.append(encrypt(x[1], y[1], w[1]))

    # sent to server
    w.sort()
    r.sort()

    if first:
        circuit['choice'] = base64.b64encode(x[choice])
    else:
        circuit['choice'] = base64.b64encode(y[choice])

    circuit['wa'] = base64.b64encode(w[0])
    circuit['wb'] = base64.b64encode(w[1])
    circuit['r1'] = base64.b64encode(r[0])
    circuit['r2'] = base64.b64encode(r[1])
    circuit['r3'] = base64.b64encode(r[2])
    circuit['r4'] = base64.b64encode(r[3])

    return circuit

# We are using any key only once, so we can use a nonce of 0

def encrypt(x_key, y_key, w):
    c_x = Cipher(algorithms.AES(x_key), modes.CTR(b'\x00'*16), default_backend()).encryptor()
    c_y = Cipher(algorithms.AES(y_key), modes.CTR(b'\x00'*16), default_backend()).encryptor()
    return c_x.update(c_y.update(w) + c_y.finalize()) + c_x.finalize()

def decrypt(x_key, y_key, e):
    c_x = Cipher(algorithms.AES(x_key), modes.CTR(b'\x00'*16), default_backend()).decryptor()
    c_y = Cipher(algorithms.AES(y_key), modes.CTR(b'\x00'*16), default_backend()).decryptor()
    return c_y.update(c_x.update(e) + c_x.finalize()) + c_y.finalize()

def DH_get_key_pair():
    private_key = ec.generate_private_key(
    	ec.SECP256R1(), default_backend()
    	)
    return private_key, base64.b64encode(private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo))

def DH_get_shared(private_key, peer_public_bytes):
    peer_public_key = serialization.load_pem_public_key(base64.b64decode(peer_public_bytes),
                                                        default_backend())

    return private_key.exchange(ec.ECDH(), peer_public_key)

def verify(circuit_1, circuit_2):
    if circuit_1[:6] != circuit_2[:6]:
        return None
    choice_1, choice_2 = circuit_1[-1], circuit_2[-1]
    ws = [decrypt(choice_1, choice_2, r) for r in circuit_1[2:6]]
    ws = [w for w in ws if w in circuit_1[:2]]
    if len(ws) != 1:
        return None
    return base64.b64encode(ws[0])
