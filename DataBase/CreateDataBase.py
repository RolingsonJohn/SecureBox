import sqlite3 as sql

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
