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
| 5 | `percent_bar` used `top_y = int(7 - val*7/100)` | 0% still lit the bottom LED | `top_y = 8 - round(val*8/100)`. 0% lights 0 LEDs and 100% lights 8. Replaced later by the partial top LED, see below |
| 6 | Ctrl+C or an error during a menu action skipped `stop_server()` | The non-daemon poll thread kept the process running forever | `cli()` is wrapped in `try/finally: stop_server()` |
| 7 | `clear_matrix` used `col.copy()` | Crashed on tuple colours, such as the ones `get_color()` returns | It uses `list(col)` |
| 8 | Matrix cells shared colour lists (`led_matrix` literal, `test_matrix`) | Changing one cell in place changed every cell and `White_col`/`Black_col` | Each cell gets its own list |
| 9 | `intro`, `intro2`, `colors` called `sense.*` with no `None` check | `AttributeError` if called before `init()` succeeded | Added `if sense is None: return`. `start_server` also checks it |
| 10 | `clear_matrix`, `set_matrix`, `draw_rect`, `percent_bar` returned early when `sense is None` | They only edit the in-memory matrix, so without hardware they silently did nothing | Removed the guard |

## Fixed in 4edbc51

Tested against a fake SenseHat, not on real hardware.

| # | Issue | Effect | Fix |
|---|-------|--------|-----|
| 11 | `colors()` drew with `set_pixel` and never updated `led_matrix` | The stored matrix went out of sync with the display | It writes with `set_matrix`, then calls `sense.set_pixels(led_matrix)` once |
| 12 | The poll thread and the CLI both changed `led_matrix` and the display | Their updates could interleave, for example bars drawn halfway through `intro2` | While polling runs, the menu accepts only `7.stop` and `1.exit`. Any other choice prints a message. A new `server_running()` checks this |
| 13 | If the poll thread died on an error, `p_thrd` still pointed at the dead thread | `6.start` did nothing until `7.stop` | `start_server` also starts a new thread when `p_thrd` isn't alive |
| 14 | Style | | Removed the tabs and trailing whitespace. `== None` became `is None`. `exist()` is now one line. The local `battery` became `ina219`. Removed the unused `O`/`X` |

## Features added after the review

Tested against a fake SenseHat. Not yet confirmed on the Pi.

### Display layout

The poll thread draws one bar per value every second (the CPU reading itself takes 2 s).

| x | Bar | Colour | Full bar at | Source |
|---|-----|--------|-------------|--------|
| 1 | Memory usage | 15 | 100% | `cpu.get_memUsage()` |
| 2 | CPU usage | 6 | 100% | `cpu.get_cpuUsage()` |
| 5 | Battery charge | 24 | 100% | `bat_info['Percent']` |
| 6 | Battery current | 16 if negative, 23 if positive | 1.5 A or more | `bat_info['Current']` |

The memory and CPU bars are skipped when their reading is `''`. The two battery bars are drawn only when the INA219 is found.

### Changes

| Commit | Change |
|--------|--------|
| `d68450b` | Battery current bar at x=6. Length is `abs(Current) / 1.5 A`, capped at 100%. The colour shows the direction |
| `cff813a` | `lib/cpuinfo.py`: new `get_memUsage()`. It uses `psutil.virtual_memory().percent` when psutil is installed. Otherwise it reads `/proc/meminfo` and returns `(MemTotal - MemAvailable) / MemTotal` in %. It returns `''` when neither is available |
| `3c340f7` | Memory usage bar at x=1 |
| `d85845c` | Daemon mode and `pihat_server.service`, see below |
| `c256b4d` | Removed `After=multi-user.target` from the service. On the Pi, `wayvnc.service` never finished starting, so `multi-user.target` was never reached and `systemctl start pihat_server` hung |
| `6f4e27f` | `percent_bar` shows the leftover value as brightness. Each LED is 12.5%. The full LEDs light from the bottom, and the LED above them gets the leftover fraction of the colour. For example, 56% lights 4 full LEDs and a 5th at 48% |
| `610d935` | `BAR_GAMMA` for the partial LED: `level = rest ** BAR_GAMMA`. It defaults to 1.0, because the Sense HAT driver already applies its own gamma table (`sense.gamma`). Raise it toward 2.2 if the partial LED looks too bright |
| — | Removed the unused `intro()` and `test_matrix()` (the menu's intro option ran `intro2`). Renamed `intro2` to `intro` |

### Daemon mode

`python3 pihat_server.py -d` (or `--daemon`) runs without the menu:

1. It shows `intro(0.2)`, then starts the poll thread.
2. It runs until SIGTERM (`systemctl stop`) or SIGINT (Ctrl+C). Then it stops the thread, clears the LEDs and exits with code 0.
3. If the poll thread dies, it exits with code 1, so `Restart=on-failure` restarts it after 10 s.

With no argument the menu runs as before.

`pihat_server.service` runs it as user `gkyr` from `/home/gkyr/Work/Python_test1/sensehat`. The install and log commands are in the comment at the top of the file. The user needs the `i2c`, `video` and `input` groups for the Sense HAT and the INA219.

## Still open (not changed)

- The Sense HAT shows only 32 levels per colour channel, so a very small leftover on a bar's top LED can round down to dark. This is worse for colours that use 128 instead of 255.
- On the Pi, `wayvnc.service` hangs at boot and keeps `multi-user.target` from being reached. It doesn't affect pihat_server any more, but other units ordered after that target still wait.
