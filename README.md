# To-Do CLI v0.2

Programa para manipular archivos de tareas al estilo `~/life/to-do.txt`.

## Formato del archivo

Cada línea es una tarea. Puede incluir:

- `[ ]` — tarea pendiente
- `[X]` — tarea resuelta
- `[Categoria]` — categoría (ej: `[Trabajo]`, `[Orden]`)
- `| A | B | C` — prioridad
- `--- ` — indica que es una subtarea (anidada bajo la tarea anterior)

## Instalación

```bash
python3 todo.py
```

El programa busca primero `~/life/to-do.txt`. Si no existe, usa el archivo `to-do.txt` local.

## Modo normal

| Tecla | Acción |
|---|---|
| `Tab` | Abrir menú de acciones |
| `↑` / `↓` | Navegar entre tareas |
| `Enter` | Marcar/desmarcar tarea como resuelta (`[ ]` ↔ `[X]`) |
| `a` | Añadir tarea (pide nombre, categoría y prioridad A/B/C) |
| `s` | Añadir subtarea (se inserta al final del bloque actual) |
| `k` | Eliminar línea actual |
| `Ctrl+K` | Eliminar bloque (tarea + subtareas) |
| `C` | Modificar nombre, categoría o prioridad de una tarea |
| `u` | Deshacer última modificación (hasta 50 cambios) |
| `m` | Activar modo mover |
| `q` | Salir |

Dentro del menú: `↑/↓` navegar, `Enter` ejecutar, `Tab/ESC` cerrar.

## Modo mover

Se activa con `m` y se desactiva con `m`, `ESC` o `Enter`.

| Tecla | Acción |
|---|---|
| `↑` / `↓` | Mover línea o bloque (según modo) |
| `→` | Convertir en subtarea (agrega `--- `) |
| `←` | Convertir en tarea (quita `--- `) |
| `b` | Alternar entre mover línea / mover bloque |
| `m` / `ESC` / `Enter` | Salir del modo mover |

Todos los cambios se guardan automáticamente en el archivo.
