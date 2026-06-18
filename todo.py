#!/usr/bin/env python3
import curses
import os

TODO_FILE = os.path.expanduser("~/life/to-do.txt")
FALLBACK_FILE = os.path.join(os.path.dirname(__file__), "to-do.txt")
_filepath = None
_history = []
_MAX_HISTORY = 50
VERSION = "v0.2"

MENU_OPTIONS = [
    ("Añadir tarea", ord("a")),
    ("Añadir subtarea", ord("s")),
    ("Modificar tarea", ord("c")),
    ("Eliminar linea", ord("k")),
    ("Eliminar bloque", 11),
    ("Deshacer", ord("u")),
    ("Mover", ord("m")),
    ("Salir del programa", ord("q")),
]

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


def load_tasks(path):
    global _filepath
    if os.path.exists(path):
        _filepath = path
    elif os.path.exists(FALLBACK_FILE):
        _filepath = FALLBACK_FILE
    else:
        return []
    with open(_filepath, "r") as f:
        return [line.rstrip("\n") for line in f]


def save_tasks(tasks):
    with open(_filepath, "w") as f:
        for task in tasks:
            f.write(task + "\n")


def push_history(tasks):
    global _history
    _history.append([t for t in tasks])
    if len(_history) > _MAX_HISTORY:
        _history.pop(0)


def undo_task(tasks):
    global _history
    if _history:
        return _history.pop()
    return tasks


def toggle_task(tasks, idx):
    push_history(tasks)
    line = tasks[idx]
    if "[ ]" in line:
        line = line.replace("[ ]", "[X]", 1)
    elif "[X]" in line:
        line = line.replace("[X]", "[ ]", 1)
    else:
        return tasks
    tasks[idx] = line
    save_tasks(tasks)
    return tasks


def move_task(tasks, idx, direction):
    push_history(tasks)
    target = idx + direction
    if target < 0 or target >= len(tasks):
        return tasks, idx
    tasks[idx], tasks[target] = tasks[target], tasks[idx]
    save_tasks(tasks)
    return tasks, target


def get_block(tasks, idx):
    start = idx
    while start > 0 and tasks[start].startswith("---"):
        start -= 1
    end = start
    while end + 1 < len(tasks) and tasks[end + 1].startswith("---"):
        end += 1
    return start, end


def move_block(tasks, idx, direction):
    push_history(tasks)
    start, end = get_block(tasks, idx)
    offset = idx - start
    if direction == -1:
        if start == 0:
            return tasks, idx
        above_start, above_end = get_block(tasks, start - 1)
        block = tasks[start:end + 1]
        above = tasks[above_start:start]
        new_tasks = tasks[:above_start] + block + above + tasks[end + 1:]
        new_idx = above_start + offset
    elif direction == 1:
        if end == len(tasks) - 1:
            return tasks, idx
        below_start, below_end = get_block(tasks, end + 1)
        block = tasks[start:end + 1]
        below = tasks[end + 1:below_end + 1]
        new_tasks = tasks[:start] + below + block + tasks[below_end + 1:]
        new_idx = start + len(below) + offset
    save_tasks(new_tasks)
    return new_tasks, new_idx


def indent_task(tasks, idx, direction):
    push_history(tasks)
    line = tasks[idx]
    if direction == 1:
        if not line.startswith("--- "):
            line = "--- " + line
    elif direction == -1:
        if line.startswith("--- "):
            line = line[4:]
        elif line.startswith("---"):
            line = line[3:]
    tasks[idx] = line
    save_tasks(tasks)
    return tasks


def show_splash(stdscr):
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()
    stdscr.clear()

    max_w = max(len(l) for l in BANNER)
    x = max(0, (width - max_w) // 2)
    y = max(0, (height - len(BANNER)) // 2)

    for i, line in enumerate(BANNER):
        if x + len(line) < width:
            stdscr.addstr(y + i, x, line)

    msg = "Presiona cualquier tecla para continuar"
    mx = max(0, (width - len(msg)) // 2)
    my = min(y + len(BANNER) + 2, height - 1)
    stdscr.addstr(my, mx, msg)

    stdscr.refresh()
    stdscr.getch()


def get_input(stdscr, y, x, prompt):
    curses.curs_set(1)
    stdscr.addstr(y, x, prompt)
    stdscr.refresh()
    buf = ""
    while True:
        key = stdscr.get_wch()
        if isinstance(key, str):
            if key in ("\n", "\r"):
                break
            elif key in ("\x7f", "\b"):
                if buf:
                    buf = buf[:-1]
                    stdscr.addstr(y, x + len(prompt), buf + " ")
                    stdscr.move(y, x + len(prompt) + len(buf))
            elif key >= " ":
                buf += key
                stdscr.addstr(y, x + len(prompt) + len(buf) - 1, key)
        elif isinstance(key, int):
            if key == curses.KEY_ENTER:
                break
            elif key == curses.KEY_BACKSPACE:
                if buf:
                    buf = buf[:-1]
                    stdscr.addstr(y, x + len(prompt), buf + " ")
                    stdscr.move(y, x + len(prompt) + len(buf))
        stdscr.refresh()
    curses.curs_set(0)
    return buf


def add_task(stdscr, tasks):
    push_history(tasks)
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    y = h // 2 - 2

    name = get_input(stdscr, y, 2, "Nombre de la tarea: ")
    cat = get_input(stdscr, y + 1, 2, "Ingrese la categoria: ")
    while True:
        prio = get_input(stdscr, y + 2, 2, "Ingrese la prioridad (A/B/C): ").upper()
        if prio in ("A", "B", "C"):
            break
        stdscr.addstr(y + 3, 2, "Prioridad invalida. Use A, B o C.")
        stdscr.refresh()
        curses.napms(1000)
        stdscr.move(y + 2, 2 + len("Ingrese la prioridad (A/B/C): "))
        stdscr.clrtoeol()
        stdscr.refresh()

    linea = f"[ ] [{cat}] {name} | {prio}"
    tasks.append(linea)
    save_tasks(tasks)

    stdscr.clear()
    stdscr.addstr(h // 2, 2, "Tarea agregada correctamente!")
    stdscr.refresh()
    curses.napms(800)
    return tasks


def add_subtask(stdscr, tasks, idx):
    push_history(tasks)
    _, block_end = get_block(tasks, idx)
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    y = h // 2 - 1

    name = get_input(stdscr, y, 2, "Nombre de la subtarea: ")

    linea = f"--- [ ] {name}"
    tasks.insert(block_end + 1, linea)
    save_tasks(tasks)

    stdscr.clear()
    stdscr.addstr(h // 2, 2, "Subtarea agregada correctamente!")
    stdscr.refresh()
    curses.napms(800)
    return tasks, block_end + 1


def delete_line(tasks, idx):
    push_history(tasks)
    del tasks[idx]
    save_tasks(tasks)
    return tasks, min(idx, len(tasks) - 1)


def delete_block(tasks, idx):
    push_history(tasks)
    start, end = get_block(tasks, idx)
    del tasks[start:end + 1]
    save_tasks(tasks)
    return tasks, min(start, len(tasks) - 1)


def parse_line(line):
    is_sub = line.startswith("--- ")
    rest = line[4:] if is_sub else line
    status = rest[:4]
    rest = rest[4:]
    cat = ""
    prio = ""
    if is_sub:
        name = rest
    else:
        if rest.startswith("["):
            end_bracket = rest.find("]")
            if end_bracket != -1:
                cat = rest[1:end_bracket]
                rest = rest[end_bracket + 2:]
        pipe = rest.rfind(" | ")
        if pipe != -1:
            name = rest[:pipe]
            prio = rest[pipe + 3:]
        else:
            name = rest
    return status, cat, name, prio, is_sub


def build_line(status, cat, name, prio, is_sub):
    if is_sub:
        return f"--- {status}{name}"
    if cat and prio:
        return f"{status}[{cat}] {name} | {prio}"
    if cat:
        return f"{status}[{cat}] {name}"
    if prio:
        return f"{status}{name} | {prio}"
    return f"{status}{name}"



def edit_task_menu(stdscr, tasks, idx):
    push_history(tasks)
    status, cat, name, prio, is_sub = parse_line(tasks[idx])

    if is_sub:
        options = ["Nombre"]
        values = {"Nombre": name}
        rebuild = lambda new: build_line(status, cat, new, prio, is_sub)
    else:
        options = ["Nombre", "Categoria", "Prioridad"]
        values = {"Nombre": name, "Categoria": cat, "Prioridad": prio}
        def rebuild(new_cat, new_name, new_prio):
            return build_line(status, new_cat, new_name, new_prio, is_sub)

    h, w = stdscr.getmaxyx()
    sel = 0
    while True:
        stdscr.clear()
        title = " Modificar "
        tw = len(title)
        max_opt_w = max(len(o) for o in options)
        box_w = max(tw, max_opt_w + 4) + 4
        bx = max(0, (w - box_w) // 2)
        by = max(0, (h - len(options) - 4) // 2)

        stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(by, bx + (box_w - tw) // 2, title)
        stdscr.attroff(curses.A_REVERSE)

        for i, opt in enumerate(options):
            y = by + 2 + i
            if i == sel:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, bx + 2, f"  {opt}  ")
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, bx + 2, f"  {opt}  ")

        foot = "Enter: seleccionar  ESC/q: cancelar"
        stdscr.addstr(h - 1, 0, foot[:w - 1])
        stdscr.refresh()

        key = stdscr.getch()
        if key == curses.KEY_UP and sel > 0:
            sel -= 1
        elif key == curses.KEY_DOWN and sel < len(options) - 1:
            sel += 1
        elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
            field = options[sel]
            stdscr.clear()
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

            if new_val:
                if field == "Nombre":
                    name = new_val
                elif field == "Categoria":
                    cat = new_val
                elif field == "Prioridad":
                    prio = new_val

                if is_sub:
                    tasks[idx] = build_line(status, cat, name, prio, is_sub)
                else:
                    tasks[idx] = build_line(status, cat, name, prio, is_sub)
                save_tasks(tasks)

            break
        elif key in (ord("q"), 27):
            break

    return tasks


def _key_str(k):
    if k == 11:
        return "^K"
    if k == 27:
        return "ESC"
    if 0 < k < 32:
        return f"^{chr(k + 64)}"
    return chr(k).upper()


def draw_small_term_warning(stdscr, w, h, min_w, min_h):
    msg1 = "Terminal demasiado pequena"
    msg2 = f"Minimo: {min_w} ancho x {min_h} alto"
    msg_w = max(len(msg1), len(msg2)) + 4
    if msg_w > w or 4 > h:
        return
    bx = max(0, (w - msg_w) // 2)
    by = max(0, (h - 4) // 2)
    stdscr.addstr(by, bx,     "+" + "-" * (msg_w - 2) + "+")
    stdscr.addstr(by + 1, bx, "| " + msg1 + " " * (msg_w - 4 - len(msg1)) + " |")
    stdscr.addstr(by + 2, bx, "| " + msg2 + " " * (msg_w - 4 - len(msg2)) + " |")
    stdscr.addstr(by + 3, bx, "+" + "-" * (msg_w - 2) + "+")


def draw_menu_overlay(stdscr, sel, options):
    h, w = stdscr.getmaxyx()

    max_label = max(len(o[0]) + len(_key_str(o[1])) + 8 for o in options)
    box_w = max_label + 12
    box_h = len(options) + 5

    if box_w > w or box_h > h:
        draw_small_term_warning(stdscr, w, h, box_w, box_h)
        return

    bx = max(0, (w - box_w) // 2)
    by = max(0, (h - box_h) // 2)

    for i in range(box_h):
        for j in range(box_w):
            if i == 0:
                ch = "\u2550" if 0 < j < box_w - 1 else ("\u2554" if j == 0 else "\u2557")
            elif i == box_h - 1:
                ch = "\u2550" if 0 < j < box_w - 1 else ("\u255a" if j == 0 else "\u255d")
            elif j == 0 or j == box_w - 1:
                ch = "\u2551"
            elif i == len(options) + 3:
                ch = "\u2560" if j == 0 else ("\u2563" if j == box_w - 1 else "\u2550")
            else:
                ch = " "
            if bx + j < w and by + i < h:
                try:
                    stdscr.addstr(by + i, bx + j, ch)
                except:
                    pass

    title = " Menu "
    tx = bx + (box_w - len(title)) // 2
    stdscr.addstr(by, tx, title)

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

    foot = " Salir de este menu  [Tab]"
    fx = bx + (box_w - len(foot)) // 2
    stdscr.addstr(by + len(options) + 4, fx, foot)


def draw(stdscr):
    show_splash(stdscr)

    tasks = load_tasks(TODO_FILE)
    if not tasks:
        stdscr.addstr(0, 0, "No se encontró el archivo to-do.txt")
        stdscr.getch()
        return

    curses.curs_set(0)

    current = 0
    move_mode = False
    block_mode = False
    menu_active = False
    menu_sel = 0

    while True:
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        max_lines = height - 2
        start = max(0, current - max_lines // 2)

        block_start, block_end = get_block(tasks, current) if (move_mode and block_mode) else (-1, -1)

        for i, task in enumerate(tasks[start:start + max_lines], start=start):
            y = i - start
            in_block = block_start <= i <= block_end
            if i == current:
                attr = curses.A_REVERSE | (curses.A_UNDERLINE if move_mode else 0)
                stdscr.attron(attr)
                line = f"> {task}"
                if len(line) >= width:
                    line = line[:width - 1]
                stdscr.addstr(y, 0, line)
                stdscr.attroff(attr)
            elif in_block:
                stdscr.attron(curses.A_UNDERLINE)
                prefix = "  "
                line = f"{prefix}{task}"
                if len(line) >= width:
                    line = line[:width - 1]
                stdscr.addstr(y, 0, line)
                stdscr.attroff(curses.A_UNDERLINE)
            else:
                prefix = "  "
                line = f"{prefix}{task}"
                if len(line) >= width:
                    line = line[:width - 1]
                stdscr.addstr(y, 0, line)

        if move_mode:
            if block_mode:
                left = "MOVER BLOQUE"
            else:
                left = "MOVER LINEA  |  B: mover bloque"
        else:
            left = "Tab: Menu"

        right = f"ToDo by geroluna {VERSION}"
        padding = width - len(left) - len(right) - 2
        if padding < 1:
            padding = 1
        status = left + " " * padding + right
        if len(status) >= width:
            status = status[:width - 1]
        stdscr.addstr(height - 1, 0, status)

        menu_w = max(len(o[0]) + len(_key_str(o[1])) + 8 for o in MENU_OPTIONS) + 12
        menu_h = len(MENU_OPTIONS) + 5
        if menu_w > width or menu_h > height:
            draw_small_term_warning(stdscr, width, height, menu_w, menu_h)

        if menu_active:
            draw_menu_overlay(stdscr, menu_sel, MENU_OPTIONS)
        stdscr.refresh()

        key = stdscr.getch()
        if 65 <= key <= 90:
            key = key + 32

        if menu_active:
            if key == curses.KEY_UP:
                menu_sel = (menu_sel - 1) % len(MENU_OPTIONS)
                continue
            elif key == curses.KEY_DOWN:
                menu_sel = (menu_sel + 1) % len(MENU_OPTIONS)
                continue
            elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                key = MENU_OPTIONS[menu_sel][1]
                menu_active = False
            elif key in (ord("\t"), 27):
                menu_active = False
                continue
            else:
                continue

        if key == ord("\t") and not move_mode:
            menu_active = True
            menu_sel = 0
            continue

        if move_mode:
            if key == curses.KEY_UP and current > 0:
                fn = move_block if block_mode else move_task
                tasks, current = fn(tasks, current, -1)

            elif key == curses.KEY_DOWN and current < len(tasks) - 1:
                fn = move_block if block_mode else move_task
                tasks, current = fn(tasks, current, 1)

            elif key == curses.KEY_RIGHT:
                tasks = indent_task(tasks, current, 1)

            elif key == curses.KEY_LEFT:
                tasks = indent_task(tasks, current, -1)

            elif key == ord("b"):
                block_mode = not block_mode
            elif key in (ord("m"), 27, ord("\n"), ord("\r"), curses.KEY_ENTER):
                move_mode = False
                block_mode = False
        else:
            if key == curses.KEY_UP and current > 0:
                current -= 1
            elif key == curses.KEY_DOWN and current < len(tasks) - 1:
                current += 1
            elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
                tasks = toggle_task(tasks, current)

            elif key == ord("m"):
                move_mode = True
            elif key == ord("a"):
                tasks = add_task(stdscr, tasks)

            elif key == ord("s"):
                tasks, current = add_subtask(stdscr, tasks, current)

            elif key == ord("k"):
                tasks, current = delete_line(tasks, current)

            elif key == 11:
                tasks, current = delete_block(tasks, current)

            elif key == ord("u"):
                restored = undo_task(tasks)
                if restored != tasks:
                    tasks = restored
                    save_tasks(tasks)
                current = min(current, len(tasks) - 1)

            elif key == ord("c"):
                tasks = edit_task_menu(stdscr, tasks, current)

            elif key == ord("q"):
                break


def main():
    curses.wrapper(draw)


if __name__ == "__main__":
    main()
