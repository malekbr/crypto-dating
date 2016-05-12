from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization



class signingClient:
	def __init__(self):
		self.private_key = dsa.generate_private_key(key_size = 2048, backend = default_backend())
		self.public_key = self.private_key.public_key()

	# Signs a message with RSA digital signature protocol with appendix according to PKCS#1 PSS.
	# input:
	#			message as a bytes file
	#	return: the signature for the message using the private key of self
	def sign(self, message):
		signer = self.private_key.signer(hashes.SHA256())
		signer.update(message)
		signature = signer.finalize()
		return signature

	# return the public key of self
	def getPublicKey(self):
		return self.public_key

	# return public bytes of public key
	def getPublicBytes(self):
		return self.public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)



# verifies the signature having public key and the message as well
# input: signature as a PKCS1_PSS.signature
#			public_key RSA generated key of the signer
#			message as a byte file
#	return: True if the signature corresponds to public key, False otherwise
def verify(signature, public_key, message):
	verifier = public_key.verifier(signature, hashes.SHA256())
	verifier.update(message)
	try:
		verifier.verify()
		return True
	except:
		return False


# client = signingClient()
# message = "to be signed"
# message1 = "not signed"
# signature = client.sign(message)
# print verify(signature, client.getPublicKey(), message1)
