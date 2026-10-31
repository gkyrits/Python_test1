# Review: `camplay_gui.py` and its modules

Reviewed at commit `aeda4db` (branch `camera`) on 2026-10-31.

## Structure

| File | Lines | Contents |
|---|---|---|
| `camplay_gui.py` | 185 | Entry point. `main_win`: list of cameras, Update, camera combobox, Open. With one camera it opens its `camera_win` directly as the main window |
| `camwork.py` | 885 | `camera_win` (one per camera: Info menu, Snap, PreView, QTView, Options, H/V rot, Foto, Video, Start Rec, Start Web; UDP and TCP image streaming on port 8000), `full_screen_view` (double-click on the preview), `import_special_libs()`, `picamera2_inst` (4 slots) |
| `camoptions.py` | 411 | `options_win` (modal options form), `update_options()` |
| `genutils.py` | 117 | `d_print` (pretty print of dicts/lists), file names with date/time, `info_win` (Properties / Sensor Modes) |
| `webutils.py` | 118 | MJPEG streaming web server (port 8000) |
| `sockutils.py` | 147 | TCP image transfer: `send_dict` / `recv_dict`, `make_pil_image` |
| `cam_client.py` | 177 | TCP client GUI |
| `picamera2_sim/` | | Picamera2 simulator for Windows, used when `picamera2` can't be imported |
| `camplay` | | Pi launcher script: `cd` to the folder and run `camplay_gui.py` |

**How windows are tracked:** `main_win.cam_inst` holds one `camera_win` per combobox position (4 slots). When a camera window closes, `camera_win` calls its `on_close(idx)` callback, and `main_win` clears that slot. If a slot still holds a window that no longer exists, Open clears it too.

## Bugs

### Fixed on `camera`

`1e2bf99`:
1. **Off-by-one in the "too many cameras" check.** `cbxIdx > len(self.cam_inst)` let index 4 through, which crashed with `IndexError`. Now `>=`.
2. **Close cleanup never ran.** `camplay_gui.py` runs as `__main__`, so `camwork`'s `import camplay_gui as gui` loaded a second copy of the module, where `gui.mainWin` was always `None`. `camera_win` now takes an `on_close` callback, and the circular import is gone.
3. **Update with no cameras crashed** on `cbx_entries[0]`. The combobox is now cleared instead. Open with nothing selected returns with "No camera selected" instead of crashing on `curselection()[0]`.
4. **`cam_inst` was a class attribute**, one list shared by every instance. Now created in `__init__`.

`a16377f`:

5. **The close handler ran ~18 times per window close.** `<Destroy>` is bound on the camera window, and Tk sends it for every child widget too. `__close_win` now returns unless `e.widget is self.win`.

`2467609`:

6. **Start Web after Stop Web failed with `OSError: [Errno 98] Address already in use`.** `stop()` of `pageServer` and `simpleServer` only called `shutdown()`, which ends `serve_forever` but leaves the listening socket open on port 8000. Both now call `server_close()` too. `simpleServer` uses `ReuseTCPServer` (`allow_reuse_address`, as `StreamingServer` already had), and the server threads are daemon threads.

`aeda4db`:

7. **Browsers froze after Stop Web, and handler threads leaked.** The `/stream.mjpg` handler waited for the next frame with no way out, so after Stop a watching browser stayed connected on the last frame, and one thread was left per Start/Stop cycle. `StreamingOutput.end()` sets `stopped` and wakes the handlers. `pageServer.stop()` calls it first, and the handlers then close their clients. Each handler now uses the output it started with, not the global `outStream` that the next Start replaces.

### Still open

- **A failed Start Web leaves the camera recording.** `start_webPage` starts recording before starting the web server (`start_ffmpeg_stream` does the same). If the server fails to start, recording keeps running with no server, `stream_type` is not set and the button stays "Start Web". Starting the server first, or stopping the recording on error, would fix it.
- **Stale slots after Update.** `cam_inst` is keyed by the combobox position. If Update returns the cameras in a different order, an open window stays in the slot of its old position. Keying by `Num` (or the camera ID) would be safer.
- **Cameras are stopped, never closed.** Closing a window calls `picam.stop()` but not `close()`, and the instance stays in `picamera2_inst` for reuse, so the camera stays open until the program exits.

## Smaller improvements

- The single-camera path passes `cam_num=0` instead of `camera_info[0]['Num']` as the multi-camera path does. It works, since the only camera is number 0.
- Dead code in `camplay_gui.py`: `__add_text_frame` (never called, which also makes the `tk.Text` branch of `__update_btn` unreachable), `test_print` (only in a commented-out line), and the module-level `global` statements.
- `genutils.py` imports `camwork` (for `camera_win.INFO_*_ID`) while `camwork` imports `genutils`. It works because the names are only used inside methods, but moving the two IDs into `genutils` would remove the cycle.
- Typo "aleary" in `__open_btn`.

## Checked and correct

Tested on Windows with `picamera2_sim`, driving the GUI from a script:

| Case | Result |
|---|---|
| Open the 5th camera (index 4) | "Too many cameras", no slot used |
| Open camera 0, close it | `on_close` called once, slot back to `None` |
| Open camera 0 again | Opens normally |
| Update with no cameras | Combobox empty, nothing selected |
| Open with nothing selected | "No camera selected" |
| Single camera (`root=True`) window closed | Handler runs once, `picam` is `None` |

Web page server (`webutils.py`), with clients connected to `/stream.mjpg`:

| Case | Result |
|---|---|
| Stop, then bind port 8000 without `SO_REUSEADDR` | Port free (before the fix: still in use) |
| 3 Start/Stop cycles, a client with a frame and one still waiting for its first | Both clients closed each cycle, Stop takes 0.1 s |
| A client receiving frames when Stop is pressed | Closed |
| Threads left after all cycles | 0 (before the fix: one per cycle) |

Windows lets a `SO_REUSEADDR` socket bind over a port that is still listening, so a plain Start/Stop/Start loop passes there even with the old code; Linux doesn't. That's why the port test binds without `SO_REUSEADDR`.

- `server_close()` doesn't wait for the stream handler threads: `StreamingServer` has `daemon_threads = True`, and `ThreadingMixIn` only joins non-daemon threads. So Stop can't hang on a connected browser.

- The Pmw combobox list is created with `exportselection=0`, so selecting text in the info box doesn't clear the camera selection.
- `selectitem('')` raises `IndexError` in Pmw when `''` isn't in the list, which is why the empty case clears the entry field instead.
