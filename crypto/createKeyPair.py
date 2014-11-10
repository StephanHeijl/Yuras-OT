from Crypto.PublicKey import RSA
from Crypto import Random

class KeyPairGenerator(object):
	def __init__(self):
		self.random = Random.new()
		self.key = None
		self.name = "sample"
		
	def createKeyPair(self):
		self.key = RSA.generate(4096, self.random.read)
		return self.key
		
	def getPublicKey(self):
		if self.key is None:
			raise ValueError, "You need to run `createKeyPair` first."
		
		return self.key.publickey().exportKey()
	
	def getPrivateKey(self):
		if self.key is None:
			raise ValueError, "You need to run `createKeyPair` first."
			
		return self.key.exportKey()
	
	def storePublicKey(self):
		publicKey = self.getPublicKey()
		with open("%s_rsa_id.pub" % self.name, "w") as pubFile:
			pubFile.write(publicKey)
	
	def storePrivateKey(self):
		privateKey = self.getPrivateKey()
		with open("%s_rsa_id.ppk" % self.name, "w") as priFile:
			priFile.write(privateKey)
		
		
# RUNNING #

if __name__ == "__main__":
	kpg = KeyPairGenerator()
	kpg.createKeyPair()
	kpg.storePublicKey()
	kpg.storePrivateKey()
