import os
import sqlite3 as sql
from uuid import uuid4
import hashlib as h
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2

con = sql.connect('secure_box.db')
cur = con.cursor()

uidUsuario = uuid4()

salt = os.urandom(16)

nick = "alumnodb"
password = "alumnodb"
h_name = h.sha256(nick.encode('utf-8')).hexdigest()
h_password = h.sha256(salt + password.encode('utf-8')).hexdigest()

uidContenedor = uuid4()
name_cont = "contenedor_1"
password_cont = "contenedor_1"
h_password_cont = h.sha256(salt + password_cont.encode('utf-8')).hexdigest()

# Derivar clave
# Clave del usuario
derivated_password = PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)

# Clave contenedor
derivated_password_cont = PBKDF2(password_cont, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)

# Cifrado de la clave

def encryption(mensaje:str, key:bytes)-> str:
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(mensaje.encode('utf-8'))
    return nonce + ciphertext + tag

def dencryption(cif_data:str, key:bytes)-> tuple:
    nonce = cif_data[:12]
    ciphertext = cif_data[12:-16]
    tag = cif_data[-16:]

    if isinstance(cif_data, str):
        nonce = nonce.encode('utf-8')
        ciphertext = ciphertext.encode('utf-8')
        tag = tag.encode('utf-8')

    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt(ciphertext)

# Clave del Contenedor
cif_name_cont = encryption(name_cont, derivated_password)
cif_password_cont = encryption(h_password_cont, derivated_password)

cif_data = encryption("Contenido del contenedor 1", derivated_password_cont)

ope_xor = int.from_bytes(os.urandom(16), 'big')
salt_xor = int.from_bytes(salt, 'big') ^ ope_xor

salt_xor = int.to_bytes(salt_xor, length=16, byteorder='big')
ope_xor = int.to_bytes(ope_xor, length=16, byteorder='big')

print(f"1.\nsalt_xor = {salt_xor}\nsalt = {salt}\nnum_gen = {ope_xor}\n\tA + B = {salt_xor + ope_xor}")

cur.execute("INSERT INTO Usuario VALUES (?, ?, ?, ?, ?, ?)", (str(uidUsuario), h_name, h_password,
                                                             salt_xor + ope_xor, os.urandom(16), os.urandom(16)))

cur.execute("INSERT INTO Contenedor VALUES (?, ?, ?, ?, ?, ?, ?)", (str(uidContenedor), str(uidUsuario), 
                                                                   cif_name_cont, cif_password_cont, cif_data,
                                                                   salt_xor + ope_xor, os.urandom(16)))

descif_name_cont = dencryption(cif_name_cont, derivated_password)
descif_password_cont = dencryption(cif_password_cont, derivated_password)
descif_data = dencryption(cif_data, derivated_password_cont)

# print(derivated_password, descif_name_cont, descif_password_cont, descif_data)

con.commit()

cur.execute("SELECT * FROM Usuario")
data = cur.fetchone()

waska = data[3]

waska_salt = waska[:16]
waska_ope = waska[-16:]

print(f"2.\nsalt_xor = {waska_salt}\nnum_gen = {waska_ope}\nwaska = {waska}\nall_data = {data}\n")

print(int.to_bytes(int.from_bytes(waska_salt, 'big') ^ int.from_bytes(waska_ope, 'big'), length=16, byteorder='big'))
print(salt)


con.close()