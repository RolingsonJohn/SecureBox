from tkinter import Tk, messagebox
from SecureBox.Sistema import Sistema
from GUI.login_canvas import LoginCanvas
from GUI.container_canvas import ContainerCanvas

def alter_cont():
    """
        Función que permite
        el aternar entre el login
        y la vista del contenedor
    """
    global login_canvas, container_canvas
    print("Aqui llego")
    login_canvas.pack_forget()
    container_canvas.charge_tree()
    container_canvas.pack()

def alter_login():
    """
        Función que permite
        el aternar entre la vista
        del contenedor y el login
    """

    global login_canvas, container_canvas
    print("Aqui llego")
    container_canvas.pack_forget()
    login_canvas.pack()

def kill_window():
    """
        Handler del cerrado de la ventana
    """

    global window
    if messagebox.askokcancel("Salir", "¿Desea guardar un backup?"):
        Sistema._instance.save_data(True)
    else:
        Sistema._instance.save_data(False)
    window.destroy()    
        

def login_view():
    global login_canvas, container_canvas, window

    window = Tk()
    window.title("Login")
    window.geometry("600x400")
    window.resizable(False, False)
    window.configure(bg = "black")
    window.protocol("WM_DELETE_WINDOW", kill_window)

    if messagebox.askokcancel("Integridad", "¿Desea verificar la integridad de su base de datos con un backup anterior?", parent=window):
        if Sistema._instance.pull_checksum():
            messagebox.showinfo("Correcto", "El checksum de la base de datos actual coincide con el del backup.", parent=window)
        else:
            messagebox.showwarning("Warning", "El checksum de la base de datos actual no coincide con el del backup.\nSe recomienda restaurar la base de datos.", parent=window)

    login_canvas = LoginCanvas(window, alter=alter_cont)
    login_canvas.pack()

    container_canvas = ContainerCanvas(window, alter=alter_login)
    container_canvas.pack()

    window.mainloop()
