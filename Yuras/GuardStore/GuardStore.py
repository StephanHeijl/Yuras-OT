class GuardStore(object):
	def __init__(self):
		pass
	
	def secureDocument(self, _id, user):
		pass 
		# document = Document.getById(_id)
		# key = Random.read(1024)
		# encryptedDocument = self.__encryptDocumentAES( document.contents, key)
		# encryptedKey = self.__encryptDocumentKey(key, user)
		# Document.contents = encryptedDocument
		# storedKey = Key()
		# Key(documentId = _id, userId = user._id, key=encryptedKey)		
	
	def __encryptDocumentAES(self, document, key):
		pass
		# encryptedDocument = encrypt(document, key)
		# return encryptedDocument
	
	def __encryptDocumentKey(self, key, user):
		pass
		# encryptedKey = user.publicKey.encrypt(key)
		# return encryptedKey
		
	def unlockDocument(self, _id, user, password):
		pass 
		# encryptedKey = Key.getByField(documentId=_id,userId=user._id)
		# document = Document.getById(_id)
		# if len(encryptedKey) == 0:
		# 	return False
		# decryptedPrivateKey = self.__decryptUserPrivateKey(user, password)
		# decryptedDocumentKey = self.__decryptDocumentKey(encryptedKey, decryptedPrivateKey)
		# document.contents = self.__decryptDocumentAES(document.contents, decryptedDocumentKey)
		# return document
		

	def __decryptDocumentAES(self, document, key):
		pass
		# decryptedDocument = decrypt(document, key)
		# return decryptedDocument
	
	def __decryptUserPrivateKey(self, user, password):
		pass 
		# derivedPassKey = derive(password, user.salt)
		# return decrypt( user.privateKey, 
	
	def __decryptDocumentKey(self, key, privateKey):
		pass
		# encryptedKey = user.privateKey
		# return encryptedKey
		