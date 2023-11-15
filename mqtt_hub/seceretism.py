from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib, sys, os

dirPath = os.path.dirname(os.path.realpath(__file__))

def generate_key(username, pw):
    
    key = hashlib.pbkdf2_hmac(hash_name='sha256', password=pw.encode('utf8'), salt=username.encode('utf8'), iterations=100000)

    with open(dirPath+"/secretism.bin", "wb") as f:
        f.write(key)
    return key

def read_key():
    try:
        with open(dirPath+"/secretism.bin", "rb") as f:
            key = f.read()
    except FileNotFoundError:
        key = generate_key()
    if(sys.getsizeof(key) != 65):
        key = generate_key()
    return key

def check_key(username, pw):
    try:
        with open(dirPath+"/secretism.bin", "rb") as f:
            ekey = f.read()
    except FileNotFoundError:   # There is no login informations
        return -1
    
    nkey = hashlib.pbkdf2_hmac(hash_name='sha256', password=pw.encode('utf8'), salt=username.encode('utf8'), iterations=100000)

    if(ekey != nkey):   # Doesn't match
        return 1
    
    elif(ekey == nkey): # Match
        return 0
    


def seceretism(data, username, pw):
    key = read_key()

    il = [0 for i in range(16)]
    for i in range(len(username)):
        il[15-i] = 0 ^ ord(username[len(username)-i-1])
    for i in range(len(pw)):
        il[15-i] = il[15-i] ^ ord(pw[len(pw)-i-1])

    iv = bytes(il)
    block_size = 256

    aes = AES.new(key, AES.MODE_OFB, iv)
    paded_data = pad(data.encode('utf8'), block_size)
    cipher_text = aes.encrypt(paded_data)

    return cipher_text.hex()

def unsecretism(cipher_text, username, pw):
    key = read_key()

    il = [0 for i in range(16)]
    for i in range(len(username)):
        il[15-i] = 0 ^ ord(username[len(username)-i-1])
    for i in range(len(pw)):
        il[15-i] = il[15-i] ^ ord(pw[len(pw)-i-1])

    iv = bytes(il)
    block_size = 256
    aes = AES.new(key, AES.MODE_OFB, iv)

    decrypted_data = aes.decrypt(bytes.fromhex(cipher_text))
    plain_text = unpad(decrypted_data, block_size).decode('utf8')

    return plain_text

def __eg():
    cipher=seceretism('hellow123 !@#$')
    plain=unsecretism(cipher)
    print(plain)