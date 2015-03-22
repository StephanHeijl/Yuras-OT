from Yuras.common.StoredObject import StoredObject
import bcrypt, scrypt, base64, time, os

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random

from Yuras.common.Config import Config

class User(StoredObject):
	_encrypt = True
	
	def __init__(self):
		self.username = ""
		
		self.firstname = ""
		self.lastname = ""
		
		self.email = ""
		self.password = ""
		self.documents = []
		
		super(User, self).__init__(collection = "users")
		
	@staticmethod
	def getMostCommonPasswords(n=10000):
		with open(os.path.join( Config().WebAppDirectory, "../..", "common-passwords.txt"), "r") as cpw:
			passwords = cpw.read().split("\n")
		return passwords[:n]
	
	def matchObjects(self, match, limit=None, skip=0, fields={"referenceDocument":0}, sort=None,reverse=False):
		# Does not return reference template by default
		return super(User, self).matchObjects(match,limit,skip,fields,sort,reverse)
	
	def getReferenceDocument(self):
		try:
			return self.matchObjects({"_id":self._id}, limit=1, fields={"referenceDocument":1})[0].referenceDocument
		except:
			return None
	
	def setPassword(self, password):
		hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(Config().bcryptDifficulty))
		
		if self.checkPassword(password):
			return False
		
		self.password = hashedPassword
		self.createUserKeyPair(password)
		del password
		return True
		
	def checkPassword(self, password):
		if self.password == "":
			return True
		try:
			return self.password == bcrypt.hashpw(
				password.encode('utf-8'),
				self.password.encode('utf-8'))
		except:
			return False
	
	def createUserKeyPair(self, password):
		password = password.encode('utf-8')
		salt = Random.new().read(32)
		
		print "Generating Scrypt hash"
		t = time.time()
		derived_key = scrypt.hash(password, salt, N=1<<Config().scryptDifficulty)[:32]
		print "Took %s s." % (time.time()-t)
		
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
		
	# Flask-Login integration
	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return str(self._id)