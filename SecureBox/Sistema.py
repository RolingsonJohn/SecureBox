import os
import hashlib as h
import sqlite3 as sql
from datetime import datetime
from uuid import uuid4
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import SecureBox.utils as u
from SecureBox.Config import DATABASE, DATABASEBK, CONFIG_DRIVE, CHECKSUM
from SecureBox.Usuario import Usuario

MAX_ATTEMPTS = 10

class Sistema:
    """
        Clase Singleton
    """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Sistema, cls).__new__(cls)
            cls._instance.counter = 0
        return cls
    

    def __init__(self):
        self.usuario = None
        self.counter = 0


    def register(self, nickname: str, password: str):
        """
            Método encargado de registrar nuevos usuarios
            en la bbdd.
            Params:
                - nickname str: Nombre del usuario.
                - password str: Contraseña con la que se registra.
        """
        if not os.path.exists(DATABASE):
            return u.TypeRet.NO_DB

        salt = os.urandom(16)
        number = os.urandom(16)

        h_nick = h.sha256(nickname.encode('utf-8')).hexdigest()
        h_password = h.sha256(salt + password.encode('utf-8')).hexdigest()
        salt_xor = u.xor_operation(salt, number, 16)
        
        try:
            con = sql.connect(DATABASE)
            cur = con.cursor()
            
            user = Usuario(id=uuid4(), name=nickname, password=password)
            cur.execute("INSERT INTO Usuario VALUES (?, ?, ?, ?, ?, ?)", (str(user.id), h_nick, h_password, salt_xor + number, os.urandom(16), os.urandom(16)))
        
            con.commit()
            con.close()

        except sql.IntegrityError as e:
            u.print_err(e)
            return u.TypeRet.REP
        except Exception as e:
            u.print_err(e)
            return u.TypeRet.FAILED

        self.usuario = user
        u.edited = True


    def login(self, nickname: str, password: str) -> u.TypeRet:
        """
            Método encargado del inicio de sesión de un usuario.
            Se realiza comprobando el hash de los argumentos introducidos
            por el usuario con el valor almacenado en la bbdd.
            Params:
                - nickname str: nombre del usuario.
                - password str: contraseña con la que se registró el usuario.
            Return:
                - TypeRet: código de retorno según la situación.
        """

        if not os.path.exists(DATABASE):
            return u.TypeRet.NO_DB

        # Invulnerable, se guarda hash. Te hasheo la inyección, tonto :P
        h_nick = h.sha256(nickname.encode('utf-8')).hexdigest()

        con = sql.connect(DATABASE)
        cur = con.cursor()
        
        cur.execute("SELECT Email FROM Usuario WHERE Nickname = ?", (h_nick,))
        data = cur.fetchone()

        if data is None:
            u.print_err("Usuario no registrado.")
            return u.TypeRet.FAILED
        
        data = data[0]

        salt_xor = data[:16]
        number = data[-16:]

        salt = u.xor_operation(salt_xor, number, 16)

        h_password = h.sha256(salt + password.encode('utf-8')).hexdigest()

        try:
            cur.execute("SELECT 1 FROM Usuario WHERE Nickname = ? AND Password = ?", (h_nick, h_password,))
            coincidence = cur.fetchone()

            if coincidence is None or coincidence[0] != 1:
                if self.counter == MAX_ATTEMPTS:
                    os.remove(DATABASE)
                    self.counter = 0
                    return u.TypeRet.HACKING
                self.counter += 1
                print("Contraseña incorrecta")
                return u.TypeRet.FAILED
            
            cur.execute("SELECT UserId FROM Usuario WHERE Nickname = ? AND Password = ?", (h_nick, h_password,))
            usuario = cur.fetchone()

            self.usuario = Usuario(id=usuario[0], name=nickname, password=password, salt=salt)
            cur = None
            con.close()

            self.usuario.load_containers(password=password)

        except Exception as e:
            u.print_err(e)    
            cur = None
            con.close()
            return False
        return u.TypeRet.OK


    def save_data(self, bk:bool):
        """
            Método encargado de actualizar el contenido de los contenedores.
            Generalmente utilizada al final de la ejecución.
            Adicionalmente sube un backup y su checksum a la nube (Google Drive).
            Params:
                - bk bool: flag utilizada para identificar si se ha modificado
                el contenido de algún contenedor durante la ejecución.
        """
        if u.edited:
            con = sql.connect(DATABASE)
            cur = con.cursor()

            for cont in self.usuario.contenedores.values():
                print(cont.text, cont.id,  self.usuario.id)
                print(type(cont.text), type(cont.id), type(self.usuario.id))
                cur.execute("UPDATE Contenedor SET Text = ? WHERE ContainerId = ? AND UserId = ?", (cont.text, str(cont.id), str(self.usuario.id)))

            cur = None
            con.commit()
            con.close()

            if bk:
                gauth = GoogleAuth()
                gauth.LoadClientConfigFile(CONFIG_DRIVE)
                gauth.LocalWebserverAuth()
                
                drive = GoogleDrive(gauth)
                self.push_checksum(drive)
                self.save_backup(drive)


    def save_backup(self, drive):
        """
            Método encargado de subir un backup de la bbdd
            a Google Drive.
            Utilizada en bloque junto a push_checksum().
            Params:
                - drive GoogleAuth: conexión oauth de Google.
        """
        file_to_upload = drive.CreateFile({'title':f'[{datetime.now()}]_{DATABASEBK}'})
        file_to_upload.SetContentFile(DATABASE)
        file_to_upload.Upload()


    def restore_database(self):
        """
            Método encargado de descargar el backup de la bbdd más
            actualizado encontrado en Google Drive.
            Sobreescribe la bbdd local.
        """
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile(CONFIG_DRIVE)
        gauth.LocalWebserverAuth()

        drive = GoogleDrive(gauth)

        file_list = drive.ListFile({'q': f"title contains '{DATABASEBK}'"}).GetList()
        file_list[0].GetContentFile(DATABASE)

        u.print_info(f"Archivo descargado: {file_list[0]['title']}")
        

    def pull_checksum(self):
        """
            Método encargado de comprobar el checksum del backup más
            actualizado para mantener la integridad de la bbdd.
        """
        gauth = GoogleAuth()
        gauth.LoadClientConfigFile(CONFIG_DRIVE)
        gauth.LocalWebserverAuth()

        drive = GoogleDrive(gauth)

        file_list = drive.ListFile({'q':f"title contains '{CHECKSUM}'"}).GetList()
        checksum_drive = file_list[0].GetContentString()

        with open(DATABASE, 'rb') as db:
            data = db.read()
            checksum = h.sha256(data).hexdigest()
        
        u.print_info(f"Archivo descargado: {file_list[0]['title']}")
        u.print_info(f"Código SHA-256 Local  = {checksum}")
        u.print_info(f"Código SHA-256 Remoto = {checksum_drive}")
        if checksum.strip() != checksum_drive.strip():
            u.print_err("Checksum Local no coincide con el remoto")
            return False

        return True
    

    def push_checksum(self, drive):
        """
            Método encargado de subir el checksum de la bbdd
            a Google Drive.
            Utilizada en bloque junto a save_backup().
            Params:
                - drive GoogleAuth: conexión oauth de Google.
        """
        with open(DATABASE, 'rb') as db:
            data = db.read()
            checksum = h.sha256(data).hexdigest()
        
        file_to_upload = drive.CreateFile({'title':f'[{datetime.now()}]_{CHECKSUM}'})
        file_to_upload.SetContentString(checksum)
        file_to_upload.Upload()