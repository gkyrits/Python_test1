# Review: `camplay_gui.py` and its modules

Reviewed at commit `b1419a8` (branch `camera`) on 2026-10-31: all files in `camera/`.

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

Numbered on from the fixes. ✔ = reproduced with the simulator; the others are from reading the code, since the simulator can't record, stream or serve TCP.

**Serious**

8. **TCP SERVER runs code from the network.** Requests are read with `pickle.loads` (`sockutils.recv_dict`, called from `__parse_tcp_cmds_4`), so anyone who can reach port 8000 while this mode is on can run any command on the Pi. Sending the commands as JSON would fix it; only the image data needs to be binary.
9. ✔ **After Update, Open can start the wrong camera.** `picamera2_inst` is keyed by the list position and reused without checking `Num` (`__initialize_Camera`). In the test, the window for camera Num 1 got the Picamera2 of camera Num 2, left in that slot before Update.
10. ✔ **With the default options, every file is `foto.jpg`.** The default `path` is `""`, and `get_filename` then returns `"foto.jpg"`, for videos too. Each capture overwrites the previous one.

**Camera state**

11. **Modes don't block each other.** Start Web, Video, Foto and H/V rot all stop and reconfigure the camera even while Start Rec is recording. Stop Web calls `stop_recording()`, which in Picamera2 stops all encoders, so it probably ends the Rec recording too while the button still shows "Stop Rec".
12. **A failed start leaves the camera recording.** `start_webPage` and `start_ffmpeg_stream` start recording before the web server; if the server fails to start, recording keeps running with no server, `stream_type` is not set and the button stays "Start Web". `start_video` switches the button to "Stop Rec" before the setup that can fail.
13. **Closing a window while recording or streaming leaves things running.** `__close_win` only calls `picam.stop()`. The mp4 is never finished (probably unplayable). In TCP mode, the server thread (not a daemon thread) stays blocked in `accept()`, which keeps the program alive after its windows close, still holding port 8000.
14. **Video freezes the GUI for the whole clip** (10 s by default): `tm.sleep(duration)` runs on the Tk thread in every `snap_*_video`.

**Smaller**

15. ✔ **Raw or unknown formats crash with `NameError: name 'formats' is not defined`** in `sockutils._make_array_shared`, instead of the intended "Format not supported".
16. **A non-number in Options → Duration or Audio Sync makes Ok fail silently.** `_save_options` raises `TclError`; nothing is saved and the window stays open with no message.
17. **UDP targets are hard-coded and differ:** UDP sends to `192.168.2.5`, FFMPEG UDP to `192.168.2.2`.
18. **HLS/DASH share the whole working folder.** `simpleServer` uses `SimpleHTTPRequestHandler`, which serves the current directory, so the source files and `cam_options.json` can be listed and downloaded.
19. **YUYV conversion ignores the stride** (`make_pil_image` reshapes to `(height, width, 2)`). It will fail when rows are padded. Likely, not yet seen.
20. **"Auto Number" does nothing:** `fname_incnum` is saved but never used.
21. **Stale slots after Update.** `cam_inst` is keyed by the combobox position. If Update returns the cameras in a different order, an open window stays in the slot of its old position. Keying by `Num` (or the camera ID) would be safer. Related to 9.
22. **Cameras are stopped, never closed.** Closing a window calls `picam.stop()` but not `close()`, and the instance stays in `picamera2_inst` for reuse, so the camera stays open until the program exits.

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

- Closing a camera window while PreView is on doesn't crash the preview loop: the loop is scheduled with `self.win.after`, and Tk drops the pending callback when the window is destroyed.
- The Pmw combobox list is created with `exportselection=0`, so selecting text in the info box doesn't clear the camera selection.
- `selectitem('')` raises `IndexError` in Pmw when `''` isn't in the list, which is why the empty case clears the entry field instead.
