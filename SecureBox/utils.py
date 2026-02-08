import os
from datetime import datetime
from enum import Enum
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2

edited = False

class TypeRet(Enum):
    """
        Distintos tipos de retorno
    """
    OK = 0
    FAILED = -1
    HACKING = -200
    NO_DB = -2
    REP = -3

def print_err(e:Exception):
    """
        Función de impresión de errores con la hora exacta
    """
    print(f"[{datetime.today()}] Warning: {e}")

def print_info(e:str):
    """
        Función de impresión de información con la hora exacta
    """
    print(f"[{datetime.today()}] {e}")

def xor_operation(a: bytes, b: bytes, size: int) -> bytes:
    """
        Operación xor entre dos operandos, especificando su tamaño.
        El resultado se almacena en formato big endian.
        Params:
            - a (bytes): Primer operando.
            - b (bytes): Segundo operando.
            - size (int): Tamaño de los operandos
        Return:
            - Resultado de la operación xor
    """
    int_a = int.from_bytes(a, 'big')
    c = int.from_bytes(b, 'big') ^ int_a

    return int.to_bytes(c, length=size, byteorder='big')

def encryption(mensaje:str, key:bytes)-> str:
    """
        Función de cifrado de un mensaje, especificando una clave.
        Emplea el cifrado AES en el modo de operación Galois Counter Mode.
        Params:
            - mensaje (str): Mensaje que se busca cifrar.
            - key (bytes): Clave empleada para cifrar el mensaje.
        Return:
            - La concatenación del nonce + Mensaje cifrado + tag
    """
    
    if mensaje.strip() == '':
        return ''
    
    nonce = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(mensaje.encode('utf-8'))
    return nonce + ciphertext + tag

def decryption(cif_data:str, key:bytes)-> bytes:
    """
        Función de descifrado de un mensaje, especificando una clave.
        Emplea el cifrado AES en el modo de operación Galois Counter Mode,
        gracias a este modo también se puede verificar si un mensaje ha sido
        modificado, gracias a su tag.
        Params:
            - cif_data (str): Mensaje que se busca descifrar.
            - key (bytes): Clave empleada para cifrar el mensaje.
        Return:
            - Mensaje en claro
    """
    
    if cif_data.strip() == '':
        return bytes(0)

    nonce = cif_data[:12]
    ciphertext = cif_data[12:-16]
    tag = cif_data[-16:]

    if isinstance(cif_data, str):
        nonce = nonce.encode('utf-8')
        ciphertext = ciphertext.encode('utf-8')
        tag = tag.encode('utf-8')
    
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


def derivate_key(password: str, salt: int)-> str:
    """
        Función empleada para derivar una clave a partir
        de un secreto junto a un salt.
        Params:
            - password(str): Contraseña del usuario
            - salt (int): Número aleatorio grande
        Return:
            - Clave derivada empleada para el cifrado
    """
    return PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module=SHA256)