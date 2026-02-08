import os
import unittest
import sqlite3 as sql
from SecureBox.Sistema import Sistema
from SecureBox.utils import TypeRet
from SecureBox.Config import DATABASE

class TestSistema(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)
        if os.path.exists(DATABASE):
           os.remove(DATABASE)

        con = sql.connect('secure_box.db')
        cur = con.cursor()

        cur.execute("""CREATE TABLE Usuario (
                        UserId VARCHAR(32) NOT NULL PRIMARY KEY,
                        Nickname BLOB UNIQUE,
                        Password BLOB,
                        Email BLOB,
                        Phone BLOB,
                        Image BLOB  
                    )""")

        cur.execute("""CREATE TABLE Contenedor (
                        ContainerId VARCHAR(32) NOT NULL PRIMARY KEY,
                        UserId VARCHAR(32),
                        Name BLOB UNIQUE,
                        Password BLOB,
                        Text BLOB,
                        Image BLOB,
                        NumKeys BLOB,
                        FOREIGN KEY (UserId) REFERENCES Usuario(UserId)
                    )""")
        con.commit()
        con.close()
        
        Sistema._instance.register("test", "test")

    def test_register(self):
        Sistema._instance.register("test2", "test2")
        self.assertEqual(Sistema._instance.login("test2", "test2"), TypeRet.OK)

    def test_login_failed_password(self):
        self.assertEqual(Sistema._instance.login("test", "1234"), TypeRet.FAILED)
    
    def test_login_failed_nouser(self):
        self.assertEqual(Sistema._instance.login("1234", "1234"), TypeRet.FAILED)

    def test_checksum(self):
        Sistema._instance.restore_database()
        self.assertTrue(Sistema._instance.pull_checksum())

    def test_brute_force(self):
        Sistema._instance.register("test", "test")
        for i in range(0, 100, 1):
            Sistema._instance.login("test", str(i))
        
        self.assertFalse(os.path.exists(DATABASE))
        self.setUp()



class TestUsuario(unittest.TestCase):

    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        if os.path.exists(DATABASE):
           os.remove(DATABASE)

        con = sql.connect('secure_box.db')
        cur = con.cursor()

        cur.execute("""CREATE TABLE Usuario (
                        UserId VARCHAR(32) NOT NULL PRIMARY KEY,
                        Nickname BLOB UNIQUE,
                        Password BLOB,
                        Email BLOB,
                        Phone BLOB,
                        Image BLOB  
                    )""")

        cur.execute("""CREATE TABLE Contenedor (
                        ContainerId VARCHAR(32) NOT NULL PRIMARY KEY,
                        UserId VARCHAR(32),
                        Name BLOB UNIQUE,
                        Password BLOB,
                        Text BLOB,
                        Image BLOB,
                        NumKeys BLOB,
                        FOREIGN KEY (UserId) REFERENCES Usuario(UserId)
                    )""")
        con.commit()
        con.close()

        Sistema._instance.login("test", "test")
        self.user = Sistema._instance.usuario

    def test_add_container(self):
        self.user.add_container("conttest", "conttest")
        self.assertListEqual(list(self.user.contenedores.keys()), ["conttest"])

    def test_delete_container(self):
        self.user.delete_container("conttest", "conttest")
        self.assertListEqual(list(self.user.contenedores.keys()), [])

    def test_edit_container(self):
        self.user.add_container("conttest", "conttest")
        cont = self.user.contenedores.get("conttest")
        cont.touch_data("conttest", "test")

        self.assertEqual(cont.descif_data("conttest").decode(), "test")


def ordenar_tests_sistema(test1, test2):
    if test1 == "test_brute_force":
        return 1
    if test2 == "test_brute_force":
        return -1
    return 0

def ordenar_tests_usuario(test1, test2):
    if test1 == "test_delete_container":
        return 1
    if test2 == "test_delete_container":
        return -1
    return 0

if __name__ == "__main__":
    Sistema()

    loader = unittest.TestLoader()
    loader.sortTestMethodsUsing = ordenar_tests_sistema
    suite = loader.loadTestsFromTestCase(TestSistema)
    unittest.TextTestRunner().run(suite)

    suite = loader.loadTestsFromTestCase(TestUsuario)
    unittest.TextTestRunner().run(suite)