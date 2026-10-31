# Review: `pihat_gyro.py` and its modules

Reviewed at commit `70e9432` (branch `sense_gyro_test`) on 2026-10-31, together with the fixes for its three remaining bugs. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 882 | Tk app: `PiHatGyroApp` and one class per tab |
| `pi3d_gyro.py` | 546 | 3D scene (pi3d): Windows setup, off-screen framebuffer, views `AxesView` / `SolidView`, 360° background `SceneView`, `GyroScene` (gimbal rotation, `next_view()`, `show_scene()`) |
| `compass.py` | 155 | `raw_heading`, `xy_angle`, `CompassOffsets` (offset per source, S), `HardIronCalibration` (H, `uncorrected()`), `CompassView` |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 205 | `GravityTracker` (Linear: own tilt), `rotate_into_body`, `gravity_vector`, `remove_gravity`, `GravityCheck` (calibration warning), `ResidualCorrection` (Zero / Auto-zero) |
| `track.py` | 457 | `Tracker` (own tilt, ZUPT, drift correction), `TrackSampler` (thread), `TrackView` (with diagnostics) |
| `scene_360.jpg` | 415 KB | 360° photo for V: "Kiara 1 Dawn" by Greg Zaal (polyhaven.com, CC0), 2048×1024 |

**Classes in `pihat_gyro.py`:**

| Class | Role |
|---|---|
| `Tab` | base: the tab's frame, `period`, `update()`, `imu_config()`, `hide()`, `close()`, last `error` |
| `GyroscopeTab` | 3D shape following the orientation, M (view), V (360° scene), R, C, orientation sliders |
| `CompassTab` | compass (Raw XY / sense compass), North slider (offset per source), H, S |
| `VectorTab` | base: the shared X/Y/Z design (simulation sliders, Axes range, info, canvases) |
| `MagnetometerTab` | magnetometer with hard-iron correction, \|B\| warning |
| `AccelerometerTab` | Raw (with "check calibration!") / Linear (own tilt, with Zero / Auto-zero) |
| `TrackTab` | Start/Stop/Reset, Board/Gyro/Compass heading, thread |
| `PiHatGyroApp` | Sense HAT, notebook, shared calibrations (H, compass offsets), `read_magnet()`, `show_field()`, sensors per tab (`apply_imu_config`), one loop per tab (`_run`, which survives errors) |

**3D in `pi3d_gyro.py`:**

| Part | What it shows | Settings |
|---|---|---|
| `AxesView` ("Axes", M) | transparent shape with edges, X/Y/Z axes and letters | `*_LINE_WIDTH`, `BACKGROUND_COLOR`, `SHAPE_COLOR`, `SHAPE_ALPHA`, `EDGE_COLOR`, `AXIS_*_COLOR`, `LABEL_*_COLOR` |
| `SolidView` ("Solid", M) | solid shape, no axes: top white-yellow, bottom green, sides grey, lit per pixel | `SOLID_*`: background, face colours, key and fill lights, sky/ground light, shine |
| `SceneView` (V) | 360° photo on a sphere around the camera, turning opposite to the board; works with both views | `SCENE_*`: photo, texture size, radius, yaw offset, detail |

Each view has `name`, `background`, `shader` and `node`. `GyroScene` keeps what they share (display, camera, gimbal, framebuffer), hangs the current view's `node` under the roll node, and draws the scene first when V is on. The scene is built on the first V press. Without `scene_360.jpg`, a panorama marked with N/E/S/W is generated.

**Settings files** (in `sensehat/`, specific to each board):
- `pihat_gyro_hardiron.json`: the H calibration
- `pihat_gyro_compass.json`: the S offsets

## Changes since the previous review (`3e1174f`)

- **Fixed at `70e9432`:**
  - a tab error no longer stops the tab (shown in the window title)
  - Solid shader failures are printed and fall back to `mat_light`; a scene error shows a message box
  - bold titles use `app.bold_font`
  - Gyroscope info labels are `width=17`
- **Fixed now, the three remaining bugs:**
  1. **Linear mode has its own tilt** (`acceleration.GravityTracker`, used at [pihat_gyro.py:577](pihat_gyro.py:577)), the same method as the Track:
     - At stops (accel and gyro steady for 0.3 s), gravity is the mean of the measurement, and the gyro bias is measured too.
     - During movement, gravity turns with the gyroscope (`rotate_into_body`, the same convention as `track.rotate_by_gyro`).
     - It no longer depends on RTIMULib settling, and a calibration that isn't exactly 1 g doesn't matter.
     - A constant acceleration with no change for over 0.3 s looks like a stop and is removed like gravity.
  2. **Magnetometer / H:**
     - The |B| warning is judged on the field the sensor actually sees (`HardIronCalibration.uncorrected()`). When it warns, that value is shown too, e.g. `|B|: 47.2 µT (sensor 159)`.
     - If saving H fails, a message says the new offsets are used but not saved ([pihat_gyro.py:383](pihat_gyro.py:383)).
  3. **The off-screen framebuffer is checked** with `glCheckFramebufferStatus` ([pi3d_gyro.py:111](pi3d_gyro.py:111)). If it's incomplete, it's deleted and the error goes to the console and the window title (through `_run`).
- **Tested on Windows:**
  - **Simulated board** (25° tilt, rotation at 0.8 rad/s, 0.2 g push, 0.98 g calibration, gyro bias):
    - the Linear error stayed below 0.01 g in every phase
    - the gyro bias was estimated correctly
  - **In the app with a fake Sense HAT** (RTIMULib 8° off): Linear showed 0.00 g, where the old method gave 0.13 g.
  - **|B| warning:**
    - a corrected 47 µT with the sensor at 159 µT now warns
    - at 406 µT it shows "too close!"
  - **H save failure:** the message box appeared.
  - **Framebuffer:** a forced "unsupported" showed in the title, and the app kept running.
  - **Earlier tests** (all tabs, with and without a Sense HAT; M, V; the tab error loop) still pass.

## Bugs

None known.

## Remaining

1. **The scene isn't tied to real North.**
   - The scene turns with the displayed yaw, so after C (calibrate) its N is the calibration direction.
   - The Compass tab's North offset isn't used.

   Decide whether it should follow true North (the sensor's yaw plus the compass offset) or the calibrated view.

2. **The first V press freezes the window briefly** while the photo loads: ~0.2 s on Windows, probably longer on the Pi. Loading at startup, or in the background, would avoid it.

3. **The chosen view and V aren't remembered:** the app always starts in Axes, with no scene.

4. **At 0, 0, 0 the board is seen exactly edge-on** ([pi3d_gyro.py:442](pi3d_gyro.py:442)). The camera is level with the shape, so in Solid view it's just a grey strip. Raising the camera a little and pointing it down would show the top.

5. **The Solid view relies on pi3d internals:**
   - the face order of `pi3d.Cuboid` ([pi3d_gyro.py:346](pi3d_gyro.py:346))
   - `pi3d.Display.Display.INSTANCE` ([pi3d_gyro.py:288](pi3d_gyro.py:288))

   Both are fine in pi3d 2.55; check the version on the Pi.

6. **Not checked on the Pi:**
   - the Solid shader
   - the 360° scene
   - Linear mode's own tilt (`GravityTracker`): ≈ 0 g at rest after tilting and turning the board
   - `YAW_SIGN` ([track.py:77](track.py:77)) with a track that turns in Gyro mode
   - the `MAG_AXES` Z sign ([track.py:75](track.py:75)), which only matters for the compass tilt correction

7. **Gyro heading takes its start direction from a single compass reading** ([track.py:200](track.py:200)). An average over the first 1 s would be steadier.

8. **The Track fallback reads the orientation for nothing** ([pihat_gyro.py:701](pihat_gyro.py:701)). Removing it would raise the rate when there's no `_imu`.

9. **The single read uses an internal attribute of sense_hat** ([pihat_gyro.py:691](pihat_gyro.py:691)). If `self.sense._imu` changes, the code falls back to three slower reads that aren't from the same instant.

10. **Two threads touching the same data:** H recording and the Track thread both go through `read_magnet()`, and the compass offset changes from Tk while the thread reads it. It works in practice, but a lock in `HardIronCalibration` would be cleaner.

11. **The Gyroscope tab needs to settle after other tabs**, since they turn off some sensors.

12. **A new image every frame** ([pihat_gyro.py:246](pihat_gyro.py:246)).

13. **Track accuracy is limited by the method:** ~1 cm per move with stops between moves; without stops it drifts within seconds. Better accuracy needs an extra sensor without drift: a mouse sensor / optical flow, wheel encoders, or camera + ArUco markers.

14. **ANGLE licence file is missing** (`sensehat/pi3d/`). The committed DLLs are BSD-licensed and the repo is public.

15. **Leftovers**
    - `self.sense.clear()` ([pihat_gyro.py:769](pihat_gyro.py:769)) isn't needed.
    - The `Raw XY heading` label shows the angle `atan2(Y, X)`, not North.
    - The off-screen window move ([pi3d_gyro.py:447](pi3d_gyro.py:447)) is no longer needed.
    - `self.mode = None` in `AccelerometerTab.__init__` ([pihat_gyro.py:531](pihat_gyro.py:531)) is only needed because `linear()` can be called early.
    - `.gitignore`: the two settings files and `pi3d_windll-master.zip`.

## Checked and correct

- **3D:**
  - **Axes:** looks the same as before the change into a class.
  - **Solid:**
    - top white-yellow, bottom green, sides grey, in every pose tried
    - the top isn't clipped to white
  - **Scene:**
    - the right way round and not mirrored
    - yaw scrolls it (N → E → S clockwise), pitch tilts the horizon, roll looks up/down
    - the frame rate is unchanged with it on
  - **M and V:**
    - M goes through the views in order
    - V switches the scene on and off in both views and stays orange while on
    - the view name has a shadow, so it's readable over the photo
- **Tab structure:**
  - Each tab builds its design, states its sensors (`imu_config`), and runs only while it's showing.
  - Leaving a tab calls `hide()`, which stops the Track's thread.
  - Closing calls `close()` on every tab.
  - An error in one tab no longer stops it.
- **Track:**
  - gravity removed exactly at stops
  - stop detection independent of offsets
  - drift correction ~20× better
  - board axes confirmed on the Pi
- **Calibration checks:** "check calibration!" (Accelerometer, Raw) and "g … calibration?" (Track).
- **Linear:** ≈ 0 at rest at any tilt, right after a tab change, and with an imperfect calibration.
- **Compass:**
  - the two offsets are saved with S and read back at startup
  - H makes |B| steady through a full turn
- **Orientation maths and gravity removal:**
  - converting to a rotation and back returns the same angles (error below 10⁻¹³°)
  - gravity at rest is exactly 0 at any tilt, given the orientation
- **Interface:**
  - the same design across all tabs
  - the H, Zero, Start and V buttons stay orange while active
  - warnings in colour and bold
  - all bold titles use the same font

## Platform notes

- **Windows:**
  - The ANGLE DLLs are in `sensehat/pi3d/`.
  - SDL2's message loop is turned off (it was crashing Tk), and the SDL context is GLES2 through ANGLE.
  - Lines are 1 pixel wide, whatever `*_LINE_WIDTH` says.
  - The Solid shader and the scene are tested here (GLES2).
- **Raspberry Pi (X11):**
  - The pi3d window is minimized, and drawing is done off-screen.
  - The Solid shader is converted for GLES2 or GLES3; if it fails, the error is printed and `mat_light` is used.
  - The scene texture is 2048×1024.
- **Sense HAT / RTIMULib:**
  - It reports the direction of gravity: z = +1 g with the board flat.
  - **Accelerometer calibration (`RTIMULibCal`, `a`):** use 6 positions, slowly, holding still in each, **no shaking**. Afterwards `AccelCalMin/Max` should be about ±1.0 on all axes. A wrong calibration scales all readings (seen as 0.42 g on the Pi).
  - The magnetometer can be calibrated with `RTIMULibCal` `m` (for `get_compass()`), or with the app's H (for Raw XY, the Magnetometer tab and the Track).
- **Settings to check on the Pi** (in `track.py`):
  - `FORWARD_AXIS` / `RIGHT_AXIS`: confirmed.
  - `YAW_SIGN`, and the `MAG_AXES` Z sign.
  - `STILL_ACCEL_STD` / `STILL_GYRO_STD` / `GRAVITY_TOLERANCE`: use the diagnostics on the Track canvas.
