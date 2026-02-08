import curses

from SecureBox.Sistema import Sistema
from SecureBox.utils import print_err, TypeRet

def lobby():
    
    print("\n¿Desea verificar la integridad de su base de datos con un backup anterior?\n\t1. Sí\n\t2. No\n-----------------------------------\n\n")
    option = input("> ").strip()
    try:
        option = int(option)
        if option == 1:
            ret = Sistema._instance.pull_checksum()
            if ret:
                print("El checksum de la base de datos actual coincide con el del backup")
            else:
                print("El checksum de la base de datos actual no coincide con el del backup.\nSe recomienda restaurar la base de datos")
    except Exception as e:
        print_err(e)

    while(option != 'q'):

        print("\nIntroduzca la opción que desee:\n\t1. Iniciar Sesión\n\t2. Registrar Usuario\n\t3. Restaurar base de datos\n\tq. para salir\n-----------------------------------\n\n")
        option = input("> ").strip()
        try:
            option = int(option)
            if option == 1:
                show_login()
            elif option == 2:
                show_register()
            elif int(option) == 3:
                Sistema._instance.restore_database()
                print("La base de datos ha sido restaurada")
            else:
                print("Opción no soportada")
        except Exception as e:
            if option != 'q':
                print_err(e)
    
    print("\n¿Desea realizar un backup?\n\t1. Sí\n\t2. No\n-----------------------------------\n\n")
    option = input("> ").strip()
    try:
        option = int(option)
        if option == 1:
            Sistema._instance.save_data(True)
        elif option == 2:
            Sistema._instance.save_data(False)
        else:
            Sistema._instance.save_data(False)
    except Exception as e:
        print_err(e)


def show_register():

    print("Introduzca el nombre de usuario: ")
    nickname = input("> ").strip()
    print("Introduzca la contraseña: ")
    password = input("> ").strip()

    ret = Sistema._instance.register(nickname, password)
    if ret == TypeRet.NO_DB:
        print("No se ha encontrado ninguna base de datos")


def show_login():

    print("Introduzca el nombre de usuario: ")
    nickname = input("> ").strip()
    print("Introduzca la contraseña: ")
    password = input("> ").strip()

    ret = Sistema._instance.login(nickname, password)

    if ret == TypeRet.OK:
        show_container()
    elif ret == TypeRet.NO_DB:
        print("No se ha encontrado ninguna base de datos")


def show_container():

    option = 0
    while(option != 'q'):

        print(f"\n<<\tLobby\t    >>")
        print("Introduzca la opción que desee:\n\t1. Listar contenedores\n\t2. Añadir contenedor\n\t3. Borrar contenedor\n\t4. Seleccionar Contenedor\n\tq. para salir\n-----------------------------------\n\n")
        option = input("> ").strip()
        
        try:
            if int(option) == 1:
                list_containers()
            elif int(option) == 2:
                add_container()
            elif int(option) == 3:
                delete_container()
            elif int(option) == 4:
                show_content()
            else:
                print("Opción no soportada")
        except Exception as e:
            if option != 'q':
                print_err(e)


def list_containers():
    print("\n")
    for cont in Sistema._instance.usuario.contenedores.keys():
        print(cont)


def add_container():

    print("Introduzca el nombre del contenedor: ")
    name = input("> ").strip()
    print("Introduzca la contraseña: ")
    password = input("> ").strip()

    Sistema._instance.usuario.add_container(name, password)


def delete_container():

    print("Introduzca el nombre del contenedor: ")
    name = input("> ").strip()
    print("Introduzca la contraseña: ")
    password = input("> ").strip()

    Sistema._instance.usuario.delete_container(name, password)


def show_content():

    print("Introduzca el nombre del contenedor: ")
    cont_name = input("> ").strip()
    print("Introduzca la contraseña: ")
    cont_password = input("> ").strip()

    contenedor = Sistema._instance.usuario.contenedores.get(cont_name)
    if contenedor is None:
        print("El contenedor solicitado no existe")
        return
    elif not contenedor.check_password(cont_password):
        print("Contraseña errónea")
        return
    
    option = 0
    while(option != 'q'):
        print(f"\n<<\tContenedor {cont_name}\t>>")
        print("Introduzca la opción que desee:\n\t1. Ver contenido\n\t2. Modificar contenido\n\tq. para salir\n-----------------------------------\n\n")
        option = input("> ").strip()
        
        try:
            if int(option) == 1:
                print(f"{contenedor.descif_data(cont_password).decode('utf-8')}")
            elif int(option) == 2:
                modified_content = curses.wrapper(edit_content, contenedor.descif_data(cont_password).decode('utf-8'))
                contenedor.touch_data(cont_password, modified_content)
            else:
                print("Opción no soportada")
        except Exception as e:
            if option != 'q':
                print_err(e)      


def edit_content(stdscr, text):

    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

    # Se debe usar una lista para controlar los caracteres de forma dinámica
    default_content = list(text)
    cursor = len(default_content)

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "".join(default_content))
        stdscr.move(0, cursor)
        stdscr.refresh()
        pressed_char = stdscr.getch()

        if pressed_char == curses.KEY_LEFT:
            cursor = max(0, cursor - 1)
        elif pressed_char == curses.KEY_RIGHT:
            cursor = min(len(default_content), cursor + 1)
        elif pressed_char == 27: #ESC
            break
        elif pressed_char in (10, 13): #\n y \r
            break
        elif pressed_char == curses.KEY_BACKSPACE:
            if cursor > 0:
                cursor -= 1
                default_content.pop(cursor)
        elif pressed_char == curses.KEY_DC:
            if cursor < len(default_content):
                default_content.pop(cursor)
        elif 32 <= pressed_char <= 126:
            default_content.insert(cursor, chr(pressed_char))
            cursor += 1
    
    return "".join(default_content)