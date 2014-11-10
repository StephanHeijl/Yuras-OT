import argparse
from base64 import b64encode

# Crypto imports #
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto import Random


class FileEncryptor(object):
	def loadFile(self, filename):
		with open(filename) as file:
			fileContents = file.read()
		return fileContents
	
	def encryptContents(self, keyFileName, contents):
		with open(keyFileName,"r") as keyFile:
			publicKey = RSA.importKey(keyFile.read())
		if not publicKey.can_encrypt():
			raise ValueError, "This is a private key, you can't use this to encrypt this file."
		
		keyLength = 32
		
		# Pad the contents to a multiple of the block size
		padChar = "@"
		padLength = keyLength - len(contents) % keyLength
		contents = contents.rjust(len(contents) + padLength, padChar)
					
		# Encrypt the file with a random 256 bit key.
		randomKey = Random.new().read(keyLength)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(randomKey, AES.MODE_CBC, iv)
		encryptedContents = cipher.encrypt(contents)
		
		# Encrypt the random key.
		cipher = PKCS1_OAEP.new(publicKey)
		self.encryptedRandomKey = cipher.encrypt(randomKey)
		del randomKey # Remove the key from memory.
		
		return encryptedContents
	
	def storeEncryptedKey(self, outputFileName):
		with open(outputFileName, "w") as encryptedKeyFile:
			encryptedKeyFile.write(b64encode(self.encryptedRandomKey))
	
	def storeEncrypted(self, outputFileName, encryptedContents):
		with open(outputFileName, "wb") as encryptedFile:
			encryptedFile.write(encryptedContents)
			
	def storeEncryptedB64(self, outputFileName, encryptedContents):
		with open(outputFileName, "w") as encryptedFile:
			encryptedFile.write(b64encode( encryptedContents))
		
	
# ARGPARSER - For use as a command line util #
parser = argparse.ArgumentParser(description="Encrypt a file.")
parser.add_argument("--in", help="The file you need to encrypt.", type=str,required=True)
parser.add_argument("--out", help="Where to store the encrypted file.", type=str,required=True)
parser.add_argument("--key", help="The public key you'd like to encrypt the symmetric key with.", type=str,required=True)
parser.add_argument("--b64", help="Convert the encrypted file to base64", action="store_true")

# RUNNING #
if __name__ == "__main__":
	args = vars(parser.parse_args())
	FE = FileEncryptor()
	f =  FE.loadFile(args["in"])
	ec = FE.encryptContents(args["key"],f)
	if args["b64"]:
		FE.storeEncryptedB64(args["out"],ec)
	else:
		FE.storeEncrypted(args["out"],ec)
		
	FE.storeEncryptedKey(args["out"]+".key")
	
	

# TESTING #

