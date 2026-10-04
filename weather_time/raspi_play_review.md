# raspi_play.py review

Review of `weather_time/raspi_play.py` and the modules it uses. First written 2026-09-27 on branch `ai_work`; last updated 2026-10-04 for branch `claude_work` at commit 548e55c (Options tab with language and weather locations, settings applied without restart, place in the weather panel).

## What it does

A Tkinter dashboard sized for a 320x240 Raspberry Pi LCD:

- **Top panel:** big clock (HH:MM + seconds) and date (day, weekday, month, year) in Greek or English.
- **Bottom-left panel:** tap to cycle through the enabled room sensor views (SENSOR 1 = Sense HAT or AHT10 temperature/humidity, SENSOR 2 = SI7021, SENSOR 3 = Sense HAT or MPL3115 pressure/altitude) and the IP/CPU/battery view (LAN and Wi-Fi IP, CPU usage and temperature, INA219 battery % and current). Disabled sensors are skipped.
- **Bottom-right panel:** current weather from OpenWeatherMap for the selected location (description, temp, place name under it, feels-like, humidity, pressure, wind, icon with a night variant). Tap it to swap to a 3-hourly forecast table for one day; tap the first/last icon to go back/forward a day; it returns to normal after 30 s.
- **Tap the clock:** opens the history graph (`simplegraph.py`) drawn from the binary log (also from the previous month's file when the time range starts there), with a "Wait Load Graph" message while it loads. A sensor with no reading (disabled or failed, logged as zeros) repeats its previous value instead of plotting 0.
- **Keys 1/2/3** (on-screen, and GPIO 18/23/24 on the Pi): 1 = test popup, 2 = options form (`optionform.py`, needs Pmw, imported only when the form opens), 3 = exit. The form has two working tabs, each in groove frames with 7 pt fonts:
  - **Sensors:** an Enable frame (S1/S2/S3 switches) and an Offset frame (a calibration offset per sensor value).
  - **Options:** a Language frame (EN/GR checkbuttons, one choice) and a Location frame (combobox of saved locations, Name/Lat/Lon entries, Add and Del). Add with a new name creates a location; with an existing name (case ignored) it only updates that location's lat/lon. Del keeps at least one.
  - Ok checks every value in all tabs first (bad ones turn pink, the form stays open and nothing changes), then stores all tabs and saves `options.json` once. Ok and Cancel release the keyboard grab before closing. The third tab is still a placeholder.
  - **Applied without restart** (`Gui.options_changed()`): a disabled sensor on screen moves to the next one; a new language relabels the weather and sensor panels (month/weekday on the next clock tick, the forecast table when next shown); a new language or location makes the weather thread fetch at once (`wthr_refresh`).
- Polls the sensors every 60 s and the weather every 120 s for display, and pushes the web pressure into the barometer as sea-level reference. It works on its own; it does not write the repository.
- **On Windows** (no daemon) it also runs `sensor_server` in a background thread so the repository is still updated, and stops it on exit.
- Disables the X screensaver/DPMS while running.

**Settings** shared by the screens live in `options.py`: `LCD_SIZE`, `FULL_SCREEN` (1 on the Pi, 0 on Windows for a normal window), `LANG` (EN/GR), the weather `locations` (`{id: {name, lat, lon}}`) with the selected `LOCATION` and `get_location()`, the `SENSE1/2/3_EN` switches and the per-sensor offsets, plus `center_form()`, `wait_msg()`, `full_screen()` (frameless window) and `grab_keyboard()` (a frameless window gets no keys from the window manager on the Pi, so the options form grabs the keyboard while open).

**Saved settings:** the language, the locations and the selected one, the enable switches and the offsets are saved to `weather_time/options.json` (git-ignored, written via a temp file) and loaded at import. raspi_play and sensor_server call `opt.reload_if_changed()` before each sensor read, so a change made in the form reaches sensor_server within one sensor period. JSON keeps the location ids as strings; `load()` turns them back into ints and checks every location. weather.py reads the selected location on every request (`get_weather_info()`/`get_forecast_info()` with no lat/lon), and sends `LANG` as the OpenWeatherMap language. Offsets are added inside each sensor driver, so they are already in the logged values; for the Sense HAT the altitude is computed from the corrected pressure. Humidity is clamped to 0-100 % after the offset.

**Disabled sensors** are not read, not shown and saved as zeros (the record layout stays fixed). `load_info_binary()` returns the stored values whatever the current switches, and the graph treats an all-zero sensor block as no reading. The graph hides the T/H buttons when sensor 1 is off and P when sensor 3 is off.

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
| `Gui` class: panels, click handlers, update_* setters, `post()` queue to the Tk thread, `options_changed()` | raspi_play.py:108-792 |
| Clock thread (1 s) | raspi_play.py:794-815 |
| Weather thread (120 s) | raspi_play.py:817-857 |
| Sensor thread (60 s), enabled sensors only, + sea-pressure sync, display only | raspi_play.py:859-948 |
| CPU/IP/battery thread (5 s) | raspi_play.py:950-988 |
| GPIO keys | raspi_play.py:994-1008 |
| Main: start threads (plus sensor_server thread on Windows), mainloop, cleanup | raspi_play.py:1023-1067 |
| Shared settings, locations + `get_location()`, options.json save/load, popups, full screen, keyboard grab | options.py |
| Logging: weather poll + web log, enabled sensors, poll loop | sensor_server.py:33-97 |
| Menu (exit / graph) and startup options | sensor_server.py:100-156 |
| systemd unit | sensor_server.service |
| Weather API client | weather.py |
| Sensor drivers | aht10sense.py, si7021sense.py, mpl3115sense.py, pihatsense.py |
| Binary log save/load (across month files), Sense HAT detection | repository.py |
| Graph screen / options form (Sensors and Options tabs) | simplegraph.py / optionform.py |

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
10. **raspi_play wouldn't start without Pmw.** `optionform` is now imported inside `option_window()`; without Pmw only key 2 fails.
11. **Duplicate keys in `icon_map_day`, `KeyError` on unknown ids.** Dead duplicates removed (600 and 612 still show icon 24); an unknown id (e.g. Meteosource `Id=0`) shows icon 13.
12. **Graph only read the current month's file.** `load_info_binary()` also reads earlier month files the time range reaches, so the 24 h graph is full on the 1st.
13. **Graph hid or zeroed history using today's switches.** Stored values are returned as they are; `parce_info()` treats an all-zero sensor block (and pressure 0) as no reading and `fill_missing()` repeats the previous value.
14. **Panel kept showing a sensor that was just disabled.** Closing the options form checks the shown sensor and moves to the next one.
15. **A global keyboard grab could lock the screen.** Ok and Cancel release the grab before closing, and Ok closes the form even if applying fails. The grab is still global (needed for the frameless window on the Pi).
16. **Offsets could push humidity past 0-100 %.** Clamped in the AHT10, SI7021 and Sense HAT drivers.
17. **Smaller items.** `FULL_SCREEN` is 0 on Windows; `options.save()` updates `settings_mtime`; the graph's "Please wait" popup closes on error (`try/finally`); `load_info()` uses `ast.literal_eval`; `radio_play` uses `BASE_DIR`; `senseInfo_panel` configures all the grid rows it uses.

18. **Meteosource used the fixed location.** `get_meteo_weather_info()` wrote lat/lon into `open_param`; it now sets `meteo_param`.
19. **JSON turned location ids into strings.** `options.load()` makes them ints again, so `locations[LOCATION]` still works after a reload.
20. **Cancel after a failed Ok kept half the changes.** Each tab's check now returns a store function (or None if a value is wrong) and changes nothing; Ok stores the tabs only when all are valid, so Cancel leaves `options` as it was.

### Still open

1. **API keys and a password are public.** `weather.py:5,19,29` holds an OpenWeatherMap key, a Meteosource key and an account password in a comment, and `github.com/gkyrits/Python_test1` is public. Rotate both keys and change the password, then load keys from an untracked config file or environment variable. Removing them from the file does not remove them from git history.
2. **Two readers of the same sensors.** raspi_play and sensor_server both poll I2C. The MPL3115 read is a multi-step sequence with 1 s pauses, so simultaneous reads could occasionally interleave and give a wrong value. The Sense HAT is less affected. On Windows both also call the weather site (two requests every 2 minutes, fine for the free plan).

## Smaller improvements

- Editing a location's name to the name of another one (instead of using Add) gives two locations with the same name in the combobox.
- A long place name in the weather panel (row 2, `columnspan=2`) widens the first two grid columns and pushes the icon right. Truncating the text (or a fixed `width`) would keep the layout.
- The location combobox drop-down opens while the options form holds a global keyboard grab. ttk restores the form's grab when the drop-down closes, so it should be fine, but it is worth checking on the Pi.

- Offsets are baked into the logged values, so changing an offset later does not correct older records. That is fine as long as it is expected; a note in the form or the README would help.
- The MPL3115 altitude offset is independent of its pressure offset, while the Sense HAT altitude follows its corrected pressure. Two ways to calibrate the same thing; dropping `MPL3115_ALTIT_OFFSET` and recomputing would match the Sense HAT.
- Importing `repository` now opens the Sense HAT (via `pihatsense.exist()`), so every program that only reads the log, such as a standalone graph, also initialises the HAT. Harmless, but a lazy check would avoid it.
- Global `exit` in raspi_play.py shadows the built-in; a `threading.Event` (as in sensor_server.py) would also let threads stop immediately.
- The clock thread sleeps a fixed 1 s, so seconds occasionally skip; scheduling with `root.after` aligned to the next second would fix it.
- `update_battery` (raspi_play.py:292) treats exactly 0 % as "no battery" and blanks the fields.
- Debug `print`s fire on every hover and sensor update.
