# raspi_play.py review

Review of `weather_time/raspi_play.py` and the modules it uses. First written 2026-09-27 on branch `ai_work`; last updated 2026-10-03 for branch `claude_work` at commit 4d873c8 (options form, sensor enable switches and calibration offsets).

## What it does

A Tkinter dashboard sized for a 320x240 Raspberry Pi LCD:

- **Top panel:** big clock (HH:MM + seconds) and date (day, weekday, month, year) in Greek or English.
- **Bottom-left panel:** tap to cycle through the enabled room sensor views (SENSOR 1 = Sense HAT or AHT10 temperature/humidity, SENSOR 2 = SI7021, SENSOR 3 = Sense HAT or MPL3115 pressure/altitude) and the IP/CPU/battery view (LAN and Wi-Fi IP, CPU usage and temperature, INA219 battery % and current). Disabled sensors are skipped.
- **Bottom-right panel:** current weather from OpenWeatherMap (description, temp, feels-like, humidity, pressure, wind, icon with a night variant). Tap it to swap to a 3-hourly forecast table for one day; tap the first/last icon to go back/forward a day; it returns to normal after 30 s.
- **Tap the clock:** opens the history graph (`simplegraph.py`) drawn from the binary log, with a "Wait Load Graph" message while it loads.
- **Keys 1/2/3** (on-screen, and GPIO 18/23/24 on the Pi): 1 = test popup, 2 = options form (`optionform.py`, needs Pmw), 3 = exit. The form's **Sensors** tab has the S1/S2/S3 enable switches and a calibration offset per sensor value; Ok checks every offset is a number (bad ones turn pink), applies them and saves `options.json`. The other two tabs are still placeholders.
- Polls the sensors every 60 s and the weather every 120 s for display, and pushes the web pressure into the barometer as sea-level reference. It works on its own; it does not write the repository.
- **On Windows** (no daemon) it also runs `sensor_server` in a background thread so the repository is still updated, and stops it on exit.
- Disables the X screensaver/DPMS while running.

**Settings** shared by the screens live in `options.py`: `LCD_SIZE`, `FULL_SCREEN` (currently 1), `LANG` (EN/GR), the `SENSE1/2/3_EN` switches and the per-sensor offsets, plus `center_form()`, `wait_msg()`, `full_screen()` (frameless window) and `grab_keyboard()` (a frameless window gets no keys from the window manager on the Pi, so the options form grabs the keyboard while open).

**Saved settings:** the enable switches and offsets are saved to `weather_time/options.json` (git-ignored, written via a temp file) and loaded at import. raspi_play and sensor_server call `opt.reload_if_changed()` before each sensor read, so a change made in the form reaches sensor_server within one sensor period. Offsets are added inside each sensor driver, so they are already in the logged values; for the Sense HAT the altitude is computed from the corrected pressure.

**Disabled sensors** are not read, not shown, saved as zeros (the record layout stays fixed) and returned as zeros by `load_info_binary()`; the graph hides the T/H buttons when sensor 1 is off and P when sensor 3 is off.

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
| `Gui` class: panels, click handlers, update_* setters, `post()` queue to the Tk thread | raspi_play.py:107-750 |
| Clock thread (1 s) | raspi_play.py:752-773 |
| Weather thread (120 s) | raspi_play.py:775-817 |
| Sensor thread (60 s), enabled sensors only, + sea-pressure sync, display only | raspi_play.py:819-905 |
| CPU/IP/battery thread (5 s) | raspi_play.py:907-945 |
| GPIO keys | raspi_play.py:951-965 |
| Main: start threads (plus sensor_server thread on Windows), mainloop, cleanup | raspi_play.py:981-1023 |
| Shared settings, options.json save/load, popups, full screen, keyboard grab | options.py |
| Logging: weather poll + web log, enabled sensors, poll loop | sensor_server.py:33-97 |
| Menu (exit / graph) and startup options | sensor_server.py:100-156 |
| systemd unit | sensor_server.service |
| Weather API client | weather.py |
| Sensor drivers | aht10sense.py, si7021sense.py, mpl3115sense.py, pihatsense.py |
| Binary log save/load, Sense HAT detection | repository.py |
| Graph screen / options form (Sensors tab) | simplegraph.py / optionform.py |

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
9. **Every sensor read on every cycle.** Fixed in your commits: raspi_play and sensor_server now read only the enabled sensors, and only the Sense HAT or the AHT10/MPL3115 set, not both.

### Still open

1. **API keys and a password are public.** `weather.py:4,13,22` holds an OpenWeatherMap key, a Meteosource key and an account password in a comment, and `github.com/gkyrits/Python_test1` is public. Rotate both keys and change the password, then load keys from an untracked config file or environment variable. Removing them from the file does not remove them from git history.
2. **raspi_play won't start without Pmw.** `import optionform` (raspi_play.py:15) imports Pmw at startup, so a Pi without `python3-pmw` fails before the clock appears. Importing optionform inside `option_window()` (raspi_play.py:238) would limit the failure to key 2.
3. **Two readers of the same sensors.** raspi_play and sensor_server both poll I2C. The MPL3115 read is a multi-step sequence with 1 s pauses, so simultaneous reads could occasionally interleave and give a wrong value. The Sense HAT is less affected. On Windows both also call the weather site (two requests every 2 minutes, fine for the free plan).
4. **Duplicate keys in `icon_map_day`** (raspi_play.py:80): 600 and 612 appear more than once, so the last value (24) wins. Any code missing from the map (e.g. Meteosource `Id=0`) raises `KeyError` mid-update; `.get(id, default)` would avoid that.
5. **Graph only looks inside the current month's file** (repository.py:159), so shortly after the 1st of a month the 24 h graph is mostly empty.

### Found in the options/sensors commits (1-2 Oct)

6. **The graph hides or zeroes history using today's switches.** `load_info_binary()` (repository.py:196-208) decides from the *current* `SENSEx_EN` whether to return a sensor's values. Disabling a sensor hides all its earlier logged data too, and re-enabling it brings back the zeros saved while it was off. In the graph those zeros are plotted as real 0 °C / 0 % points (only pressure 0 is treated as missing, simplegraph.py:79). Returning the stored values as they are, and treating an all-zero sensor block as "no reading" (skip the point) in `parce_info()`, would fix both.
7. **The panel keeps showing a sensor that was just disabled.** If the sensor on screen is switched off in the options form, `sense_id` still points at it and every update redraws its last (no longer refreshed) reading, until the panel is tapped. After Ok, `option_window()` could call `sensePanel_nextShow()` when the current sensor is no longer enabled.
8. **A global keyboard grab can lock the screen.** `grab_keyboard()` uses `grab_set_global()`, which takes the whole X display (pointer too). If the options form ever fails to close (an exception in a callback), nothing else on the Pi gets input until raspi_play is killed. `grab_set()` (local grab) plus `focus_force()` may be enough for the frameless window; if not, release the grab explicitly in the Ok/Cancel handlers.
9. **Offsets can push humidity past 0-100 %.** A humidity offset is added without clamping, so the panel can show e.g. 103 %. The log is safe (`__byte` clamps to 0-255), but `simplegraph.parce_info()` drops a record whose web humidity is out of range, not the sensor's. Clamping to 0-100 in each driver would keep display and log consistent.

## Smaller improvements

- Offsets are baked into the logged values, so changing an offset later does not correct older records. That is fine as long as it is expected; a note in the form or the README would help.
- `options.save()` doesn't update `settings_mtime`, so the process that saved reloads its own file on the next sensor read. Harmless, one extra read.
- The MPL3115 altitude offset is independent of its pressure offset, while the Sense HAT altitude follows its corrected pressure. Two ways to calibrate the same thing; dropping `MPL3115_ALTIT_OFFSET` and recomputing would match the Sense HAT.
- `options.FULL_SCREEN = 1` also applies on Windows, where the window then has no title bar and can only be closed with key 3. `FULL_SCREEN = not sys.platform.startswith('win')` would keep a normal window for testing.
- In `simplegraph.canvas_click` (simplegraph.py:424) the "Please wait" popup stays open if `get_initdata()` raises; a `try/finally` would close it.
- Importing `repository` now opens the Sense HAT (via `pihatsense.exist()`), so every program that only reads the log, such as a standalone graph, also initialises the HAT. Harmless, but a lazy check would avoid it.
- Global `exit` in raspi_play.py shadows the built-in; a `threading.Event` (as in sensor_server.py) would also let threads stop immediately.
- The clock thread sleeps a fixed 1 s, so seconds occasionally skip; scheduling with `root.after` aligned to the next second would fix it.
- `repository.load_info()` uses `eval()` on file text (repository.py:148); `ast.literal_eval` is safer.
- `update_battery` (raspi_play.py:277) treats exactly 0 % as "no battery" and blanks the fields.
- `senseInfo_panel` (raspi_play.py:425) configures 6 grid rows but uses 7 for sensor 3.
- Debug `print`s fire on every hover and sensor update.
- `radio_play` (raspi_play.py:219) builds its path from `os.getcwd()` rather than `BASE_DIR`.
