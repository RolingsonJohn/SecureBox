import hashlib as h

import SecureBox.utils as u


class Contenedor:
    """
        Clase Contenedor
    """
    def __init__(self, id="", name:str="", hashed_password:str="", cif_text:str="", salt=0):
        self.id = id
        self.name = name
        self.password = hashed_password
        self.text = cif_text
        self.salt = salt


    def check_password(self, password:str="") -> bool:
        """
            Método encargado de comprobar la contraseña del contenedor
            introducida por el usuario con la bbdd.
            Params:
                - password str: contraseña del contenedor.
            Return:
                - bool: true/false
        """
        h_password = h.sha256(self.salt + password.encode('utf-8')).hexdigest()
        # A John le hacía ilusión...
        return False if h_password != self.password else True 


    def descif_data(self, password:str="") -> str:
        """
            Método encargado de descifrar el contenido del contenedor
            para ser mostrado posteriormente.
            Params:
                - password str: contraseña del contenedor.
            Return:
                - str: contenido descifrado.
        """
        h_password = h.sha256(self.salt + password.encode('utf-8')).hexdigest()
        if h_password != self.password:
            return None
        
        derivated_password = u.derivate_key(password=password, salt=self.salt)
        descif_data = u.decryption(self.text, derivated_password) 

        return descif_data


    def touch_data(self, password:str="", data_to_keep:str = "") -> bool:
        """
            Método encargado de cifrar el contenido introducido por el usuario
            para ser guardado posteriormente.
            Params:
                - password str: contraseña del contenedor.
                - data_to_keep str: contenido a guardar.
            Return:
                - bool: true/false autenticación
        """
        h_password = h.sha256(self.salt + password.encode('utf-8')).hexdigest()
        if h_password != self.password:
            return False
        
        derivated_password = u.derivate_key(password=password, salt=self.salt)
        self.text = u.encryption(data_to_keep, derivated_password)

        u.edited = True
        
        return True