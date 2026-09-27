# raspi_play.py review

Review of `weather_time/raspi_play.py` and the modules it imports. First written 2026-09-27 on branch `ai_work`; updated the same day for branch `claude_work` (commits 030da99, c0298fa, 0d23074).

## What it does

A Tkinter dashboard sized for a 320x240 Raspberry Pi LCD:

- **Top panel:** big clock (HH:MM + seconds) and date (day, weekday, month, year) in Greek or English (`lang`, default Greek).
- **Bottom-left panel:** tap to cycle between an IP/CPU/battery view (LAN and Wi-Fi IP, CPU usage and temperature, INA219 battery % and current) and room sensor views (SENSOR 1 = Sense HAT or AHT10 temperature/humidity, SENSOR 2 = SI7021, SENSOR 3 = Sense HAT or MPL3115 pressure/altitude).
- **Bottom-right panel:** current weather from OpenWeatherMap (description, temp, feels-like, humidity, pressure, wind, icon with a night variant). Tap it to swap to a 3-hourly forecast table for one day; tap the first/last icon to go back/forward a day; it returns to normal after 30 s.
- **Tap the clock:** opens the history graph (`simplegraph.py`) drawn from the binary log.
- **Side keys 1/2/3** (on-screen, or GPIO 18/23/24 when `register_keys()` is enabled): 1 = test popup, 2 = options form (`optionmenu.py`, placeholder tabs), 3 = exit.
- Polls the sensors every 60 s and the weather every 120 s for display, and pushes the web pressure into the barometer as sea-level reference. It works on its own; it no longer writes the repository.
- Disables the X screensaver/DPMS while running.

**sensor_server.py** (new) is a daemon that does the logging: it polls the weather site (120 s) and the sensors (60 s), sets the sea pressure, and appends a record to `weather_time/repository/sensor-YYYY-MM.bin`. It runs as a systemd service (`sensor_server.service`), stops cleanly on SIGTERM/Ctrl+C, and accepts `--sensor-period`, `--weather-period` and `--once`.

Install on the Pi (in `/home/gkyr/Work/Python_test1/weather_time`):

```
sudo cp sensor_server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now sensor_server
journalctl -u sensor_server -f
```

## Structure

| Piece | Where |
|---|---|
| Helpers: month/weekday names, wind direction, forecast day split | raspi_play.py:54-106 |
| `Gui` class: panels, click handlers, update_* setters, `post()` queue to the Tk thread | raspi_play.py:108-783 |
| Clock thread (1 s) | raspi_play.py:786-806 |
| Weather thread (120 s) | raspi_play.py:809-850 |
| Sensor thread (60 s) + sea-pressure sync, display only | raspi_play.py:853-931 |
| CPU/IP/battery thread (5 s) | raspi_play.py:934-971 |
| Main: start threads, mainloop, cleanup | raspi_play.py:1006-1041 |
| Logging daemon | sensor_server.py, sensor_server.service |
| Weather API client | weather.py |
| Sensor drivers | aht10sense.py, si7021sense.py, mpl3115sense.py, pihatsense.py |
| Binary log save/load | repository.py |
| Graph screen / options screen | simplegraph.py / optionmenu.py |

All worker threads hand GUI updates to `Gui.post()`; the Tk main loop runs them every 100 ms.

## Bugs

### Fixed on claude_work

1. **Tkinter touched from background threads.** Workers and GPIO key callbacks now go through a queue polled by `root.after`; the info popup timeout uses `root.after` instead of `threading.Timer`.
2. **Wind direction East/West swapped.** Now correct, in Greek (Β, ΒΑ, Α, ΝΑ, Ν, ΝΔ, Δ, ΒΔ) or English with `lang=EN`.
3. **Forecast hours in UTC.** weather.py now uses the epoch `dt` in local time. Days are grouped by date (last slot no longer dropped), Today/Tomorrow comes from the real date, and paging is clamped to the days available.
4. **Sense HAT all zeros when the first weather call failed.** Sea pressure is only taken from a successful reading; pihatsense.py falls back to 1013.25 hPa if it gets 0.
5. **No network timeouts, forecast fetched on the GUI thread.** Requests time out after 10 s; the forecast is fetched in a background thread so the clock keeps running.
6. **`repository/` path depended on the working directory.** It is now always `weather_time/repository`, and a `.gitignore` keeps the data out of git. Old logs written elsewhere (e.g. `Python_test1/repository/`) must be moved there for the graph to show them.

### Still open

1. **API keys and a password are public.** `weather.py:4,13,22` holds an OpenWeatherMap key, a Meteosource key and an account password in a comment, and `github.com/gkyrits/Python_test1` is public. Rotate both keys and change the password, then load keys from an untracked config file or environment variable. Removing them from the file does not remove them from git history.
2. **Two processes read the same sensors.** raspi_play and sensor_server both poll I2C. The MPL3115 read is a multi-step sequence with 1 s pauses, so simultaneous reads could occasionally interleave and give a wrong value. The Sense HAT is less affected.
3. **Duplicate keys in `icon_map_day`** (raspi_play.py:81): 600 and 612 appear more than once, so the last value (24) wins. Any code missing from the map (e.g. Meteosource `Id=0`) raises `KeyError` mid-update; `.get(id, default)` would avoid that.
4. **Graph only looks inside the current month's file** (repository.py:149), so shortly after the 1st of a month the 24 h graph is mostly empty. `simplegraph.draw_form` also has a deliberate `tm.sleep(1)` on the GUI thread (simplegraph.py:495).

## Smaller improvements

- `register_keys()` is commented out (raspi_play.py:1010), so the physical GPIO buttons do nothing on the Pi. A platform check would let it stay on.
- `USE_PI_SENSE_HAT` now lives only in repository.py (still a TODO to auto-detect).
- Sensor polling reads all four sensors every cycle even though only the Sense HAT is in use; the MPL3115 path alone sleeps 2 s.
- `SenseHat()` is constructed on every read; create it once.
- Global `exit` in raspi_play.py shadows the built-in; a `threading.Event` (as in sensor_server.py) would also let threads stop immediately.
- The clock thread sleeps a fixed 1 s, so seconds occasionally skip; scheduling with `root.after` aligned to the next second would fix it.
- `repository.load_info()` uses `eval()` on file text (repository.py:141); `ast.literal_eval` is safer.
- `update_battery` (raspi_play.py:299) treats exactly 0 % as "no battery" and blanks the fields.
- `senseInfo_panel` (raspi_play.py:447) configures 6 grid rows but uses 7 for sensor 3.
- Debug `print`s fire on every hover and sensor update.
- `radio_play` (raspi_play.py:239) builds its path from `os.getcwd()` rather than `BASE_DIR`.
