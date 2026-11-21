# sock_test review

Review of `sock_test/` (a Tkinter TCP client/server pair). Written 2026-11-21 on branch `develop` at commit c1d7019 (image index/delete, per-byte key decode, socket close races, port validation).

## What it does

Two small Tkinter apps (350x500 windows) that talk over one TCP connection:

- **Server (`server_app.py`):** enter a port and press **Start** to listen (all interfaces, one client at a time). Port 8000 by default.
  - **Keys tab:** labels laid out like a remote (Up/Left/Center/Right/Down and Key 1-5). Each key code the client sends lights its label red for 300 ms (`KEY_TIME`).
  - **Fotos tab:** **Path** picks a folder; its file list is loaded and the path is saved to `sock_test/server.opt` (listed in `sock_test/.gitignore`, which isn't committed yet) and loaded again at start. **Next** shows the next file stretched to the canvas, with a "N of M files" counter. **Delete** asks for confirmation and removes the current file from the list only (the file on disk stays).
- **Client (`client_app.py`):** enter the server IP (127.0.0.1 by default) and port and press **Connect**.
  - **Keys tab:** buttons for the same keys; each click sends one key code.
  - **Fotos tab:** **Load** opens an image from disk and shows it on the canvas. **Send** and the progress bar are placeholders (no command yet).
- Socket errors show a message box in the client; the button text follows the connection state (Connect/Disconnect, Start/Stop).

## Protocol

One byte per key press, client to server. Codes are in `socketwork.py`:

| Code | Key | Code | Key |
|---|---|---|---|
| 0x01 | Up | 0x06 | Key 1 |
| 0x02 | Down | 0x07 | Key 2 |
| 0x03 | Left | 0x08 | Key 3 |
| 0x04 | Right | 0x09 | Key 4 |
| 0x05 | Center (Enter) | 0x0A | Key 5 |

There is no framing: the server reads whatever bytes arrived and handles each one. Bytes outside 0x01-0x0A are ignored. The server never sends anything back; the client only prints what it receives.

## Structure

- **`socketwork.py`:** key codes, `parse_port()` (1-65535 or None), and two socket wrappers.
  - **`ServerSock`:** `start(port)` binds a listener (0.5 s accept timeout so `stop()` is noticed) and starts the accept thread. The accept thread serves one client at a time in `_client_worker`, then goes back to accept. Callbacks: `on_key_received(code)`, `on_connect(addr)`, `on_disconnect()`, `on_error(e)`. `stop()` shuts the client socket down, closes the listener and joins the accept thread (1 s timeout).
  - **`ClientSock`:** `connect(host, port)` (blocking) starts a receive thread bound to that socket. `send(data)` closes the connection if sending fails. `close()` takes the socket under a lock before shutting it down, so `on_disconnect` fires once whichever thread closes first; the receive thread only closes its own socket, so a late exit can't close a newer connection. Callbacks: `on_disconnect()`, `on_error(e)`.
- **Threading:** socket callbacks run on worker threads. Both apps pass them to the Tk main thread with `root.after(0, ...)` instead of touching widgets directly.
- **`server_app.py` / `client_app.py`:** the windows. Both share the same layout (top IP/port frame, notebook with Keys and Fotos tabs, bottom button) and the `alt` ttk theme for coloured tabs.

## Running

Start the server first, press Start, then start the client and press Connect:

```powershell
python sock_test\server_app.py
```

```powershell
python sock_test\client_app.py
```

Needs Pillow (`PIL.Image`, `PIL.ImageTk`) for the Fotos tabs.

## Bugs

### Fixed in c1d7019

1. **Next skipped the first image.** The index started at 0 and was increased before showing, so file 0 only appeared after wrapping. It now starts at -1 (nothing shown), and the counter is 1-based.
2. **Delete removed the wrong file.** Right after loading a folder it deleted a file never shown, and after a delete it skipped the file that moved into the current slot. It now ignores Delete until an image is shown, then shows the file in the same slot (wrapping to the first).
3. **Key presses could be lost.** TCP can join several presses into one `recv`, and only the first byte was read. Every byte is handled now, and 0x00 is rejected.
4. **A failed send left the client half-connected.** The button said Connect but the socket was still open, so the next click disconnected. `send()` now closes the connection and the disconnect event resets the button.
5. **Close races.** In the client, the receive thread could close at the same time as the GUI, firing `on_disconnect` twice and freezing the GUI for up to 1 s in `join`. In the server, `stop()` could hit an `AttributeError` when the worker cleared `client_sock`. Both now work on a local copy taken first (the client under a lock).
6. **Bad port input.** Text that isn't a number raised an uncaught `ValueError`; a port above 65535 leaked the server's listener. Both apps now check the port and show an error.

### Still open

1. **Race in `ClientSock.send()`** (`socketwork.py`). It checks `self.sock` and then uses it; if the server drops the connection at that moment, the receive thread can set it to None in between, and the user sees a "'NoneType' object has no attribute 'sendall'" error. A local copy fixes it.
2. **Delete asks before checking.** Before any image is shown, Delete still asks "Are you sure…?" and then does nothing; the check should come before the dialog.
3. **Connect blocks the GUI.** `ClientSock.connect()` runs on the Tk thread; an unreachable host freezes the window for about 20 s on Windows.
4. **Tight error loop.** If `accept()` keeps failing with anything other than a timeout, the accept thread calls `on_error` in a loop. If `stop()`'s 1 s join ever times out and Start is pressed again, the old thread keeps running against the closed listener.
5. **No close-window handler.** Neither app sets `WM_DELETE_WINDOW`, so sockets aren't stopped when the window closes, and a key arriving after the window is gone raises an error in the worker thread.

## Smaller improvements

- `server_app.py` defines `load_next_image` twice; the first copy (a file dialog) is dead code, overridden by the second.
- `filedialog.askopenfile` opens a file handle that is never closed; `askopenfilename` is enough. `Image.open` isn't closed either and can keep the file locked on Windows.
- The folder list includes subfolders and non-image files (the filter in `update_path_info` is commented out).
- Images are stretched to the canvas without keeping the aspect ratio; before the Fotos tab is drawn, `winfo_width()` can be 1.
- The empty-list labels differ: "No file selected" after deleting every file, "0 of N files" after loading a folder.
- `from tkinter import Image` is overwritten by `PIL.Image` in both apps; drop it. `self.tkimg` would be clearer than `global tkimg`.
- `key_received` has ten near-identical branches; a `{code: label}` dict would replace them. Fast repeat presses clear the highlight early because the earlier timer still fires, and the reset colour `gray90` doesn't match the default label background on Windows.
- `sock_test/.gitignore` only ignores `/server.opt`; adding `__pycache__/` would stop it showing as untracked.
