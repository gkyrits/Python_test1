# Review: `pihat_gyro.py` and its modules

Reviewed at commit `b481e18` (branch `sense_gyro_test`) on 2026-10-29. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 824 | Tk app: `PiHatGyroApp` and one class per tab |
| `pi3d_gyro.py` | 278 | 3D scene (pi3d): Windows setup, off-screen framebuffer, gimbal rotation. Interface `GyroScene` |
| `compass.py` | 150 | `raw_heading`, `xy_angle`, `CompassOffsets` (offset per source, S), `HardIronCalibration` (H), `CompassView` |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 118 | `gravity_vector`, `remove_gravity`, `GravityCheck` (calibration warning), `ResidualCorrection` (Zero / Auto-zero) |
| `track.py` | 457 | `Tracker` (own tilt, ZUPT, drift correction), `TrackSampler` (thread), `TrackView` (with diagnostics) |

**Classes in `pihat_gyro.py`:**

| Class | Role |
|---|---|
| `Tab` | base: the tab's frame, `period`, `update()`, `imu_config()`, `hide()`, `close()` |
| `GyroscopeTab` | 3D shape following the orientation, C/R, orientation sliders |
| `CompassTab` | compass (Raw XY / sense compass), North slider (offset per source), H, S |
| `VectorTab` | base: the shared X/Y/Z design (simulation sliders, Axes range, info, canvases) |
| `MagnetometerTab` | magnetometer with hard-iron correction, \|B\| warning |
| `AccelerometerTab` | Raw (with "check calibration!") / Linear (with Zero / Auto-zero) |
| `TrackTab` | Start/Stop/Reset, Board/Gyro/Compass heading, thread |
| `PiHatGyroApp` | Sense HAT, notebook, shared calibrations (H, compass offsets), `read_magnet()`, `show_field()`, sensors per tab (`apply_imu_config`), one loop per tab (`_run`) |

**Settings files** (in `sensehat/`, specific to each board):
- `pihat_gyro_hardiron.json`: the H calibration
- `pihat_gyro_compass.json`: the S offsets

## Changes since the previous review (`d3d7617`)

- **Accelerometer calibration found on the Pi:**
  - Raw Z read 0.42 g with the board still and flat. The cause was a bad `AccelCalMin/Max` in `RTIMULib.ini` (Z max 2.38, from shaking during calibration). After recalibrating, |a| = 0.98 g.
  - **Raw mode is now the default.**
  - In Raw mode, **`GravityCheck`** shows "check calibration!" when |a| at rest is more than 10% away from 1 g.
  - **The Track diagnostics** show the measured gravity **g**, with "calibration?".
- **Restructure:** `PiHatGyroApp` (renamed from `Transparent3DCubeApp`), and one class per tab.
  - One loop mechanism replaces the five `*_loop` methods.
  - Each tab states its own sensors, replacing the `if tab is …` chain.
  - The stale "Κενό tab" comment and the class name item from the previous review are resolved.
- **Tested after the restructure** (fake Sense HAT, and without one): all tabs gave the same results as before.

## Issues

### Medium

1. **Linear mode still uses RTIMULib's orientation** ([pihat_gyro.py:540](pihat_gyro.py:540))
   `remove_gravity(raw, self.sense.get_orientation())` leaves 0.1–0.2 g of gravity behind while RTIMULib is still settling, e.g. after a tab change. The Track's own-tilt method (gravity at stops, gyroscope during movement) would fix it. It can move into a shared class in `acceleration.py`, and now that each tab is its own class, the change stays inside `AccelerometerTab`.

2. **Track accuracy is limited by the method**
   With stops between moves it's ~1 cm per move; without stops it drifts within seconds. More accuracy needs an extra sensor without drift: a USB optical mouse or optical flow for a table, wheel encoders for a robot, or camera + ArUco markers.

3. **The single read uses an internal attribute of sense_hat** ([pihat_gyro.py:653](pihat_gyro.py:653))
   `self.sense._imu` isn't public API. If a version changes it, the code falls back automatically to three reads, which is slower and not from the same instant.

4. **Bold titles still use `"TkDefaultFont 9 bold"`** ([pihat_gyro.py:146](pihat_gyro.py:146), [239](pihat_gyro.py:239), [397](pihat_gyro.py:397), [417](pihat_gyro.py:417), [507](pihat_gyro.py:507), [515](pihat_gyro.py:515), [615](pihat_gyro.py:615))
   This is read as a font family called "TkDefaultFont", so on the Pi the 7 titles may come out a different size. `app.bold_font` already exists and is used for the warnings.

5. **Gyroscope info labels may be cut off on the Pi** ([pihat_gyro.py:166](pihat_gyro.py:166))
   `width=12` stays fixed, but `Pitch (Y): -123.4°` is 18 characters.

6. **ANGLE licence file is missing** (`sensehat/pi3d/`): the committed DLLs are BSD-licensed, and the repo is public.

### Low

7. **An error stops that tab's loop for good** ([pihat_gyro.py:763](pihat_gyro.py:763))
   An I2C error inside a tab's `update()` ends its `after()` chain, and the tab freezes. Since all tabs now share `_run`, the fix is in **one place**: a `try/except` that shows the error and schedules the next call. The Track thread already handles errors this way.

8. **Not checked on the Pi:**
   - `YAW_SIGN` ([track.py:77](track.py:77)) with a track that turns in Gyro mode.
   - The `MAG_AXES` Z sign ([track.py:75](track.py:75)): it only affects the compass tilt correction with the board tilted.

9. **Gyro heading takes its start direction from a single compass reading** ([track.py:200](track.py:200))
   Metal or a magnet nearby at that moment turns the whole track. An average over the first 1 s would be more stable.

10. **The fallback reads the orientation for nothing** ([pihat_gyro.py:663](pihat_gyro.py:663)): the Track no longer uses it. Removing it would raise the rate when there's no `_imu`.

11. **Two threads touching the same data**
    - H recording and the Track thread both go through `read_magnet()`.
    - The compass offset is changed from Tk while the thread reads it.

    Both are simple variables, so in practice there's no problem, but a lock in `HardIronCalibration` would be cleaner.

12. **The Gyroscope tab needs to settle after other tabs**, since they turn off some sensors. The Track doesn't have this problem.

13. **The |B| warning uses the corrected value** (the field the sensor actually sees is the uncorrected one), and **saving H has no error handling** ([compass.py:109](compass.py:109)). S already handles it.

14. **No check that the framebuffer is complete** ([pi3d_gyro.py:67](pi3d_gyro.py:67)), and **a new image every frame** ([pihat_gyro.py:216](pihat_gyro.py:216)).

15. **Leftovers**
    - The `M` button ([pihat_gyro.py:136](pihat_gyro.py:136)) has no command.
    - `self.sense.clear()` ([line 731](pihat_gyro.py:731)) isn't needed.
    - The `Raw XY heading` label shows the angle `atan2(Y, X)`, not North.
    - The off-screen window move ([pi3d_gyro.py:122](pi3d_gyro.py:122)) is no longer needed.
    - In `AccelerometerTab.__init__`, `self.mode = None` before `super().__init__()` is needed only because `linear()` can be called early. A small tidy-up would be to create the controls before the base builds the panel.
    - `.gitignore`: the two settings files and `pi3d_windll-master.zip`.

## Checked and correct

- **Tab structure:**
  - Each tab is self-contained: it builds its design, states its sensors (`imu_config`), and runs only while it's showing.
  - The app holds only what's shared.
  - Leaving a tab calls `hide()`, which stops the Track's thread.
  - Closing calls `close()` on every tab (the 3D scene, the thread).
- **Track:**
  - Gravity is removed exactly at stops (own tilt from the measured gravity).
  - Stop detection doesn't depend on offsets.
  - The drift correction at stops reduces the error about 20 times.
  - Board axes: forward = +y reading, right = −x reading, confirmed on the Pi.
- **Calibration checks:** "check calibration!" (Accelerometer, Raw) and "g … calibration?" (Track) would have caught the bad `RTIMULib.ini` immediately.
- **Compass:**
  - The two offsets are kept separately, saved with S, and read back at startup.
  - H makes |B| steady through a full turn.
- **Orientation maths and gravity removal:** converting to a rotation and back returns the same angles, with an error below 10⁻¹³°; gravity at rest is exactly 0 at any tilt, given the orientation.
- **Interface:**
  - The same design across all tabs.
  - The H, Zero and Start buttons stay orange while active, even with the pointer over them.
  - Warnings in colour and bold.

## Platform notes

- **Windows:**
  - The ANGLE DLLs are in `sensehat/pi3d/`.
  - SDL2's message loop is turned off (it was crashing Tk), and the SDL context is GLES2 through ANGLE.
  - Lines are 1 pixel wide.
- **Raspberry Pi (X11):** the pi3d window is minimized, and drawing is done off-screen.
- **Sense HAT / RTIMULib:**
  - It reports the direction of gravity: z = +1 g with the board flat.
  - **Accelerometer calibration (`RTIMULibCal`, `a`):** use 6 positions, slowly, holding still in each, **no shaking**. Afterwards `AccelCalMin/Max` should be about ±1.0 on all axes. A wrong calibration scales all readings (seen as 0.42 g on the Pi).
  - The magnetometer can be calibrated with `RTIMULibCal` `m` (for `get_compass()`), or with the app's H (for Raw XY, the Magnetometer tab and the Track).
- **Settings to check on the Pi** (in `track.py`):
  - `FORWARD_AXIS` / `RIGHT_AXIS`: confirmed.
  - `YAW_SIGN`, and the `MAG_AXES` Z sign.
  - `STILL_ACCEL_STD` / `STILL_GYRO_STD` / `GRAVITY_TOLERANCE`: use the diagnostics on the Track canvas.
