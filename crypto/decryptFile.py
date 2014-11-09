import argparse
from base64 import b64decode

# Crypto imports #
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA

class FileDecryptor(object):	
	def loadEncryptedFile(self,filename):
		with open(filename) as file:
			fileContents = file.read()
		return fileContents
	
	def decryptContents(self, privateKeyFileName, keyFileName, contents, base64=False):
		with open(privateKeyFileName,"r") as privateKeyFile:
			privateKey = RSA.importKey(privateKeyFile.read())
		if not privateKey.can_sign():
			raise ValueError, "This is a public key, you can't use this to encrypt this file."
		
		cipher = PKCS1_OAEP.new(privateKey)
		if base64:
			contents = b64decode(contents)
		
		with open(keyFileName, "r") as keyFile:
			binaryKey = b64decode(keyFile.read())
			
		decryptedKey = cipher.decrypt(binaryKey)
		
		cipher = AES.new(decryptedKey)		
		decryptedContents = cipher.decrypt(contents)
		
		return decryptedContents
	
	def storeDecrypted(self, outputFileName, decryptedContents):
		with open(outputFileName, "w") as decryptedFile:
			decryptedFile.write(decryptedContents)
	
# ARGPARSER - For use as a command line util #
parser = argparse.ArgumentParser(description="Decrypt a file.")
parser.add_argument("--in", help="The file you need to decrypt.", type=str,required=True)
parser.add_argument("--out", help="Where to store the decrypted file.", type=str,required=True)
parser.add_argument("--privateKey", help="The private key you'd like to decrypt the key this file was encrypted with.", type=str,required=True)
parser.add_argument("--key", help="The encrypted keyfile this file was encrypted with.", type=str,required=True)
parser.add_argument("--b64", help="Convert the encrypted file from base64", action="store_true")

# RUNNING #
if __name__ == "__main__":
	args = vars(parser.parse_args())
	FD = FileDecryptor()
	f =  FD.loadEncryptedFile(args["in"])
	dc = FD.decryptContents(args["privateKey"],args["key"],f, args["b64"])
	FD.storeDecrypted(args["out"],dc)
	