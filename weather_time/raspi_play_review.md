# raspi_play.py review

Review of `weather_time/raspi_play.py` and the modules it uses. First written 2026-09-27 on branch `ai_work`; last updated 2026-09-30 for branch `claude_work` at commit aa58469.

## What it does

A Tkinter dashboard sized for a 320x240 Raspberry Pi LCD:

- **Top panel:** big clock (HH:MM + seconds) and date (day, weekday, month, year) in Greek or English.
- **Bottom-left panel:** tap to cycle between an IP/CPU/battery view (LAN and Wi-Fi IP, CPU usage and temperature, INA219 battery % and current) and room sensor views (SENSOR 1 = Sense HAT or AHT10 temperature/humidity, SENSOR 2 = SI7021, SENSOR 3 = Sense HAT or MPL3115 pressure/altitude).
- **Bottom-right panel:** current weather from OpenWeatherMap (description, temp, feels-like, humidity, pressure, wind, icon with a night variant). Tap it to swap to a 3-hourly forecast table for one day; tap the first/last icon to go back/forward a day; it returns to normal after 30 s.
- **Tap the clock:** opens the history graph (`simplegraph.py`) drawn from the binary log, with a "Wait Load Graph" message while it loads.
- **Keys 1/2/3** (on-screen, and GPIO 18/23/24 on the Pi): 1 = test popup, 2 = options form (`optionform.py`, placeholder tabs, needs Pmw), 3 = exit.
- Polls the sensors every 60 s and the weather every 120 s for display, and pushes the web pressure into the barometer as sea-level reference. It works on its own; it does not write the repository.
- **On Windows** (no daemon) it also runs `sensor_server` in a background thread so the repository is still updated, and stops it on exit.
- Disables the X screensaver/DPMS while running.

**Settings** shared by the screens live in `options.py`: `LCD_SIZE`, `FULL_SCREEN` (currently 1), `LANG` (EN/GR), plus `center_form()` and the `wait_msg()` popup.

**Sense HAT detection:** `repository.USE_PI_SENSE_HAT` is set from `pihatsense.exist()`, and both raspi_play and sensor_server read it from there. Without a Sense HAT (or on Windows) they use the AHT10/MPL3115 readings.

**sensor_server.py** does the logging: it polls the weather site (120 s) and the sensors (60 s), sets the sea pressure, and appends a record to `weather_time/repository/sensor-YYYY-MM.bin`. Every weather poll logs the web temperature and humidity (`web temper: 20.9 C, humid: 71 %`).

- **From a terminal** (`python3 sensor_server.py`) it shows a menu while polling continues in a thread: `1. exit` stops cleanly (Ctrl+C or Ctrl+D too), `2. graph` opens the `simplegraph.py` window and returns to the menu when it closes. Without a display it prints "cannot open graph window" and keeps running.
- **As a daemon** it runs as a systemd service (`sensor_server.service`, started with `--no-cli`) and stops cleanly on SIGTERM.
- Options: `--sensor-period`, `--weather-period`, `--once` (single poll and exit), `--no-cli`.

Install on the Pi (in `/home/gkyr/Work/Python_test1/weather_time`):

```
sudo apt install python3-pmw
sudo cp sensor_server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sensor_server
journalctl -u sensor_server -f
```

## Structure

| Piece | Where |
|---|---|
| Helpers: month/weekday names, wind direction, forecast day split | raspi_play.py:53-105 |
| `Gui` class: panels, click handlers, update_* setters, `post()` queue to the Tk thread | raspi_play.py:107-764 |
| Clock thread (1 s) | raspi_play.py:767-787 |
| Weather thread (120 s) | raspi_play.py:790-831 |
| Sensor thread (60 s) + sea-pressure sync, display only | raspi_play.py:834-912 |
| CPU/IP/battery thread (5 s) | raspi_play.py:915-952 |
| GPIO keys | raspi_play.py:959-972 |
| Main: start threads (plus sensor_server thread on Windows), mainloop, cleanup | raspi_play.py:987-1031 |
| Shared settings and popups | options.py |
| Logging: weather poll + web log, sensors, poll loop | sensor_server.py:32-89 |
| Menu (exit / graph) and startup options | sensor_server.py:92-148 |
| systemd unit | sensor_server.service |
| Weather API client | weather.py |
| Sensor drivers | aht10sense.py, si7021sense.py, mpl3115sense.py, pihatsense.py |
| Binary log save/load, Sense HAT detection | repository.py |
| Graph screen / options form | simplegraph.py / optionform.py |

All worker threads (and the GPIO key callbacks) hand GUI updates to `Gui.post()`; the Tk main loop runs them every 100 ms.

## Bugs

### Fixed on claude_work

1. **Tkinter touched from background threads.** Workers and GPIO key callbacks now go through a queue polled by `root.after`; the info popup timeout uses `root.after` instead of `threading.Timer`.
2. **Wind direction East/West swapped.** Now correct, in Greek (Β, ΒΑ, Α, ΝΑ, Ν, ΝΔ, Δ, ΒΔ) or English with `LANG=EN`.
3. **Forecast hours in UTC.** weather.py now uses the epoch `dt` in local time. Days are grouped by date (last slot no longer dropped), Today/Tomorrow comes from the real date, and paging is clamped to the days available.
4. **Sense HAT all zeros when the first weather call failed.** Sea pressure is only taken from a successful reading; pihatsense.py falls back to 1013.25 hPa if it gets 0.
5. **No network timeouts, forecast fetched on the GUI thread.** Requests time out after 10 s; the forecast is fetched in a background thread so the clock keeps running.
6. **`repository/` path depended on the working directory.** It is now always `weather_time/repository`, and a `.gitignore` keeps the data out of git. Old logs written elsewhere (e.g. `Python_test1/repository/`) must be moved there for the graph to show them.
7. **"short format requires -32768 <= number <= 32767" on save.** The Sense HAT returns pressure 0 before its first sample, which gave an altitude of 44330 m and overflowed the 16-bit field. pihatsense.py now creates `SenseHat()` once, retries a 0 pressure and sets altitude 0 when there is no reading; repository.py clamps every value and writes a record in one go, so a failure never leaves half a record.
8. **GPIO keys disabled, Sense HAT flag hard-coded, 1 s sleep in the graph.** Fixed in your commits: `register_keys()` runs (and catches gpiozero errors), `USE_PI_SENSE_HAT` is auto-detected, and the graph no longer sleeps.

### Still open

1. **API keys and a password are public.** `weather.py:4,13,22` holds an OpenWeatherMap key, a Meteosource key and an account password in a comment, and `github.com/gkyrits/Python_test1` is public. Rotate both keys and change the password, then load keys from an untracked config file or environment variable. Removing them from the file does not remove them from git history.
2. **raspi_play won't start without Pmw.** `import optionform` (raspi_play.py:15) imports Pmw at startup, so a Pi without `python3-pmw` fails before the clock appears. Importing optionform inside `option_window()` (raspi_play.py:240) would limit the failure to key 2.
3. **Two readers of the same sensors.** raspi_play and sensor_server both poll I2C. The MPL3115 read is a multi-step sequence with 1 s pauses, so simultaneous reads could occasionally interleave and give a wrong value. The Sense HAT is less affected. On Windows both also call the weather site (two requests every 2 minutes, fine for the free plan).
4. **Duplicate keys in `icon_map_day`** (raspi_play.py:80): 600 and 612 appear more than once, so the last value (24) wins. Any code missing from the map (e.g. Meteosource `Id=0`) raises `KeyError` mid-update; `.get(id, default)` would avoid that.
5. **Graph only looks inside the current month's file** (repository.py:145), so shortly after the 1st of a month the 24 h graph is mostly empty.

## Smaller improvements

- `options.FULL_SCREEN = 1` also applies on Windows, where the window then has no title bar and can only be closed with key 3. `FULL_SCREEN = not sys.platform.startswith('win')` would keep a normal window for testing.
- In `simplegraph.canvas_click` (simplegraph.py:430) the "Please wait" popup stays open if `get_initdata()` raises; a `try/finally` would close it.
- Importing `repository` now opens the Sense HAT (via `pihatsense.exist()`), so every program that only reads the log, such as a standalone graph, also initialises the HAT. Harmless, but a lazy check would avoid it.
- Sensor polling reads all four sensors every cycle even though only one set is in use; the MPL3115 path alone sleeps 2 s.
- Global `exit` in raspi_play.py shadows the built-in; a `threading.Event` (as in sensor_server.py) would also let threads stop immediately.
- The clock thread sleeps a fixed 1 s, so seconds occasionally skip; scheduling with `root.after` aligned to the next second would fix it.
- `repository.load_info()` uses `eval()` on file text (repository.py:137); `ast.literal_eval` is safer.
- `update_battery` (raspi_play.py:280) treats exactly 0 % as "no battery" and blanks the fields.
- `senseInfo_panel` (raspi_play.py:428) configures 6 grid rows but uses 7 for sensor 3.
- Debug `print`s fire on every hover and sensor update.
- `radio_play` (raspi_play.py:220) builds its path from `os.getcwd()` rather than `BASE_DIR`.
