# pihat_server.py review

Reviewed 2026-10-11 on branch `develop` (commit `4e46d0a`, with the CPU/battery poll thread).
Fixes were applied in commit `dcd2b7b`. They were tested against a fake SenseHat, not on real hardware.

## Fixed in dcd2b7b

| # | Issue | Effect | Fix |
|---|-------|--------|-----|
| 1 | Global `exit=False` shadowed the built-in `exit()` | When `init()` failed, `exit()` raised `TypeError: 'bool' object is not callable` instead of exiting | Renamed it to `poll_exit`. A failed start now calls `sys.exit(1)` |
| 2 | `stop_server` never reset the flag | After `7.stop`, `6.start` started a thread that ended at once | `start_server` resets `poll_exit = False` |
| 3 | `stop_server` cleared the LEDs before joining the thread | The thread could redraw the bars after the clear | It joins the thread first, then clears |
| 4 | `cpu.get_cpuUsage()` returns `''` when psutil is missing | `percent_bar` raised `TypeError` and the poll thread died | The CPU bar is skipped when the value is `''` |
| 5 | `percent_bar` used `top_y = int(7 - val*7/100)` | 0% still lit the bottom LED | `top_y = 8 - round(val*8/100)`. 0% lights 0 LEDs and 100% lights 8 |
| 6 | Ctrl+C or an error during a menu action skipped `stop_server()` | The non-daemon poll thread kept the process running forever | `cli()` is wrapped in `try/finally: stop_server()` |
| 7 | `clear_matrix` used `col.copy()` | Crashed on tuple colours, such as the ones `get_color()` returns | It uses `list(col)` |
| 8 | Matrix cells shared colour lists (`led_matrix` literal, `test_matrix`) | Changing one cell in place changed every cell and `White_col`/`Black_col` | Each cell gets its own list |
| 9 | `intro`, `intro2`, `colors` called `sense.*` with no `None` check | `AttributeError` if called before `init()` succeeded | Added `if sense is None: return`. `start_server` also checks it |
| 10 | `clear_matrix`, `set_matrix`, `draw_rect`, `percent_bar` returned early when `sense is None` | They only edit the in-memory matrix, so without hardware they silently did nothing | Removed the guard |

## Still open (not changed)

- `colors()` draws with `set_pixel` and never updates `led_matrix`, so the stored matrix goes out of sync with the display.
- The poll thread and the CLI both change `led_matrix` with no lock. For example, menu `2.clear` while the thread runs gets redrawn on its next tick.
- `intro()` and `test_matrix()` aren't called anywhere, because the menu's intro option runs `intro2`.
- Style:
  - Lines 12–13 use tabs for alignment, and some lines have trailing whitespace.
  - The code uses `== None` / `!= None` where `is None` is the convention.
  - `exist()` can be a single line, `return sense is not None`.
  - The local variable `battery` in `poll_thread` shares its name with the module (imported as `batt`), which is easy to mix up.
- `O`/`X` are aliases of `Black_col`/`White_col` and are no longer used.
