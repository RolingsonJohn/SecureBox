from SecureBox.Sistema import Sistema
from SecureBox.utils import print_err
from GUI.gui import login_view
from terminal_lobby import *

if __name__ == '__main__':
    Sistema()
    
    print("Seleccione el modo de visualización:\n\t1. GUI\n\t2. Terminal\n\r")
    option = input("> ").strip()

    #try:
    option = int(option)
    if option == 1:
        login_view()
    elif option == 2:
        lobby()
    else:
        print("Opción no soportada\n\r")
    #except Exception as e:
        #print_err(e)
