from SecureBox.Sistema import Sistema
from SecureBox.utils import TypeRet
from tkinter import Entry, PhotoImage, Button, Canvas, messagebox, Label, Toplevel
from GUI.utils_view import ASSET_PATH

class LoginCanvas(Canvas):
    """
        Canvas que representa el contenido de los contenedores
        de los usuarios.
    """
    def __init__(self, master=None, alter=None):
        super().__init__(master, height=400, width=600, bg="black")
        self.master = master
        self.place(x=0, y=0)
        self.alter_canvas = alter
        self.create_elements()
    
    def create_elements(self):
        """
            Método de inicialización de objetos que se
            muestran en la pantalla
        """

        self.title = Label(self, text="SecureBox", font=("Arial", 24, "bold"), fg="white", bg="black")
        self.title.place(x=380, y=40)

        self.nickname_label = Label(self, text="NickName", font=("Arial", 14, "bold"), fg="white", bg="black")
        self.nickname_label.place(x=380, y=90)
        self.nickname_entry = Entry(self, font=("Arial", 12), bg="lightgray", fg="black")
        self.nickname_entry.place(x=380, y=120, width=180, height=25)

        self.password_label = Label(self, text="Password", font=("Arial", 14, "bold"), fg="white", bg="black")
        self.password_label.place(x=380, y=160)
        self.password_entry = Entry(self, font=("Arial", 12), bg="lightgray", fg="black", show="*")
        self.password_entry.place(x=380, y=190, width=180, height=25)

        self.button_image_login = PhotoImage(file=ASSET_PATH + "button_1.png")
        self.button_login = self.add_button(event=self.login_action, pos_x=400, pos_y=230, width=134, height=30, name="", button_image=self.button_image_login)

        self.button_image_reg = PhotoImage(file=ASSET_PATH + "button_3.png")
        self.button_register = self.add_button(event=self.register_action, pos_x=400, pos_y=270, width=134, height=30, name="", button_image=self.button_image_reg)

        self.button_image_res = PhotoImage(file=ASSET_PATH + "button_2.png")
        self.button_restore = self.add_button(event=self.restore_action, pos_x=400, pos_y=310, width=134, height=30, name="", button_image=self.button_image_res)

        self.bg_image = PhotoImage(file=ASSET_PATH + "image_1.png")
        self.image_bg = self.create_image(161.0, 199.0, image=self.bg_image)

    def add_button(self, event, pos_x, pos_y, width, height, name, button_image) -> Button:
        """
            Método que permite añadir un botón en una posición del canvas.
            Params:
                - event (fun): método que se instancia al hacer click sobre el botón.
                - pos_x (float): posición x en la que se va a ubicar el botón.
                - pos_y (float): posición y en la que se va a ubicar el botón.
                - width (float): anchura a representar del botón.
                - height (float): altura a representar del botón.
                - name (str): Nombre que se muestra del botón.
                - button_Image: Imagen que se coloca sobre el botón.
        """

        button = Button(
            master=self,
            text=name,
            image=button_image,
            borderwidth=0,
            highlightthickness=0,
            command=event,
            compound="center"
        )
        button.place(x=pos_x, y=pos_y, width=width, height=height)

        button.bind("<Enter>", lambda e: button.config(cursor="hand2"))
        button.bind("<Leave>", lambda e: button.config(cursor="arrow"))

        return button

    
    def restore_action(self):
        """
            Acción del botón button_restore, que permite la 
            restauración de la base de datos desde drive
        """
        okl = messagebox.askokcancel("Restore", f"¿Desea restarura la base de datos desde Drive?")
        if okl == True:
            Sistema._instance.restore_database()


    def login_action(self):
        """
            Acción del botón button_login, que permite el 
            acceso al usuario tras introducir los datos
            correctos.
        """

        nickname = self.nickname_entry.get().strip()
        password = self.password_entry.get().strip()
        
        ret = Sistema._instance.login(nickname, password)
        if ret == TypeRet.OK:
            messagebox.showinfo("Login", f"Bienvenido, {nickname}!", parent=self)
            self.alter_canvas()
        elif ret == TypeRet.NO_DB:
            print("Aqui entro")
            okl = messagebox.askokcancel("Restore", f"No hay ninguna bbdd en el sistema, ¿desea restarurala desde Drive?")
            if okl == True:
                Sistema._instance.restore_database()

        elif ret == TypeRet.FAILED:
            messagebox.showwarning("Error", "Usuario o contraseña incorrectos.")
        elif ret == TypeRet.HACKING:
            messagebox.showerror("Error", "Se está forzando en acceso.\nLa bbdd será borrada.")
        else:
            messagebox.showwarning("Warning", "Se desconoce el error.")

    def register_action(self):
        """
            Acción del botón button_register, que permite a 
            un usuario registrarse en el sistema.
        """
        modal = RegisterModal(self)
        self.wait_window(modal)


class RegisterModal(Toplevel):
    """
        Ventana Modal que permite el
        ingresar los datos de un nuevo
        usuario.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ingrese los datos de registro")
        self.transient(parent)  # Hace que la ventana sea modal
        self.grab_set()  # Bloquea la ventana principal hasta cerrar la modal

        Label(self, text="Nickname:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_nickname = Entry(self)
        self.entry_nickname.grid(row=0, column=1, padx=10, pady=5)

        Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_clave = Entry(self, show="*")
        self.entry_clave.grid(row=1, column=1, padx=10, pady=5)

        self.btn_ok = Button(self, text="Aceptar", command=self.cerrar)
        self.btn_ok.grid(row=2, column=0, columnspan=2, pady=10)


    def cerrar(self):
        """
            Acción del botón btn_ok, instanciada
            tras el añadido de los datos del usuario.
        """

        entry_nickname = self.entry_nickname.get()
        key = self.entry_clave.get()
        
        ret = Sistema._instance.register(nickname=entry_nickname, password=key)
        if ret == TypeRet.FAILED:
            messagebox.showerror("Error", "Ese nickname ya se encuentra en uso.")
        
        self.destroy() 
