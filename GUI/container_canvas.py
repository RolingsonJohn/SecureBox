from SecureBox.Sistema import Sistema
from tkinter import Entry, PhotoImage, Button, Canvas, messagebox, Label, ttk, Text, Toplevel
from tkinter.simpledialog import askstring
from GUI.utils_view import SlidePanel
from pathlib import Path

class ContainerCanvas(Canvas):
    """
        Canvas que representa el contenido de los contenedores
        de los usuarios.
    """
    def __init__(self, master=None, alter=None):
        super().__init__(master, height=400, width=600, bg="black")
        self.master = master
        self.place(x=0, y=0)
        self.alter = alter
        self.create_elements()
    

    def create_elements(self):
        """
            Método de inicialización de objetos que se
            muestran en la pantalla
        """

        self.title = Label(self, text="SecureBox", font=("Arial", 24, "bold"), fg="white", bg="black")
        self.title.place(x=50, y=40)

        self.tree = ttk.Treeview(self, columns=("Name"), show="headings", selectmode="browse")
        self.tree.place(x=200, y=100)

        self.tree.heading("Name", text="Name")
        self.tree.column("Name", width=200)

        self.button_edit = self.add_button(event=self.modified_content, pos_x=20, pos_y=100, width=134, height=30, name="Edit")
        self.button_view = self.add_button(event=self.view_content, pos_x=20, pos_y=130, width=134, height=30, name="View")
        self.button_add = self.add_button(event=self.add_container, pos_x=20, pos_y=160, width=134, height=30, name="Add Cont.")
        self.button_del = self.add_button(event=self.del_container, pos_x=20, pos_y=190, width=134, height=30, name="Del Cont.")
        self.button_back = self.add_button(event=self.go_back, pos_x=20, pos_y=220, width=134, height=30, name="Back")

        self.slide_panel = SlidePanel(self.master, 1.0, 0.7)


    def charge_tree(self):
        self.tree.delete(*self.tree.get_children())
        for cont in Sistema._instance.usuario.contenedores.keys():
            self.tree.insert("", "end", values=cont)


    def add_button(self, event, pos_x, pos_y, width, height, name, button_image=None) -> Button:
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
            borderwidth=5,
            highlightthickness=0,
            command=event,
            compound="center"
        )
        button.place(x=pos_x, y=pos_y, width=width, height=height)

        button.bind("<Enter>", lambda e: button.config(cursor="hand2"))
        button.bind("<Leave>", lambda e: button.config(cursor="arrow"))

        return button
    

    def go_back(self):
        """
            Acción del botón button_back, que permite
            el retroceder a la ventana principal de la app.
        """

        self.alter()

    def del_container(self):
        """
            Acción del botón button_del, que permite
            el borrado de un contenedor.
        """

        selected_items = self.tree.selection()
        if selected_items:
            selected_item = self.tree.item(selected_items[0])
            nombre_cont = selected_item['values'][0]
            clave = askstring(f'{nombre_cont}', 'Introduzca la clave del contenedor', show='*', parent=self)
            clave = clave if clave is not None else ""

            if not Sistema._instance.usuario.delete_container(name=nombre_cont, cont_password=clave):
                messagebox.showwarning("Incorrecto", "La contraseña introducida es incorrecta.")

        else:
            modal = AddContainerModal(self)
            modal.btn_ok.config(command=modal.del_container)
            self.wait_window(modal)
        self.charge_tree()


    def add_container(self):
        """
            Acción del botón button_add, que permite
            el añadido de un contenedor.
        """

        modal = AddContainerModal(self)
        modal.btn_ok.config(command=modal.add_container)
        self.wait_window(modal)
        self.charge_tree()


    def accept_button_action(self, cont, clave):
        """
            Acción del botón de edición del desplegable,
            que confirma la edición del conteneido de un contenedor.
            Params:
                - cont (Contenedor): contenedor con los campos a editar.
                - clave (str): Contraseña del contenedor.
        """

        cont.touch_data(clave, self.slide_panel.content.get("1.0", "end-1c"))
        self.slide_panel.animate()
        self.slide_panel.content.delete("1.0", "end")


    def modified_content(self):
        """
            Acción del botón button_edit, que permite
            la edición del contenido de un contenedor.
        """

        selected_items = self.tree.selection()
        if selected_items:
            selected_item = self.tree.item(selected_items[0])
            nombre_cont = selected_item['values'][0]
            clave = askstring(f'{nombre_cont}', 'Introduzca la clave del contenedor', show='*', parent=self)
            clave = clave if clave is not None else ""

            cont = Sistema._instance.usuario.contenedores.get(nombre_cont)
            if cont.check_password(clave) == True:
                if self.slide_panel.content.get("1.0", "end-1c").strip() == "":
                    self.slide_panel.content.insert("1.0", cont.descif_data(clave))

                self.slide_panel.button_accept.config(command=lambda: self.accept_button_action(cont, clave))
                self.slide_panel.animate()

            else:
                messagebox.showerror("Error", "Contraseña errónea.")
        else:
            messagebox.showerror("Datos", "Debe seleccionar un contenedor.")


    def view_content(self):
        """
            Acción del botón button_view, que permite
            visualizar el contenido de un contenedor.
        """

        selected_items = self.tree.selection()
        if selected_items:
            selected_item = self.tree.item(selected_items[0])
            nombre_cont = selected_item['values'][0]
            clave = askstring(f'{nombre_cont}', 'Introduzca la clave del contenedor', show='*', parent=self)
            clave = clave if clave is not None else ""
            
            cont = Sistema._instance.usuario.contenedores.get(nombre_cont)
            if cont.check_password(clave) == True:
                messagebox.showinfo(f"{nombre_cont}", cont.descif_data(clave), parent=self)
            else:
                messagebox.showerror("Error", "Contraseña errónea.", parent=self)
        else:
            messagebox.showerror("Datos", "Debe seleccionar un contenedor.")


class AddContainerModal(Toplevel):
    """
        Ventana Modal que permite el
        ingresar los datos de un contenedor
        que se quiere eliminar/añadir.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ingrese los datos del nuevo contenedor")
        self.transient(parent)  # Hace que la ventana sea modal
        self.grab_set()  # Bloquea la ventana principal hasta cerrar la modal

        Label(self, text="Contenedor:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_cont = Entry(self)
        self.entry_cont.grid(row=0, column=1, padx=10, pady=5)

        Label(self, text="Clave:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_clave = Entry(self, show="*")
        self.entry_clave.grid(row=1, column=1, padx=10, pady=5)

        self.btn_ok = Button(self, text="Aceptar", command=self.cerrar)
        self.btn_ok.grid(row=2, column=0, columnspan=2, pady=10)

    def cerrar(self):
        self.destroy()

    def add_container(self):
        """
            Método que permite recopilar
            la información para la creación de un
            contenedor y su posterior creación.
        """

        cont = self.entry_cont.get()
        key = self.entry_clave.get()

        ret = Sistema._instance.usuario.add_container(name=cont, cont_password=key)
        self.destroy()
    
    def del_container(self):
        """
            Método que permite recopilar
            la información para el borrado de un
            contenedor y su posterior eliminación.
        """
        cont = self.entry_cont.get()
        key = self.entry_clave.get()

        ret = Sistema._instance.usuario.delete_container(name=cont, cont_password=key)
        self.destroy()