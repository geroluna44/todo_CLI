#!/usr/bin/env python3
# =============================================================================
# LÍNEAS 1-3: IMPORTACIONES
# =============================================================================
# Las importaciones traen código ya escrito por otros para reutilizarlo.
# Se escriben siempre al inicio del archivo.

import curses
# curses: biblioteca estándar de Python para hacer interfaces de terminal
# interactivas (TUI). Permite mover el cursor, detectar teclas sin Enter,
# cambiar colores, etc. Es como tener un "lienzo" en la terminal.

import os
# os: biblioteca para interactuar con el sistema operativo: rutas de archivos,
# variables de entorno, comandos del sistema, etc.


# =============================================================================
# LÍNEAS 5-10: VARIABLES GLOBALES Y CONSTANTES
# =============================================================================
# Las variables que están fuera de cualquier función se llaman "globales".
# Las que están en MAYÚSCULAS son "constantes" (por convención, no deberían
# cambiar aunque Python no las protege realmente).

TODO_FILE = os.path.expanduser("~/life/to-do.txt")
# os.path.expanduser("~") reemplaza "~" por la ruta de tu carpeta personal.
# Para el usuario "gero", "~/life/to-do.txt" se convierte en:
# "/home/gero/life/to-do.txt"
# Esta es la ruta PRINCIPAL donde se guardan las tareas.

FALLBACK_FILE = os.path.join(os.path.dirname(__file__), "to-do.txt")
# Si el archivo principal no existe, se usa este de respaldo.
# os.path.dirname(__file__) obtiene la carpeta donde está este script.
# os.path.join() une partes de una ruta de forma correcta según el SO.
# Así que busca "to-do.txt" en la misma carpeta que todo.py.

_filepath = None
# Variable global que almacenará la ruta del archivo que SÍ existe.
# Se inicializa como None (nulo) y se asigna dentro de load_tasks().
# El guión bajo _ al inicio es una convención que indica "uso interno".

_history = []
# Lista que guarda los estados anteriores de la lista de tareas.
# Sirve para la función "deshacer" (undo).
# Cada elemento es una copia de la lista de tareas en un momento dado.

_MAX_HISTORY = 50
# Número máximo de estados que podemos deshacer.
# Una vez alcanzado, se descartan los más antiguos.

VERSION = "v0.2"
# Versión del programa. Se muestra en la barra de estado.


# =============================================================================
# LÍNEAS 12-21: CONFIGURACIÓN DEL MENÚ
# =============================================================================
# MENU_OPTIONS es una LISTA DE TUPLAS.
# Una tupla es como una lista pero que no se puede modificar (inmutable).
# Cada tupla tiene: (texto_visible, código_de_tecla)

MENU_OPTIONS = [
    ("Añadir tarea", ord("a")),
    ("Añadir subtarea", ord("s")),
    ("Modificar tarea", ord("c")),
    ("Eliminar linea", ord("k")),
    ("Eliminar bloque", 11),         # ← 11 es el código de Ctrl+K
    ("Deshacer", ord("u")),
    ("Mover", ord("m")),
    ("Salir del programa", ord("q")),
]
# ord("a") → 97. ord() convierte un carácter a su número ASCII.
# El menú se usa para que el usuario pueda elegir acciones sin recordar
# las teclas. Es una interfaz más amigable.
# El 11 en "Eliminar bloque" es el código que envía Ctrl+K en la terminal.
# K es la 11ª letra del alfabeto, por eso Ctrl+K = 11.


# =============================================================================
# LÍNEAS 23-33: EL LOGO (BANNER)
# =============================================================================
# BANNER es una lista de strings. Cada string es una línea del logo.
# Se muestra al iniciar el programa.

BANNER = [
    '░░░░░░░░░░░░░░░░░░░░░░░░░░░░',
    '░░╔════╦═══╗░░░░╔═══╦═══╗░░░',
    '░░║╔╗╔╗║╔═╗║░░░░╚╗╔╗║╔═╗║░░░',
    '░░╚╝║║╚╣║░║║░░░░░║║║║║░║║░░░',
    '░░░░║║░║║░║║╔══╗░║║║║║░║║░░░',
    '░░░░║║░║╚═╝║╚══╝╔╝╚╝║╚═╝║░░░',
    '░░░░╚╝░╚═══╝░░░░╚═══╩═══╝░░░',
    '░░░░░░░░░░░░░░░░░░░░░░░░░░░░',
    'by geroluna_44          v0.2',
]
# Los caracteres unicode (╔, ╗, ░, etc.) forman un dibujo.
# Python 3 maneja Unicode de forma nativa, no hay que hacer nada especial.


# =============================================================================
# FUNCIÓN: load_tasks (líneas 36-45)
# =============================================================================
# PROPÓSITO: Cargar las tareas desde el archivo de texto a una lista.
# PARÁMETROS: path (ruta del archivo a cargar)
# DEVUELVE: Una lista de strings, cada string es una línea del archivo.

def load_tasks(path):
    # 'global' le dice a Python: "usa la variable _filepath de fuera,
    # no crees una nueva local". Sin esto, _filepath sería una variable
    # diferente dentro de esta función.
    global _filepath

    # os.path.exists() devuelve True si la ruta existe (archivo o carpeta).
    if os.path.exists(path):
        _filepath = path            # Usamos la ruta principal
    elif os.path.exists(FALLBACK_FILE):
        _filepath = FALLBACK_FILE   # Usamos la de respaldo
    else:
        return []                   # No hay archivo → lista vacía

    # with open(...) as f: abre el archivo y lo cierra automáticamente
    # al salir del bloque. El modo "r" es solo lectura.
    with open(_filepath, "r") as f:
        # COMPRENSIÓN DE LISTAS (list comprehension):
        # [line.rstrip("\n") for line in f]
        # Es una forma compacta de crear listas. Equivale a:
        #
        #   resultado = []
        #   for line in f:
        #       resultado.append(line.rstrip("\n"))
        #
        # rstrip("\n") quita el salto de línea (\n) del final de cada línea.
        return [line.rstrip("\n") for line in f]


# =============================================================================
# FUNCIÓN: save_tasks (líneas 48-51)
# =============================================================================
# PROPÓSITO: Guardar la lista de tareas al archivo.
# PARÁMETROS: tasks (lista de strings)
# NO DEVUELVE NADA (None implícito)

def save_tasks(tasks):
    # Modo "w" (write): sobreescribe el archivo completamente.
    # Si el archivo no existe, lo crea.
    with open(_filepath, "w") as f:
        for task in tasks:
            # Escribe cada tarea en una línea, agregando \n al final.
            f.write(task + "\n")
    # Al salir del 'with', el archivo se cierra automáticamente.


# =============================================================================
# FUNCIÓN: push_history (líneas 54-58)
# =============================================================================
# PROPÓSITO: Guardar una copia del estado actual antes de modificarlo.
# Sirve para que la función "deshacer" pueda restaurar estados anteriores.
# PARÁMETROS: tasks (lista de strings)

def push_history(tasks):
    global _history

    # [t for t in tasks] crea una COPIA de la lista.
    # ¿Por qué no hacer simplemente _history.append(tasks)?
    # Porque si luego modificamos tasks, también se modificaría la copia
    # en el historial (porque ambos apuntarían al mismo objeto).
    # Haciendo [t for t in tasks] creamos una NUEVA lista con los mismos
    # elementos.
    _history.append([t for t in tasks])

    # Si el historial supera el límite, elimina el más antiguo (pop(0)).
    if len(_history) > _MAX_HISTORY:
        _history.pop(0)


# =============================================================================
# FUNCIÓN: undo_task (líneas 61-65)
# =============================================================================
# PROPÓSITO: Restaurar el estado anterior de las tareas.
# PARÁMETROS: tasks (lista actual, aunque no se usa directamente)
# DEVUELVE: La lista del estado anterior, o la misma si no hay historial.

def undo_task(tasks):
    global _history

    # if _history: es equivalente a if len(_history) > 0:
    # En Python, una lista vacía se evalúa como False.
    if _history:
        # pop() sin índice elimina y devuelve el ÚLTIMO elemento.
        # Es como desapilar: el último guardado es el primero en restaurarse
        # (comportamiento LIFO: Last In, First Out).
        return _history.pop()

    return tasks  # Si no hay historial, devolvemos las tareas sin cambios.


# =============================================================================
# FUNCIÓN: toggle_task (líneas 68-79)
# =============================================================================
# PROPÓSITO: Cambiar el estado de una tarea entre pendiente [ ] y hecha [X].
# PARÁMETROS: tasks (lista), idx (índice de la tarea a cambiar)
# DEVUELVE: La lista de tareas modificada.

def toggle_task(tasks, idx):
    push_history(tasks)       # 1. Guardamos el estado actual (por si deshacer)
    line = tasks[idx]          # 2. Obtenemos la línea en esa posición

    if "[ ]" in line:
        # replace("[ ]", "[X]", 1): reemplaza la PRIMERA ocurrencia de "[ ]"
        # por "[X]". El 1 limita a un solo reemplazo.
        line = line.replace("[ ]", "[X]", 1)
    elif "[X]" in line:
        line = line.replace("[X]", "[ ]", 1)
    else:
        return tasks  # Si no tiene [ ] ni [X], no hacemos nada

    tasks[idx] = line          # 3. Actualizamos la línea en la lista
    save_tasks(tasks)          # 4. Guardamos al archivo
    return tasks


# =============================================================================
# FUNCIÓN: move_task (líneas 82-89)
# =============================================================================
# PROPÓSITO: Intercambiar una tarea con la de arriba o abajo.
# PARÁMETROS: tasks, idx, direction (1 = abajo, -1 = arriba)
# DEVUELVE: (tasks_modificada, nuevo_índice)

def move_task(tasks, idx, direction):
    push_history(tasks)
    target = idx + direction   # La posición con la que vamos a intercambiar

    # Validación de límites: no podemos mover si estamos en el borde.
    if target < 0 or target >= len(tasks):
        return tasks, idx  # Devolvemos todo igual

    # INTERCAMBIO EN PYTHON (swap):
    # tasks[idx], tasks[target] = tasks[target], tasks[idx]
    # Esto intercambia los valores sin necesidad de variable temporal.
    # En otros lenguajes harías:
    #   temp = tasks[idx]
    #   tasks[idx] = tasks[target]
    #   tasks[target] = temp
    tasks[idx], tasks[target] = tasks[target], tasks[idx]

    save_tasks(tasks)
    return tasks, target  # Devolvemos el nuevo índice donde quedó el cursor


# =============================================================================
# FUNCIÓN: get_block (líneas 92-99)
# =============================================================================
# PROPÓSITO: Encontrar el bloque al que pertenece una tarea.
# Un "bloque" es una tarea principal + todas sus subtareas (---).
# PARÁMETROS: tasks, idx
# DEVUELVE: (inicio_del_bloque, fin_del_bloque)

def get_block(tasks, idx):
    # EMPEZAMOS DESDE idx Y RETROCEDEMOS:
    # Mientras la línea de ARRIBA empiece con "---", seguimos subiendo.
    # Así encontramos la tarea PADRE (la que NO empieza con ---).
    start = idx
    while start > 0 and tasks[start].startswith("---"):
        start -= 1

    # AHORA AVANZAMOS DESDE start HACIA ADELANTE:
    # Mientras la siguiente línea empiece con "---", es subtarea del bloque.
    end = start
    while end + 1 < len(tasks) and tasks[end + 1].startswith("---"):
        end += 1

    return start, end

# EJEMPLO:
#   [ ] [Trabajo] Hacer informe       ← start (índice 0)
#   --- [ ] Recopilar datos            ←
#   --- [ ] Escribir                   ← end (índice 2)
#   [ ] [Casa] Limpiar                 ← otro bloque
#
# Si idx = 1 (la primera subtarea):
#   - Retrocede: tasks[1] empieza con ---, tasks[0] no → start = 0
#   - Avanza: tasks[1] empieza con ---, tasks[2] también, tasks[3] no → end = 2
#   - Devuelve (0, 2)


# =============================================================================
# FUNCIÓN: move_block (líneas 102-123)
# =============================================================================
# PROPÓSITO: Mover un bloque entero (tarea + subtareas) arriba o abajo.
# PARÁMETROS: tasks, idx, direction
# DEVUELVE: (nueva_lista, nuevo_índice)

def move_block(tasks, idx, direction):
    push_history(tasks)

    # 1. Obtenemos los límites del bloque actual
    start, end = get_block(tasks, idx)
    offset = idx - start  # Posición relativa del cursor dentro del bloque

    if direction == -1:         # ← Mover hacia ARRIBA
        if start == 0:
            return tasks, idx   # Ya está arriba del todo, no se puede

        # Buscamos el bloque que está ENCIMA de nosotros
        above_start, above_end = get_block(tasks, start - 1)

        # SLICING (rebanado de listas):
        # tasks[start:end+1] → obtiene los elementos desde start hasta end
        # El slicing funciona así: lista[inicio:fin] donde 'fin' NO se incluye.
        # Por eso usamos end+1.
        block = tasks[start:end + 1]          # Nuestro bloque
        above = tasks[above_start:start]      # El bloque de arriba

        # CONSTRUIMOS UNA NUEVA LISTA concatenando partes con +
        # Orden: (lo de antes del bloque de arriba) + (nuestro bloque) +
        #        (el bloque de arriba) + (lo que sigue después de nosotros)
        new_tasks = tasks[:above_start] + block + above + tasks[end + 1:]
        new_idx = above_start + offset  # El cursor se mueve con el bloque

    elif direction == 1:         # → Mover hacia ABAJO
        if end == len(tasks) - 1:
            return tasks, idx   # Ya está abajo del todo

        below_start, below_end = get_block(tasks, end + 1)
        block = tasks[start:end + 1]
        below = tasks[end + 1:below_end + 1]

        new_tasks = tasks[:start] + below + block + tasks[below_end + 1:]
        new_idx = start + len(below) + offset

    save_tasks(new_tasks)
    return new_tasks, new_idx

# NOTA: Esta función NO modifica la lista original, CREA una nueva lista.
# Por eso asignamos el resultado: tasks, current = move_block(...)


# =============================================================================
# FUNCIÓN: indent_task (líneas 126-139)
# =============================================================================
# PROPÓSITO: Convertir una tarea en subtarea (agregar "--- ") o viceversa.
# PARÁMETROS: tasks, idx, direction (1 = indentar, -1 = desindentar)

def indent_task(tasks, idx, direction):
    push_history(tasks)
    line = tasks[idx]

    if direction == 1:   # → (flecha derecha): convertir en subtarea
        if not line.startswith("--- "):
            # Concatenamos "--- " al inicio de la línea
            line = "--- " + line

    elif direction == -1:  # ← (flecha izquierda): convertir en tarea normal
        if line.startswith("--- "):
            # Slicing: line[4:] significa "desde el carácter 4 hasta el final"
            # O sea, quitamos los primeros 4 caracteres ("--- ")
            line = line[4:]
        elif line.startswith("---"):
            # Caso borde: si empieza con "---" pero sin espacio
            line = line[3:]

    tasks[idx] = line
    save_tasks(tasks)
    return tasks

# NOTA: Los strings en Python son INMUTABLES. No puedes cambiar un carácter.
# Por eso hacemos line = "--- " + line, que crea un NUEVO string y lo asigna.


# =============================================================================
# FUNCIÓN: show_splash (líneas 142-161)
# =============================================================================
# PROPÓSITO: Mostrar la pantalla de presentación (banner + mensaje).
# PARÁMETROS: stdscr (el objeto "pantalla" de curses)
# NO DEVUELVE NADA

def show_splash(stdscr):
    curses.curs_set(0)  # Oculta el cursor parpadeante

    # getmaxyx() devuelve (alto, ancho) de la terminal en ese momento.
    # YX = Y (filas) + X (columnas). Es nomenclatura clásica de curses.
    height, width = stdscr.getmaxyx()

    stdscr.clear()  # Limpia la pantalla

    # max(len(l) for l in BANNER) calcula el ancho de la línea más larga
    # del banner. Esto es otro ejemplo de comprensión aplicada a un cálculo.
    max_w = max(len(l) for l in BANNER)

    # Cálculo para CENTRAR el banner en la pantalla:
    # (ancho_terminal - ancho_banner) // 2
    # max(0, ...) evita valores negativos si la terminal es muy pequeña.
    x = max(0, (width - max_w) // 2)
    y = max(0, (height - len(BANNER)) // 2)

    # enumerate() devuelve (índice, valor) de cada elemento de la lista.
    for i, line in enumerate(BANNER):
        # Solo dibujamos si cabe en la pantalla
        if x + len(line) < width:
            # addstr(fila, columna, texto) escribe en la posición indicada
            stdscr.addstr(y + i, x, line)

    msg = "Presiona cualquier tecla para continuar"
    mx = max(0, (width - len(msg)) // 2)
    my = min(y + len(BANNER) + 2, height - 1)
    stdscr.addstr(my, mx, msg)

    stdscr.refresh()  # Refresca la pantalla (hace visible lo dibujado)
    stdscr.getch()    # Espera a que el usuario presione UNA tecla


# =============================================================================
# FUNCIÓN: get_input (líneas 164-192)
# =============================================================================
# PROPÓSITO: Pedir texto al usuario, carácter por carácter, con soporte
#            de backspace y caracteres acentuados/UTF-8.
# PARÁMETROS: stdscr, y, x (posición), prompt (texto guía)
# DEVUELVE: El string ingresado por el usuario

def get_input(stdscr, y, x, prompt):
    curses.curs_set(1)  # Mostrar el cursor (indica que se puede escribir)

    stdscr.addstr(y, x, prompt)  # Mostrar el texto guía (ej: "Nombre: ")
    stdscr.refresh()

    buf = ""  # Buffer: aquí acumulamos el texto que escribe el usuario

    while True:
        # get_wch() lee UNA tecla. Es mejor que getch() porque soporta
        # caracteres UTF-8 (acentos, ñ, etc). getch() trunca a 0-255.
        key = stdscr.get_wch()

        # isinstance() pregunta: ¿esto es de tipo str?
        # get_wch() devuelve str para teclas normales o int para especiales.
        if isinstance(key, str):
            # ENTER: puede ser "\n" (LF) o "\r" (CR) según el terminal
            if key in ("\n", "\r"):
                break  # Salimos del bucle, terminamos de escribir

            # BACKSPACE: "\x7f" (DEL) o "\b" (BS) según el terminal
            elif key in ("\x7f", "\b"):
                if buf:                         # Si hay algo que borrar
                    buf = buf[:-1]              # Quitamos el último carácter
                    # Redibujamos el texto con un espacio extra al final
                    # para "pintar encima" del carácter borrado
                    stdscr.addstr(y, x + len(prompt), buf + " ")
                    stdscr.move(y, x + len(prompt) + len(buf))

            # Tecla NORMAL (letra, número, espacio, etc.)
            # " " >= " " es True, pero "\n" >= " " es False.
            elif key >= " ":
                buf += key  # Agregamos al buffer
                stdscr.addstr(y, x + len(prompt) + len(buf) - 1, key)

        elif isinstance(key, int):
            # Teclas ESPECIALES (flechas, F1, etc.) representadas como int
            if key == curses.KEY_ENTER:
                break
            elif key == curses.KEY_BACKSPACE:
                if buf:
                    buf = buf[:-1]
                    stdscr.addstr(y, x + len(prompt), buf + " ")
                    stdscr.move(y, x + len(prompt) + len(buf))

        stdscr.refresh()

    curses.curs_set(0)  # Volver a ocultar el cursor
    return buf  # Devolvemos lo que escribió el usuario


# =============================================================================
# FUNCIÓN: add_task (líneas 195-222)
# =============================================================================
# PROPÓSITO: Añadir una nueva tarea. Pide nombre, categoría y prioridad.
# PARÁMETROS: stdscr, tasks
# DEVUELVE: La lista de tareas actualizada

def add_task(stdscr, tasks):
    push_history(tasks)  # Guardamos estado por si quieren deshacer

    h, w = stdscr.getmaxyx()
    stdscr.clear()
    y = h // 2 - 2  # Posición vertical (centrado aproximado)

    # get_input() pausa el programa hasta que el usuario escriba algo y
    # presione Enter. Devuelve el texto ingresado.
    name = get_input(stdscr, y, 2, "Nombre de la tarea: ")
    cat = get_input(stdscr, y + 1, 2, "Ingrese la categoria: ")

    # Bucle de validación: la prioridad SOLO puede ser A, B o C.
    # Mientras no sea válida, sigue pidiendo.
    while True:
        prio = get_input(stdscr, y + 2, 2, "Ingrese la prioridad (A/B/C): ").upper()
        if prio in ("A", "B", "C"):
            break  # Prioridad válida, salimos del bucle

        # Mensaje de error temporal
        stdscr.addstr(y + 3, 2, "Prioridad invalida. Use A, B o C.")
        stdscr.refresh()
        curses.napms(1000)  # Pausa de 1000 milisegundos (1 segundo)

        # Limpiamos la línea de la prioridad para que el usuario reintente
        stdscr.move(y + 2, 2 + len("Ingrese la prioridad (A/B/C): "))
        stdscr.clrtoeol()  # Borra desde el cursor hasta el final de línea
        stdscr.refresh()

    # F-STRING: f"[ ] [{cat}] {name} | {prio}"
    # Las f-strings (Python 3.6+) permiten incrustar variables en strings
    # poniendo {nombre_variable} dentro del texto.
    linea = f"[ ] [{cat}] {name} | {prio}"
    tasks.append(linea)  # append() agrega al FINAL de la lista

    save_tasks(tasks)

    # Mostramos confirmación por 800ms
    stdscr.clear()
    stdscr.addstr(h // 2, 2, "Tarea agregada correctamente!")
    stdscr.refresh()
    curses.napms(800)

    return tasks

# EJEMPLO de f-string:
#   cat = "Trabajo", name = "Hacer informe", prio = "A"
#   resultado: "[ ] [Trabajo] Hacer informe | A"


# =============================================================================
# FUNCIÓN: add_subtask (líneas 225-242)
# =============================================================================
# PROPÓSITO: Añadir una subtarea al bloque actual (se inserta al final).
# PARÁMETROS: stdscr, tasks, idx (posición actual del cursor)
# DEVUELVE: (tasks, nuevo_índice)

def add_subtask(stdscr, tasks, idx):
    push_history(tasks)

    # Llamamos a get_block pero IGNORAMOS el inicio con _
    # _ es una convención para "no me interesa este valor"
    _, block_end = get_block(tasks, idx)

    h, w = stdscr.getmaxyx()
    stdscr.clear()
    y = h // 2 - 1

    name = get_input(stdscr, y, 2, "Nombre de la subtarea: ")

    # Las subtareas SIEMPRE empiezan con "--- " y NO tienen categoría
    # ni prioridad (solo las tareas padre tienen esos campos).
    linea = f"--- [ ] {name}"

    # insert(posición, elemento) inserta en una posición específica,
    # a diferencia de append() que agrega al final.
    tasks.insert(block_end + 1, linea)

    save_tasks(tasks)

    stdscr.clear()
    stdscr.addstr(h // 2, 2, "Subtarea agregada correctamente!")
    stdscr.refresh()
    curses.napms(800)

    # Devolvemos el índice donde se insertó para que el cursor se mueva allí
    return tasks, block_end + 1


# =============================================================================
# FUNCIÓN: delete_line (líneas 245-249)
# =============================================================================
# PROPÓSITO: Eliminar la línea actual.
# PARÁMETROS: tasks, idx

def delete_line(tasks, idx):
    push_history(tasks)

    # del elimina un elemento de una lista por su ÍNDICE.
    # Es una palabra clave de Python, no una función.
    # Si la lista era [a, b, c] y hacemos del lista[1], queda [a, c].
    del tasks[idx]

    save_tasks(tasks)

    # min(idx, len(tasks) - 1) ajusta el cursor:
    # si borramos el último elemento, el cursor sube al anterior.
    return tasks, min(idx, len(tasks) - 1)


# =============================================================================
# FUNCIÓN: delete_block (líneas 252-257)
# =============================================================================
# PROPÓSITO: Eliminar un bloque entero (tarea + todas sus subtareas).

def delete_block(tasks, idx):
    push_history(tasks)

    start, end = get_block(tasks, idx)

    # del también puede eliminar un RANGO completo con slicing:
    # del tasks[start:end+1] elimina todos los elementos desde start
    # hasta end (incluyendo end, porque end+1 es exclusivo).
    # Si la lista era [a, b, c, d] y hacemos del lista[1:3], queda [a, d].
    del tasks[start:end + 1]

    save_tasks(tasks)
    return tasks, min(start, len(tasks) - 1)


# =============================================================================
# FUNCIÓN: parse_line (líneas 260-281)
# =============================================================================
# PROPÓSITO: Descomponer una línea de texto en sus partes (parsing).
# PARÁMETROS: line (un string como "[ ] [Trabajo] Hacer | A")
# DEVUELVE: (status, categoria, nombre, prioridad, es_subtarea)

def parse_line(line):
    # Detectar si es subtarea (empieza con "--- ")
    is_sub = line.startswith("--- ")

    # Si es subtarea, nos saltamos los 4 caracteres "--- "
    # Slicing: line[4:] → desde el índice 4 hasta el final
    rest = line[4:] if is_sub else line

    # Los primeros 4 caracteres son el estado: "[ ] " o "[X] "
    # Nota: incluye el espacio después del corchete
    status = rest[:4]
    rest = rest[4:]  # Avanzamos: quitamos el estado

    cat = ""    # Categoría (vacía por defecto)
    prio = ""   # Prioridad (vacía por defecto)

    if is_sub:
        # Las subtareas no tienen categoría ni prioridad.
        # Todo lo que queda después del prefijo y estado es el nombre.
        name = rest
    else:
        # Si el siguiente carácter es "[", hay categoría
        if rest.startswith("["):
            # find("]") encuentra la posición del primer "]"
            end_bracket = rest.find("]")
            if end_bracket != -1:
                # rest[1:end_bracket] → extrae lo que está DENTRO de [ ]
                cat = rest[1:end_bracket]
                # Saltamos la categoría + el espacio después de "] "
                # end_bracket + 2 porque: "]" está en end_bracket,
                # y queremos saltar "]" y el espacio " "
                rest = rest[end_bracket + 2:]

        # rfind(" | ") busca " | " desde la DERECHA hacia la izquierda.
        # Buscamos desde la derecha porque el nombre podría contener " | ".
        pipe = rest.rfind(" | ")
        if pipe != -1:
            name = rest[:pipe]       # Todo antes de " | " es el nombre
            prio = rest[pipe + 3:]   # Todo después de " | " es la prioridad
        else:
            name = rest  # No hay prioridad

    return status, cat, name, prio, is_sub
    # Devolvemos una TUPLA de 5 elementos. Python permite devolver
    # múltiples valores separados por coma, que es una tupla implícita.


# =============================================================================
# FUNCIÓN: build_line (líneas 284-293)
# =============================================================================
# PROPÓSITO: La operación inversa de parse_line: reconstruir la línea
#            desde sus componentes.
# PARÁMETROS: status, cat, name, prio, is_sub
# DEVUELVE: El string completo de la línea

def build_line(status, cat, name, prio, is_sub):
    if is_sub:
        # Subtarea: solo tiene prefijo ---, estado y nombre
        return f"--- {status}{name}"

    # Tarea padre: puede tener categoría y prioridad opcionales
    if cat and prio:
        return f"{status}[{cat}] {name} | {prio}"
    if cat:
        return f"{status}[{cat}] {name}"
    if prio:
        return f"{status}{name} | {prio}"

    # Caso mínimo: solo estado y nombre (sin categoría ni prioridad)
    return f"{status}{name}"

# Las condiciones if cat and prio usan "truthiness":
# Un string vacío "" se evalúa como False en Python.
# Un string no vacío se evalúa como True.
# Así que if cat and prio es True solo si AMBAS tienen contenido.


# =============================================================================
# FUNCIÓN: edit_task_menu (líneas 297-388)
# =============================================================================
# PROPÓSITO: Menú interactivo para modificar una tarea. Permite cambiar
#            nombre, categoría y/o prioridad.
# PARÁMETROS: stdscr, tasks, idx

def edit_task_menu(stdscr, tasks, idx):
    push_history(tasks)

    # Descomponemos la línea en sus partes
    status, cat, name, prio, is_sub = parse_line(tasks[idx])

    # Si es subtarea, SOLO se puede editar el nombre
    # (las subtareas no tienen categoría ni prioridad)
    if is_sub:
        options = ["Nombre"]
        values = {"Nombre": name}
        # lambda es una función ANÓNIMA (sin nombre) de una sola línea.
        # Esta recibe 'new' y devuelve build_line con el nuevo nombre.
        rebuild = lambda new: build_line(status, cat, new, prio, is_sub)
    else:
        options = ["Nombre", "Categoria", "Prioridad"]
        values = {"Nombre": name, "Categoria": cat, "Prioridad": prio}
        # Función normal (no lambda) porque tiene más de un parámetro
        def rebuild(new_cat, new_name, new_prio):
            return build_line(status, new_cat, new_name, new_prio, is_sub)

    h, w = stdscr.getmaxyx()
    sel = 0  # Opción seleccionada actualmente (0 = primera)

    while True:
        stdscr.clear()

        # Dibujamos el título del menú centrado
        title = " Modificar "
        tw = len(title)
        max_opt_w = max(len(o) for o in options)  # Ancho de la opción más larga
        box_w = max(tw, max_opt_w + 4) + 4
        bx = max(0, (w - box_w) // 2)
        by = max(0, (h - len(options) - 4) // 2)

        # attron() activa un ATRIBUTO de curses (negritas, color, etc.)
        # A_REVERSE invierte colores (fondo blanco, texto negro)
        stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(by, bx + (box_w - tw) // 2, title)
        stdscr.attroff(curses.A_REVERSE)  # Desactivamos el atributo

        # Dibujamos las opciones, resaltando la seleccionada
        for i, opt in enumerate(options):
            y = by + 2 + i
            if i == sel:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, bx + 2, f"  {opt}  ")
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, bx + 2, f"  {opt}  ")

        foot = "Enter: seleccionar  ESC/q: cancelar"
        # Recortamos por si es más largo que la terminal
        stdscr.addstr(h - 1, 0, foot[:w - 1])
        stdscr.refresh()

        # Capturamos tecla (usamos getch() aquí, no get_wch(), porque
        # solo necesitamos flechas y Enter)
        key = stdscr.getch()

        # Navegación con flechas
        if key == curses.KEY_UP and sel > 0:
            sel -= 1
        elif key == curses.KEY_DOWN and sel < len(options) - 1:
            sel += 1

        # Enter: seleccionar la opción actual
        elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
            field = options[sel]
            stdscr.clear()

            # Definimos prompt según el campo seleccionado
            if field == "Nombre":
                current_val = name
                prompt = "Nuevo nombre: "
            elif field == "Categoria":
                current_val = cat
                prompt = "Nueva categoria: "
            elif field == "Prioridad":
                current_val = prio
                prompt = "Nueva prioridad (A/B/C): "

            new_val = get_input(stdscr, h // 2, 2, prompt)

            # Validación especial para prioridad
            if field == "Prioridad":
                new_val = new_val.upper()
                while new_val not in ("A", "B", "C", ""):
                    stdscr.addstr(h // 2 + 1, 2, "Solo A, B o C. Intentelo de nuevo:")
                    stdscr.refresh()
                    curses.napms(1000)
                    stdscr.move(h // 2, 2 + len(prompt))
                    stdscr.clrtoeol()
                    stdscr.refresh()
                    new_val = get_input(stdscr, h // 2, 2, prompt).upper()

            # Si el usuario escribió algo (no dejó vacío)
            if new_val:
                if field == "Nombre":
                    name = new_val
                elif field == "Categoria":
                    cat = new_val
                elif field == "Prioridad":
                    prio = new_val

                # Reconstruimos la línea completa
                if is_sub:
                    tasks[idx] = build_line(status, cat, name, prio, is_sub)
                else:
                    tasks[idx] = build_line(status, cat, name, prio, is_sub)
                save_tasks(tasks)

            break  # Salimos del menú

        # ESC (27) o q: cancelar sin guardar
        elif key in (ord("q"), 27):
            break

    return tasks


# =============================================================================
# FUNCIÓN: _key_str (líneas 391-398)
# =============================================================================
# PROPÓSITO: Convertir un código de tecla numérico a un string legible.
#            Ej: 11 → "^K", 27 → "ESC", 97 → "A"
# PARÁMETROS: k (código numérico de la tecla)

def _key_str(k):
    if k == 11:
        return "^K"    # Ctrl+K
    if k == 27:
        return "ESC"   # Escape

    # Códigos de control del 1 al 31: se muestran como ^letra
    # chr(65) = "A", chr(66) = "B", etc.
    # Para k=1: chr(1+64) = chr(65) = "A" → "^A"
    if 0 < k < 32:
        return f"^{chr(k + 64)}"

    # Para el resto: chr(k) convierte el número a su carácter.
    # .upper() lo pasa a mayúscula.
    return chr(k).upper()


# =============================================================================
# FUNCIÓN: draw_small_term_warning (líneas 401-412)
# =============================================================================
# PROPÓSITO: Mostrar un cartel cuando la terminal es demasiado pequeña.

def draw_small_term_warning(stdscr, w, h, min_w, min_h):
    msg1 = "Terminal demasiado pequena"
    msg2 = f"Minimo: {min_w} ancho x {min_h} alto"

    msg_w = max(len(msg1), len(msg2)) + 4

    # Si el mensaje es más ancho que la terminal, no podemos dibujarlo
    if msg_w > w or 4 > h:
        return

    bx = max(0, (w - msg_w) // 2)
    by = max(0, (h - 4) // 2)

    # Dibujamos un cartel con bordes de + y -
    # La multiplicación de strings: "-" * 5 = "-----"
    stdscr.addstr(by, bx,     "+" + "-" * (msg_w - 2) + "+")
    stdscr.addstr(by + 1, bx, "| " + msg1 + " " * (msg_w - 4 - len(msg1)) + " |")
    stdscr.addstr(by + 2, bx, "| " + msg2 + " " * (msg_w - 4 - len(msg2)) + " |")
    stdscr.addstr(by + 3, bx, "+" + "-" * (msg_w - 2) + "+")


# =============================================================================
# FUNCIÓN: draw_menu_overlay (líneas 415-464)
# =============================================================================
# PROPÓSITO: Dibujar el menú de acciones superpuesto sobre la lista de tareas.
#            Usa caracteres Unicode para bordes dobles (╔╗╚╝║═╠╣).

def draw_menu_overlay(stdscr, sel, options):
    h, w = stdscr.getmaxyx()

    # Calculamos el tamaño de la caja según las opciones
    max_label = max(len(o[0]) + len(_key_str(o[1])) + 8 for o in options)
    box_w = max_label + 12
    box_h = len(options) + 5

    # Si la terminal es muy pequeña, mostramos advertencia
    if box_w > w or box_h > h:
        draw_small_term_warning(stdscr, w, h, box_w, box_h)
        return

    # Posición para centrar la caja
    bx = max(0, (w - box_w) // 2)
    by = max(0, (h - box_h) // 2)

    # Dibujamos la caja carácter por carácter con dos bucles anidados
    # (i = filas, j = columnas)
    for i in range(box_h):
        for j in range(box_w):
            if i == 0:
                # Primera fila: esquinas superiores y borde horizontal
                # if-else en una línea (operador ternario):
                #   valor_si_true if condicion else valor_si_false
                ch = "\u2550" if 0 < j < box_w - 1 else ("\u2554" if j == 0 else "\u2557")
            elif i == box_h - 1:
                # Última fila: esquinas inferiores
                ch = "\u2550" if 0 < j < box_w - 1 else ("\u255a" if j == 0 else "\u255d")
            elif j == 0 or j == box_w - 1:
                # Bordes laterales
                ch = "\u2551"
            elif i == len(options) + 3:
                # Línea separadora (antes del pie)
                ch = "\u2560" if j == 0 else ("\u2563" if j == box_w - 1 else "\u2550")
            else:
                ch = " "

            # Solo dibujamos si está dentro de la pantalla
            if bx + j < w and by + i < h:
                # try/except: si addstr falla (ej: carácter no soportado),
                # simplemente lo ignoramos
                try:
                    stdscr.addstr(by + i, bx + j, ch)
                except:
                    pass

    # Título " Menu " centrado en la primera fila
    title = " Menu "
    tx = bx + (box_w - len(title)) // 2
    stdscr.addstr(by, tx, title)

    # Dibujamos las opciones del menú con sus teclas
    for i, (label, kc) in enumerate(options):
        y = by + 2 + i
        entry = f" {label} [{_key_str(kc)}]"
        x = bx + (box_w - len(entry)) // 2
        if i == sel:
            stdscr.attron(curses.A_REVERSE)
            stdscr.addstr(y, x, entry)
            stdscr.attroff(curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, entry)

    # Pie del menú
    foot = " Salir de este menu  [Tab]"
    fx = bx + (box_w - len(foot)) // 2
    stdscr.addstr(by + len(options) + 4, fx, foot)


# =============================================================================
# FUNCIÓN: draw (líneas 467-622)
# =============================================================================
# PROPÓSITO: Función PRINCIPAL del programa. Contiene el bucle infinito
#            que dibuja la interfaz y procesa las teclas.
# PARÁMETROS: stdscr (el objeto pantalla de curses)
# NOTA: Esta función recibe stdscr de curses.wrapper(), no se llama directo.

def draw(stdscr):
    # Pantalla de bienvenida (logo)
    show_splash(stdscr)

    # Cargar tareas desde el archivo
    tasks = load_tasks(TODO_FILE)

    if not tasks:
        # Si no hay archivo ni tareas, mostramos mensaje y salimos
        stdscr.addstr(0, 0, "No se encontró el archivo to-do.txt")
        stdscr.getch()
        return  # Termina el programa

    curses.curs_set(0)  # Ocultar cursor en la lista

    # ===== ESTADO DEL PROGRAMA =====
    # Estas variables controlan en qué "modo" está el programa.
    # Es una MÁQUINA DE ESTADOS simple.
    current = 0          # Índice de la tarea seleccionada (cursor)
    move_mode = False    # ¿Estamos en modo mover?
    block_mode = False   # ¿Estamos moviendo bloques (vs líneas individuales)?
    menu_active = False  # ¿Está abierto el menú de acciones?
    menu_sel = 0         # Opción seleccionada en el menú

    # BUCLE INFINITO: el programa se ejecuta hasta que el usuario presiona 'q'
    # while True se rompe con 'break' cuando se presiona 'q'.
    while True:
        # Obtenemos el tamaño actual de la terminal (puede cambiar si
        # el usuario redimensiona la ventana)
        height, width = stdscr.getmaxyx()
        stdscr.clear()

        # max_lines: cuántas líneas caben en pantalla (dejando 1 para
        # la barra de estado)
        max_lines = height - 2

        # SCROLL CENTRADO:
        # Queremos que la tarea seleccionada (current) esté centrada en
        # la pantalla. Para eso, calculamos 'start' como la línea desde
        # donde empezamos a dibujar.
        # current - max_lines // 2 hace que current quede al medio.
        # max(0, ...) evita índices negativos (principio de la lista).
        start = max(0, current - max_lines // 2)

        # Si estamos en modo mover bloques, calculamos los límites del bloque
        # actual. Si no, usamos (-1, -1) que no resaltará ningún bloque.
        if move_mode and block_mode:
            block_start, block_end = get_block(tasks, current)
        else:
            block_start, block_end = (-1, -1)

        # ===== DIBUJAR LAS TAREAS VISIBLES =====
        # tasks[start:start + max_lines] → solo las que caben en pantalla
        # enumerate(..., start=start) → los índices comienzan desde 'start'
        for i, task in enumerate(tasks[start:start + max_lines], start=start):
            y = i - start  # Posición Y en pantalla (0, 1, 2...)

            # ¿Está esta línea dentro del bloque seleccionado?
            in_block = block_start <= i <= block_end

            if i == current:
                # TAREA SELECCIONADA: se resalta con A_REVERSE
                # En modo mover, también se subraya (A_UNDERLINE)
                # El operador | COMBINA atributos (OR binario)
                attr = curses.A_REVERSE | (curses.A_UNDERLINE if move_mode else 0)
                stdscr.attron(attr)
                line = f"> {task}"  # Flecha indicadora
                if len(line) >= width:
                    line = line[:width - 1]  # Evita errores de curses
                stdscr.addstr(y, 0, line)
                stdscr.attroff(attr)

            elif in_block:
                # LÍNEA DEL BLOQUE SELECCIONADO (solo subrayada)
                stdscr.attron(curses.A_UNDERLINE)
                prefix = "  "
                line = f"{prefix}{task}"
                if len(line) >= width:
                    line = line[:width - 1]
                stdscr.addstr(y, 0, line)
                stdscr.attroff(curses.A_UNDERLINE)

            else:
                # TAREA NORMAL: sin resaltar
                prefix = "  "
                line = f"{prefix}{task}"
                if len(line) >= width:
                    line = line[:width - 1]
                stdscr.addstr(y, 0, line)

        # ===== BARRA DE ESTADO INFERIOR =====
        # Muestra información del modo actual a la izquierda
        # y el nombre/versión a la derecha.
        if move_mode:
            if block_mode:
                left = "MOVER BLOQUE"
            else:
                left = "MOVER LINEA  |  B: mover bloque"
        else:
            left = "Tab: Menu"

        right = f"ToDo by geroluna {VERSION}"

        # Calculamos espacios de relleno entre left y right
        padding = width - len(left) - len(right) - 2
        if padding < 1:
            padding = 1
        status = left + " " * padding + right
        if len(status) >= width:
            status = status[:width - 1]
        stdscr.addstr(height - 1, 0, status)

        # Verificamos si el menú cabría (si no, mostramos advertencia)
        menu_w = max(len(o[0]) + len(_key_str(o[1])) + 8 for o in MENU_OPTIONS) + 12
        menu_h = len(MENU_OPTIONS) + 5
        if menu_w > width or menu_h > height:
            draw_small_term_warning(stdscr, width, height, menu_w, menu_h)

        # Si el menú está activo, lo dibujamos superpuesto
        if menu_active:
            draw_menu_overlay(stdscr, menu_sel, MENU_OPTIONS)

        stdscr.refresh()  # Hacemos visible todo lo dibujado

        # ===== CAPTURA DE TECLA =====
        key = stdscr.getch()

        # CONVERSIÓN A MINÚSCULAS:
        # Si la tecla está entre 65 (A) y 90 (Z), sumamos 32 para
        # convertirla a su minúscula (97-122). Así el programa trata
        # mayúsculas y minúsculas igual.
        if 65 <= key <= 90:
            key = key + 32

        # ===== SI EL MENÚ ESTÁ ACTIVO =====
        if menu_active:
            if key == curses.KEY_UP:
                # Módulo (%) para que sea circular: si estamos en 0 y
                # presionamos arriba, vamos al último
                menu_sel = (menu_sel - 1) % len(MENU_OPTIONS)
                continue  # Salta al siguiente ciclo sin procesar más

            elif key == curses.KEY_DOWN:
                menu_sel = (menu_sel + 1) % len(MENU_OPTIONS)
                continue

            elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                # Enter: ejecuta la opción seleccionada.
                # Toma el código de tecla asociado a la opción del menú
                # y lo trata como si el usuario hubiera presionado esa tecla.
                key = MENU_OPTIONS[menu_sel][1]
                menu_active = False  # Cerramos el menú

            elif key in (ord("\t"), 27):  # Tab o ESC
                menu_active = False
                continue
            else:
                continue  # Ignoramos otras teclas mientras el menú está abierto

        # ===== ABRIR MENÚ CON TAB =====
        if key == ord("\t") and not move_mode:
            menu_active = True
            menu_sel = 0
            continue

        # ===== MODO MOVER =====
        if move_mode:
            if key == curses.KEY_UP and current > 0:
                # Asignamos la función según el modo (bloque o línea)
                # Esto es POLIMORFISMO: las funciones son objetos que
                # se pueden asignar a variables.
                fn = move_block if block_mode else move_task
                tasks, current = fn(tasks, current, -1)

            elif key == curses.KEY_DOWN and current < len(tasks) - 1:
                fn = move_block if block_mode else move_task
                tasks, current = fn(tasks, current, 1)

            elif key == curses.KEY_RIGHT:
                tasks = indent_task(tasks, current, 1)  # → subtarea

            elif key == curses.KEY_LEFT:
                tasks = indent_task(tasks, current, -1)  # ← tarea normal

            elif key == ord("b"):
                block_mode = not block_mode  # Alternar modo línea/bloque

            # Salir del modo mover
            elif key in (ord("m"), 27, ord("\n"), ord("\r"), curses.KEY_ENTER):
                move_mode = False
                block_mode = False

        # ===== MODO NORMAL =====
        else:
            # Navegación
            if key == curses.KEY_UP and current > 0:
                current -= 1
            elif key == curses.KEY_DOWN and current < len(tasks) - 1:
                current += 1

            # Enter: marcar/desmarcar tarea
            elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                tasks = toggle_task(tasks, current)

            # Teclas de acción (cada una llama a su función)
            elif key == ord("m"):
                move_mode = True  # Entrar a modo mover
            elif key == ord("a"):
                tasks = add_task(stdscr, tasks)
            elif key == ord("s"):
                tasks, current = add_subtask(stdscr, tasks, current)
            elif key == ord("k"):
                tasks, current = delete_line(tasks, current)
            elif key == 11:  # Ctrl+K
                tasks, current = delete_block(tasks, current)
            elif key == ord("u"):
                # Deshacer: si el estado restaurado es diferente al actual
                restored = undo_task(tasks)
                if restored != tasks:
                    tasks = restored
                    save_tasks(tasks)
                current = min(current, len(tasks) - 1)
            elif key == ord("c"):
                tasks = edit_task_menu(stdscr, tasks, current)
            elif key == ord("q"):
                break  # SALIR del programa (rompe el while True)


# =============================================================================
# FUNCIÓN: main (líneas 625-626)
# =============================================================================
# PROPÓSITO: Punto de entrada del programa.

def main():
    # curses.wrapper() es una FUNCIÓN ESPECIAL que:
    # 1. Inicializa curses (configura la terminal, desactiva echo, etc.)
    # 2. Llama a nuestra función draw(stdscr)
    # 3. Cuando draw termina (o crashea), RESTAURA la terminal a su
    #    estado original. Esto es CRUCIAL: sin esto, si el programa
    #    falla, la terminal se queda en un estado raro.
    curses.wrapper(draw)
    # Nota: no hay que llamar a draw() directamente, wrapper lo hace.


# =============================================================================
# LÍNEAS 629-630: PUNTO DE ENTRADA
# =============================================================================
# Este bloque es el "arranque" del programa.

if __name__ == "__main__":
    # __name__ es una variable especial de Python.
    # Vale "__main__" SOLO cuando ejecutas este archivo directamente
    # con "python todo.py".
    # Si en cambio IMPORTAS este archivo desde otro (from todo import ...),
    # __name__ vale "todo" (el nombre del módulo), y este bloque NO se ejecuta.
    # Esto permite usar el archivo como programa y como módulo reutilizable.
    main()
