# Review: `pihat_gyro.py` and its modules

Reviewed at commit `b3ca1d9` (branch `sense_gyro_test`) on 2026-10-29. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 832 | Tk app: `PiHatGyroApp` and one class per tab |
| `pi3d_gyro.py` | 424 | 3D scene (pi3d): Windows setup, off-screen framebuffer, views `AxesView` / `SolidView`, `GyroScene` (gimbal rotation, `next_view()`) |
| `compass.py` | 150 | `raw_heading`, `xy_angle`, `CompassOffsets` (offset per source, S), `HardIronCalibration` (H), `CompassView` |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 118 | `gravity_vector`, `remove_gravity`, `GravityCheck` (calibration warning), `ResidualCorrection` (Zero / Auto-zero) |
| `track.py` | 457 | `Tracker` (own tilt, ZUPT, drift correction), `TrackSampler` (thread), `TrackView` (with diagnostics) |

**Classes in `pihat_gyro.py`:**

| Class | Role |
|---|---|
| `Tab` | base: the tab's frame, `period`, `update()`, `imu_config()`, `hide()`, `close()` |
| `GyroscopeTab` | 3D shape following the orientation, M (view), R, C, orientation sliders |
| `CompassTab` | compass (Raw XY / sense compass), North slider (offset per source), H, S |
| `VectorTab` | base: the shared X/Y/Z design (simulation sliders, Axes range, info, canvases) |
| `MagnetometerTab` | magnetometer with hard-iron correction, \|B\| warning |
| `AccelerometerTab` | Raw (with "check calibration!") / Linear (with Zero / Auto-zero) |
| `TrackTab` | Start/Stop/Reset, Board/Gyro/Compass heading, thread |
| `PiHatGyroApp` | Sense HAT, notebook, shared calibrations (H, compass offsets), `read_magnet()`, `show_field()`, sensors per tab (`apply_imu_config`), one loop per tab (`_run`) |

**3D views in `pi3d_gyro.py`** (M goes to the next one, in the order of `VIEWS`):

| View | What it shows | Settings |
|---|---|---|
| `AxesView` ("Axes") | transparent shape with edges, X/Y/Z axes and letters | `*_LINE_WIDTH`, `BACKGROUND_COLOR`, `SHAPE_COLOR`, `SHAPE_ALPHA`, `EDGE_COLOR`, `AXIS_*_COLOR`, `LABEL_*_COLOR` |
| `SolidView` ("Solid") | solid shape, no axes: top white-yellow, bottom green, sides grey, lit per pixel | `SOLID_*`: background, face colours, key and fill lights, sky/ground light, shine |

Each view has `name`, `background`, `shader` and `node`. `GyroScene` keeps what they share (display, camera, gimbal, framebuffer) and hangs the current view's `node` under the roll node.

**Settings files** (in `sensehat/`, specific to each board):
- `pihat_gyro_hardiron.json`: the H calibration
- `pihat_gyro_compass.json`: the S offsets

## Changes since the previous review (`b481e18`)

- **3D settings at the top of `pi3d_gyro.py`:** line widths (now 2) and all colours, so they can be changed in one place.
- **M button:** selects the next 3D view. The view's name is shown at the top-left of the canvas.
- **New Solid view:**
  - It uses its own shader: per-pixel lighting (Blinn-Phong) with a key light, a weak cool fill light, more light from above than below, a small shine, and gamma 2.2.
  - The shader is written like pi3d's own and adapted the same way for GLES2 / GLES3 (`_shader_source`).
  - Each face is a separate buffer, so each can have its own colour.
- **The `background` parameter of `GyroScene` is gone:** each view has its own background, set with `glClearColor` before each frame.
- **Tested on Windows:** both views, the M button (Axes → Solid → Axes), and closing. With the depth test alone (no culling) the faces shown are the same, so the Solid view shows the right faces.
- The "`M` has no command" leftover is resolved.

## Issues

### Medium

1. **If the Solid shader fails to compile, nothing is printed** ([pi3d_gyro.py:310](pi3d_gyro.py:310))
   pi3d writes shader errors only at DEBUG log level and continues. On the Pi (GLES3, or an older pi3d), a shader error would show just a blank Solid view with no message. Checking `GL_COMPILE_STATUS` / `GL_LINK_STATUS`, printing the log and falling back to pi3d's `mat_light` would make this safe. **Check on the Pi** that the Solid view appears.

2. **Linear mode still uses RTIMULib's orientation** ([pihat_gyro.py:548](pihat_gyro.py:548))
   `remove_gravity(raw, self.sense.get_orientation())` leaves 0.1–0.2 g of gravity behind while RTIMULib is still settling, e.g. after a tab change. The Track's own-tilt method (gravity at stops, gyroscope during movement) would fix it. It can move into a shared class in `acceleration.py`, and the change stays inside `AccelerometerTab`.

3. **Track accuracy is limited by the method**
   With stops between moves it's ~1 cm per move; without stops it drifts within seconds. More accuracy needs an extra sensor without drift: a USB optical mouse or optical flow for a table, wheel encoders for a robot, or camera + ArUco markers.

4. **The single read uses an internal attribute of sense_hat** ([pihat_gyro.py:661](pihat_gyro.py:661))
   `self.sense._imu` isn't public API. If a version changes it, the code falls back automatically to three reads, which is slower and not from the same instant.

5. **Bold titles still use `"TkDefaultFont 9 bold"`** ([pihat_gyro.py:147](pihat_gyro.py:147), [247](pihat_gyro.py:247), [405](pihat_gyro.py:405), [425](pihat_gyro.py:425), [515](pihat_gyro.py:515), [523](pihat_gyro.py:523), [623](pihat_gyro.py:623))
   This is read as a font family called "TkDefaultFont", so on the Pi the 7 titles may come out a different size. `app.bold_font` already exists and is used for the warnings.

6. **Gyroscope info labels may be cut off on the Pi** ([pihat_gyro.py:167](pihat_gyro.py:167))
   `width=12` stays fixed, but `Pitch (Y): -123.4°` is 18 characters.

7. **ANGLE licence file is missing** (`sensehat/pi3d/`): the committed DLLs are BSD-licensed, and the repo is public.

### Low

8. **An error stops that tab's loop for good** ([pihat_gyro.py:771](pihat_gyro.py:771))
   An I2C error inside a tab's `update()` ends its `after()` chain, and the tab freezes. Since all tabs share `_run`, the fix is in **one place**: a `try/except` that shows the error and schedules the next call. The Track thread already handles errors this way.

9. **Solid view at 0, 0, 0 shows only a grey strip** ([pi3d_gyro.py:333](pi3d_gyro.py:333))
   The camera is level with the shape, so with the board flat the top is seen exactly edge-on. Raising the camera a little and pointing it down (for both views) would show the top in the rest position.

10. **The Solid view relies on pi3d internals** ([pi3d_gyro.py:281](pi3d_gyro.py:281), [315](pi3d_gyro.py:315))
    - The face order of `pi3d.Cuboid` (+Z, +X, +Y, −Y, −X, −Z) and its `vertices` / `indices` / `normals` lists.
    - `pi3d.Display.Display.INSTANCE` for the GL type.

    Both are the same in pi3d 2.55 on Windows; check the version on the Pi.

11. **The chosen view isn't remembered:** the app always starts in Axes.

12. **Not checked on the Pi:**
    - `YAW_SIGN` ([track.py:77](track.py:77)) with a track that turns in Gyro mode.
    - The `MAG_AXES` Z sign ([track.py:75](track.py:75)): it only affects the compass tilt correction with the board tilted.

13. **Gyro heading takes its start direction from a single compass reading** ([track.py:200](track.py:200))
    Metal or a magnet nearby at that moment turns the whole track. An average over the first 1 s would be more stable.

14. **The fallback reads the orientation for nothing** ([pihat_gyro.py:671](pihat_gyro.py:671)): the Track no longer uses it. Removing it would raise the rate when there's no `_imu`.

15. **Two threads touching the same data**
    - H recording and the Track thread both go through `read_magnet()`.
    - The compass offset is changed from Tk while the thread reads it.

    Both are simple variables, so in practice there's no problem, but a lock in `HardIronCalibration` would be cleaner.

16. **The Gyroscope tab needs to settle after other tabs**, since they turn off some sensors. The Track doesn't have this problem.

17. **The |B| warning uses the corrected value** (the field the sensor actually sees is the uncorrected one), and **saving H has no error handling** ([compass.py:109](compass.py:109)). S already handles it.

18. **No check that the framebuffer is complete** ([pi3d_gyro.py:107](pi3d_gyro.py:107)), and **a new image every frame** ([pihat_gyro.py:224](pihat_gyro.py:224)).

19. **Leftovers**
    - `self.sense.clear()` ([pihat_gyro.py:739](pihat_gyro.py:739)) isn't needed.
    - The `Raw XY heading` label shows the angle `atan2(Y, X)`, not North.
    - The off-screen window move ([pi3d_gyro.py:338](pi3d_gyro.py:338)) is no longer needed.
    - In `AccelerometerTab.__init__`, `self.mode = None` ([pihat_gyro.py:504](pihat_gyro.py:504)) before `super().__init__()` is needed only because `linear()` can be called early. A small tidy-up would be to create the controls before the base builds the panel.
    - `.gitignore`: the two settings files and `pi3d_windll-master.zip`.

## Checked and correct

- **3D views:**
  - Axes looks the same as before the change into a class.
  - Solid: top white-yellow, bottom green, sides grey, in every pose tried. The lighting doesn't clip the top to white.
  - M goes through the views in order and back to the first. The view's name on the canvas follows.
  - All views are built once at startup; switching only changes the roll node's child.
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
  - Lines are 1 pixel wide, whatever `*_LINE_WIDTH` says.
  - The Solid shader is tested here (GLES2).
- **Raspberry Pi (X11):**
  - The pi3d window is minimized, and drawing is done off-screen.
  - The Solid shader is converted for GLES2 or GLES3, depending on the context. Not yet tested.
- **Sense HAT / RTIMULib:**
  - It reports the direction of gravity: z = +1 g with the board flat.
  - **Accelerometer calibration (`RTIMULibCal`, `a`):** use 6 positions, slowly, holding still in each, **no shaking**. Afterwards `AccelCalMin/Max` should be about ±1.0 on all axes. A wrong calibration scales all readings (seen as 0.42 g on the Pi).
  - The magnetometer can be calibrated with `RTIMULibCal` `m` (for `get_compass()`), or with the app's H (for Raw XY, the Magnetometer tab and the Track).
- **Settings to check on the Pi** (in `track.py`):
  - `FORWARD_AXIS` / `RIGHT_AXIS`: confirmed.
  - `YAW_SIGN`, and the `MAG_AXES` Z sign.
  - `STILL_ACCEL_STD` / `STILL_GYRO_STD` / `GRAVITY_TOLERANCE`: use the diagnostics on the Track canvas.
