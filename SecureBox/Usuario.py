import os
import hashlib as h
import sqlite3 as sql
from uuid import uuid4
import SecureBox.utils as u
from SecureBox.Config import DATABASE
from SecureBox.Contenedor import Contenedor

class Usuario:
    """
        Clase Usuario
    """
    def __init__(self, id="", name="", password="", nonce=0, salt=0):
        self.id = id
        self.name = name
        self.password = password
        self.contenedores = dict()
        self.nonce = nonce
        self.salt = salt


    def delete_container(self, name:str, cont_password:str):
        """
            Método que permite a un usuario eliminar
            un contenedor de su repertorio de contenedores
            Params:
                - self: Atributo de la clase
                - name(str): Nombre del nuevo contenedor
                - cont_password(str): Contraseña del nuevo contenedor 
        """
        
        cont = self.contenedores.get(name)
        if cont.check_password(cont_password):
            try:
                con = sql.connect(DATABASE)
                cur = con.cursor()

                cur.execute("DELETE FROM Contenedor WHERE ContainerId = ?", (str(cont.id),))

                cur = None
                con.commit()
                con.close()
                self.contenedores.pop(name)
            except Exception as e:
                u.print_err(e)

            u.edited = True
            return True
        return False
                

    def add_container(self, name:str, cont_password:str):
        """
            Método que permite a un usuario añadir
            un contenedor nuevo a su repertorio de
            contenedores
            Params:
                - self: Atributo de la clase
                - name(str): Nombre del nuevo contenedor
                - cont_password(str): Contraseña del nuevo contenedor 
        """

        salt = os.urandom(16)

        derivated_password = u.derivate_key(self.password, self.salt)

        cif_cont_name = u.encryption(name, derivated_password)

        h_cont_password = h.sha256(salt + cont_password.encode('utf-8')).hexdigest()
        cif_cont_password = u.encryption(h_cont_password, derivated_password)

        contenedor = Contenedor(id=uuid4(), name=cif_cont_name, hashed_password=h_cont_password, cif_text="", salt=salt)
        self.contenedores.update({name:contenedor})
        number = os.urandom(16)
        salt_xor = u.xor_operation(salt, number, 16)

        try:
            con = sql.connect(DATABASE)
            cur = con.cursor()

            cur.execute("INSERT INTO Contenedor VALUES (?, ?, ?, ?, ?, ?, ?)", (str(contenedor.id), self.id, cif_cont_name, cif_cont_password, "", salt_xor + number, os.urandom(16)))

            cur = None
            con.commit()
            con.close()
        except sql.IntegrityError as e:
            u.print_err(e)
            return u.TypeRet.REP
        except Exception as e:
            u.print_err(e)
            return u.TypeRet.FAILED

        u.edited = True

    
    def load_containers(self, password:str):
        """
            Método que carga los datos del usuario que inicia sesión
            Params:
                - self: atributos de la clase
                - password(str): Contraseña del usuario
        """
        
        con = sql.connect(DATABASE)
        cur = con.cursor()

        cur.execute("SELECT * FROM Contenedor WHERE UserId = ?", (self.id,))
        contenedores = cur.fetchall()

        derivate_password = u.derivate_key(password, self.salt)

        for cont in contenedores:

            cont_name = u.decryption(cif_data=cont[2], key=derivate_password).decode('utf-8')
            h_cont_password = u.decryption(cif_data=cont[3], key=derivate_password).decode('utf-8')

            data = cont[5]
            salt_xor = data[:16]
            number = data[-16:]

            salt = u.xor_operation(salt_xor, number, 16)

            contenedor = Contenedor(id=cont[0], name=cont[2], hashed_password=h_cont_password, cif_text=cont[4], salt=salt)
            self.contenedores.update({cont_name:contenedor})
        
        cur = None
        con.close()