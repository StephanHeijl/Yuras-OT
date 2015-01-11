from Yuras.common.StoredObject import StoredObject
import bcrypt, scrypt, base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random

from Yuras.common.Config import Config

class User(StoredObject):
	def __init__(self):
		self.username = ""
		
		self.firstname = ""
		self.lastname = ""
		
		self.email = ""
		self.password = ""
		self.documents = []
		
		super(User, self).__init__(collection = "users")
	
	def setPassword(self, password):
		hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(Config().bcryptDifficulty))
		
		if self.checkPassword(password):
			return False
		
		self.password = hashedPassword
		self.createUserKeyPair(password)
		del password
		return True
		
	def checkPassword(self, password):
		try:
			return self.password == bcrypt.hashpw(
				password.encode('utf-8'),
				self.password.encode('utf-8'))
		except:
			return False
	
	def createUserKeyPair(self, password):
		password = password.encode('utf-8')
		salt = Random.new().read(32)
		derived_key = scrypt.hash(password, salt)[:32]
		
		rsakey = RSA.generate(2048, Random.new().read)
		
		self.password_salt = base64.b64encode( salt )
		self.public_key = base64.b64encode( rsakey.publickey().exportKey() )
		iv = Random.new().read(AES.block_size)
		
		cipher = AES.new(derived_key, AES.MODE_CBC, iv)
		self.private_key_iv = base64.b64encode(iv)
		private_key = rsakey.exportKey()
		paddingChar = "{"
		self.private_key = base64.b64encode( cipher.encrypt( private_key + (AES.block_size - len(private_key) % AES.block_size) * paddingChar ) )
		
		del private_key		
		del derived_key