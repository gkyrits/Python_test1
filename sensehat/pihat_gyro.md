# Review: `pihat_gyro.py` and its modules

Reviewed at commit `f681d22` (branch `sense_gyro_test`) on 2026-10-27. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 657 | Tk app with 6 tabs, Sense HAT reading, per-tab sensor setup, orientation maths |
| `pi3d_gyro.py` | 278 | 3D scene (pi3d): Windows setup, off-screen framebuffer, gimbal rotation. Interface `GyroScene` |
| `compass.py` | 125 | `raw_heading`, `xy_angle`, `HardIronCalibration`, `CompassView` (compass drawing) |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 86 | `gravity_vector`, `remove_gravity`, `ResidualCorrection` (Zero / Auto-zero) |
| `track.py` | 259 | `level_acceleration`, `Tracker` (integration with ZUPT), `TrackSampler` (thread), `TrackView` |

**Tabs:**
- **Gyroscope:** 3D shape following the orientation, with C/R calibration.
- **Compass:** north from the raw XY or `get_compass()`, with H hard-iron calibration and an offset slider.
- **Magnetometer:** X/Y/Z arrows and |B|, with a warning near a magnet.
- **Accelerometer:** Raw or Linear (gravity removed), with Zero / Auto-zero and an axis range choice.
- **Track:** speed and track from the linear acceleration, with ZUPT, in board axes or north-up.

Each tab turns on only the sensors it needs (`set_imu_config`), and reads only while it's showing.

## Issues

### Medium

1. **Track accuracy is limited by the method**
   Double integration of the acceleration drifts: an error of 0.01 g gives ~5 cm in 1 s and ~1.2 m in 5 s. ZUPT keeps the error to a few cm per move, but only with stops in between. Improvements:
   - **Software:** one RTIMULib read per sample instead of three (see item 2), and a Kalman filter with ZUPT that also estimates the offset.
   - **Hardware:** an extra sensor without drift: a USB optical mouse or an optical-flow sensor for a table, wheel encoders for a robot, or camera + ArUco markers for an absolute position in mm.

2. **Three separate sensor reads per Track sample** ([pihat_gyro.py:518](pihat_gyro.py:518))
   `get_orientation()`, `get_accelerometer_raw()` and `get_gyroscope_raw()` each make their own `IMURead()`. That's slower (about 60 Hz in the test, target 100 Hz), and the three values don't come from the same instant. Using RTIMULib directly (`IMURead()` once, then `getIMUData()`) gives everything from one read.

3. **Bold titles still use `"TkDefaultFont 9 bold"`** ([pihat_gyro.py:130](pihat_gyro.py:130), [171](pihat_gyro.py:171), [246](pihat_gyro.py:246), [258](pihat_gyro.py:258), [285](pihat_gyro.py:285), [441](pihat_gyro.py:441), [463](pihat_gyro.py:463))
   This is read as a font *family* called "TkDefaultFont" at size 9, so on the Pi the 7 section titles may come out a different size from the other labels. The fix is already in the code: `self.bold_font` (the default font in bold) is used for the |B| warning. The titles should use it too.

4. **Moving a Gyroscope slider by hand behaves differently with a Sense HAT**
   The sliders are a rotation applied before the sensor's. Moving one slider can also change the other two angles. C and R work exactly.

5. **Gyroscope info labels may be cut off on the Pi** ([pihat_gyro.py:152](pihat_gyro.py:152))
   `width=12` stays fixed, but `Pitch (Y): -123.4°` is 18 characters. The other tabs' info labels no longer have a fixed width.

6. **ANGLE licence file is missing** (`sensehat/pi3d/`)
   The committed DLLs are BSD-licensed ANGLE builds, and the repo is public. Add the licence file next to them.

### Low

7. **An error stops the Tk loops for good** ([pihat_gyro.py:368](pihat_gyro.py:368), [376](pihat_gyro.py:376), [571](pihat_gyro.py:571), [582](pihat_gyro.py:582))
   An I2C error inside `render_loop`, `compass_loop`, `magnet_loop` or `accel_loop` ends that loop's `after()` chain, and the tab freezes. The Track thread already does this properly: it catches the error, stops, and shows a message.

8. **The Track path grows without limit** ([track.py:121](track.py:121))
   A new point is added every 2 mm, and the whole path is copied and redrawn every 50 ms. That's fine for tens of metres, but if it's left running and drifting for a long time, the redraw slows down. A limit, e.g. the last 5,000 points, would solve it.

9. **H recording and Track can run together**
   If you start H on the Compass tab and then press Start on the Track tab, the Track thread updates the min/max through `_read_magnet()` while the Tk thread can stop recording (`stop()`). It's a theoretical conflict between two threads; a lock in `HardIronCalibration` would remove it.

10. **The orientation needs to settle after switching tabs**
    The Compass, Magnetometer and Accelerometer (Raw) tabs turn off some sensors. When you go back to Gyroscope or Track, the orientation needs a moment. Pressing C or Start right away measures before it has settled.

11. **The |B| warning uses the corrected value**
    The field the sensor actually sees is the uncorrected one. The difference is the hard-iron offset (a few tens of µT on your board).

12. **No error handling when saving the hard-iron calibration** ([compass.py:84](compass.py:84))
    If the folder isn't writable, saving fails without any message in the window.

13. **No check that the framebuffer is complete** ([pi3d_gyro.py:67-89](pi3d_gyro.py:67))
    If a driver rejects it, the 3D view goes silently black. Check `glCheckFramebufferStatus` after the attachments.

14. **A new image every frame** ([pihat_gyro.py:650](pihat_gyro.py:650))
    `self.tk_image.paste(...)` would reuse the existing `PhotoImage` when the size hasn't changed.

15. **Leftovers**
    - [pihat_gyro.py:97](pihat_gyro.py:97): the comment `# Κενό (προς το παρόν) tab` is above the Accelerometer tab, which is no longer empty.
    - `M` ([line 115](pihat_gyro.py:115)) and `S` ([line 217](pihat_gyro.py:217)) have no command.
    - The class `Transparent3DCubeApp` now holds the whole multi-tab app; something like `SenseHatApp` would fit better.
    - `self.sense.clear()` ([line 73](pihat_gyro.py:73)) isn't needed.
    - The `Raw XY heading` label shows the angle `atan2(Y, X)`, not North.
    - Unneeded off-screen window move at [pi3d_gyro.py:122](pi3d_gyro.py:122).
    - `pihat_gyro_hardiron.json` (written on the Pi) and `pi3d_windll-master.zip` aren't in `.gitignore`.

## Checked and correct

- **Module split:** each module has a small interface documented at the top. The 3D library can be swapped by changing `import pi3d_gyro as gyro3d`. Compass, X/Y/Z graphs, gravity removal and track are separate from the Tk layout.
- **Orientation maths:** `euler_to_matrix` / `matrix_to_euler` follow RTIMULib's convention (Z-Y-X). Converting to a rotation and back returns the same angles, with an error below 10⁻¹³°. Calibration is stored as a rotation, so later movements are exact even at a tilt.
- **Gravity removal:** `gravity_vector` agrees with RTIMULib's tilt formula (`roll = atan2(y, z)`, `pitch = atan2(−x, √(y²+z²))`). At rest the result is 0 at any tilt (tested at 2,000 random tilts, also with the 0…360 form of the angles).
- **Zero / Auto-zero:** after Zero, a still board reads < 0.001 g. Auto-zero removes a constant leftover and lets a 0.2 g push through almost fully (0.195 g).
- **Track:**
  - `level_acceleration` is 0 at rest at any tilt.
  - A simulated push (tilted board, 0.01 g leftover, noise) gave 50.6 cm for 49.0 cm.
  - In the app, with the thread, an L-shaped movement gave F 49.0 / R 36.8 cm exactly as expected.
  - Leaving the tab stops the thread, and an error stops it with a message.
- **Compass:** the raw XY heading changes by ~90° per quarter turn on your board (where `get_compass()` didn't). After H, |B| is steady through a full turn.
- **Interface:**
  - The same design across the tabs: sunken frames, dark canvases, tool buttons on the left.
  - The bottom frames are packed first, so only the canvases shrink when the window gets smaller.
  - The H, Zero and Start buttons stay orange while active, even with the pointer over them.

## Platform notes

- **Windows:**
  - The ANGLE DLLs are in `sensehat/pi3d/`, and `d3dcompiler_47.dll` comes from System32.
  - SDL2's message loop is turned off (it was crashing Tk), and the SDL context is GLES2 through ANGLE.
  - Lines are 1 pixel wide (ANGLE ignores `line_width`).
- **Raspberry Pi (X11):** the pi3d window is minimized, and drawing is done off-screen at the canvas size.
- **Sense HAT:**
  - Calibrate with `RTIMULibCal`: accelerometer (`a`) and magnetometer (`m`), then copy `RTIMULib.ini` to `~/.config/sense_hat/`.
  - This improves the orientation, Linear mode and Track. The hard-iron calibration (H) only affects the raw magnetometer readings in this app.
- **Settings to check on the Pi:**
  - `GRAVITY_SIGNS` (acceleration.py): if an axis grows in Linear mode when you tilt the board.
  - `LEFT_SIGN` (track.py): if the track comes out mirrored.
  - `STILL_ACCEL` (track.py): if Track shows "Moving" while the board is still.
