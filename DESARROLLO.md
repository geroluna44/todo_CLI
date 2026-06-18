# DESARROLLO — To-Do CLI

## Descripción

CLI interactivo con curses para manipular un archivo de tareas plano (`~/life/to-do.txt`). Navegación con cursor, marcado de tareas, reordenamiento, y gestión de subtareas.

## Estructura del archivo de tareas

```
[ ] [Categoria] Nombre de la tarea | Prioridad
[X] [Trabajo] Tarea resuelta | A
--- [ ] Subtarea sin categoría ni prioridad
```

- `[ ]` / `[X]` — estado pendiente/resuelto
- `[Categoria]` — opcional (solo tareas padre)
- `| A | B | C` — prioridad opcional (solo tareas padre)
- `--- ` — prefijo de subtarea

## Arquitectura del programa

**Archivo único:** `todo.py`

### Funciones principales

| Función | Rol |
|---|---|
| `load_tasks(path)` | Carga tareas desde el archivo, retorna lista de strings |
| `save_tasks(tasks)` | Guarda lista completa al archivo |
| `toggle_task(tasks, idx)` | Alterna `[ ]` ↔ `[X]` |
| `get_block(tasks, idx)` | Retorna `(start, end)` del bloque conteniendo `idx` |
| `move_task(tasks, idx, direction)` | Intercambia la línea actual con la de arriba/abajo |
| `move_block(tasks, idx, direction)` | Mueve todo el bloque (tarea + subtareas `---`) |
| `indent_task(tasks, idx, direction)` | Agrega/quita prefijo `--- ` |
| `add_task(stdscr, tasks)` | Input de nombre, categoría, prioridad; agrega al final |
| `add_subtask(stdscr, tasks, idx)` | Input de nombre; inserta al final del bloque actual |
| `delete_line(tasks, idx)` | Elimina la línea en `idx` |
| `delete_block(tasks, idx)` | Elimina el bloque completo |
| `get_input(stdscr, y, x, prompt)` | Campo de texto editable con backspace |
| `show_splash(stdscr)` | Muestra banner ASCII centrado |
| `parse_line(line)` | Descompone línea en `(status, cat, name, prio, is_sub)` |
| `build_line(status, cat, name, prio, is_sub)` | Reconstruye línea desde sus partes |
| `edit_task_menu(stdscr, tasks, idx)` | Menú interactivo para modificar nombre/categoría/prioridad |
| `draw_menu_overlay(stdscr, sel, options)` | Dibuja superposición del menú de acciones centrado |
| `_key_str(k)` | Convierte código de tecla a string legible (ej: `11` → `"^K"`) |
| `draw_small_term_warning(stdscr, ...)` | Dibuja cartel de terminal muy pequeña |
| `draw(stdscr)` | Loop principal de curses (modo normal + modo mover) |

### Constantes

| Nombre | Descripción |
|---|---|
| `MENU_OPTIONS` | Lista de tuplas `(label, key_code)` para el menú de acciones |
| `BANNER` | Lista de strings del logo ASCII |
| `VERSION` | Versión actual del programa |
| `_MAX_HISTORY` | Máximo de estados guardados para undo (50) |

### Variables globales

| Variable | Tipo | Descripción |
|---|---|---|
| `_filepath` | `str` | Ruta al archivo activo (seteada en `load_tasks`) |
| `_history` | `list[list[str]]` | Historial de undo (máx. 50 estados) |
| `VERSION` | `str` | `"v.0.2"` |

### Historial de undo

- `push_history(tasks)` guarda una copia superficial (`[t for t in tasks]`) antes de cada mutación.
- `undo_task(tasks)` restaura el estado anterior si existe.
- Se llama a `push_history` dentro de: `toggle_task`, `move_task`, `move_block`, `indent_task`, `add_task`, `add_subtask`, `delete_line`, `delete_block`.

## Controles de teclado

### Modo normal

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Navegar |
| `Enter` | Toggle `[ ]` / `[X]` |
| `a` | Añadir tarea |
| `s` | Añadir subtarea |
| `k` | Eliminar línea |
| `Ctrl+K` | Eliminar bloque |
| `Tab` | Abrir menú de acciones |
| `C` | Modificar nombre/categoría/prioridad |
| `u` | Undo |
| `m` | Entrar a modo mover |
| `q` | Salir |

### Modo mover

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Mover (línea o bloque según `b`) |
| `→` | Indentar → subtarea |
| `←` | Indentar ← tarea |
| `b` | Alternar línea/bloque |
| `m` / `ESC` / `Enter` | Salir del modo mover |

## Notas técnicas

- Se usa `curses.wrapper(draw)` para inicialización/restauración limpia de la terminal.
- Las flechas se renderizan con unicode (`\u2191\u2193`). Si el terminal no las soporta, reemplazar por ASCII plano.
- El truncamiento de barras de estado evita `addwstr() returned ERR`. Se aplica `status[:width - 1]` si excede el ancho.
- La detección de `Ctrl+K` usa código ASCII `11`. Si un terminal mapea distinto, ajustar.
- `curses.curs_set(0)` oculta el cursor en la lista; `curs_set(1)` lo muestra durante inputs.
- `curses.napms(ms)` se usa para pausas breves (mensajes de confirmación de 800ms).
- `get_input()` usa `get_wch()` en vez de `getch()` para aceptar caracteres UTF-8 como acentos y `ñ`. `getch()` trunca multi-byte a enteros 0-255.

## Changelog

### v0.2
- Soporte de acentos y `ñ` en inputs (migración a `get_wch()`)
- Tecla `C` para modificar nombre, categoría o prioridad de tareas y subtareas
- Menú interactivo centrado con opciones según tipo de tarea
- Funciones `parse_line()` y `build_line()` para descomponer/reconstruir líneas
- Menú de acciones con `Tab` (navegación `↑/↓`, Enter ejecuta, Tab/ESC cierra)

### v0.1
- Implementación inicial con curses
- Navegación, toggle, modo mover (línea/bloque)
- Indentar subtareas con flechas
- Añadir tarea (con categoría y prioridad) y subtarea
- Eliminar línea y bloque
- Undo con historial (hasta 50)
- Banner splash centrado
