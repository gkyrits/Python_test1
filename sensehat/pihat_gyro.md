# Review: `pihat_gyro.py` and its modules

Reviewed at commit `5b23f57` (branch `sense_gyro_test`) on 2026-10-31, together with the fixes for remaining items 6, 7 and 13 of that review. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 894 | Tk app: `PiHatGyroApp` and one class per tab |
| `pi3d_gyro.py` | 551 | 3D scene (pi3d): Windows setup, off-screen framebuffer, views `AxesView` / `SolidView`, 360° background `SceneView`, `GyroScene` (gimbal rotation, `next_view()`, `show_scene()`) |
| `compass.py` | 155 | `raw_heading`, `xy_angle`, `CompassOffsets` (offset per source, S), `HardIronCalibration` (H, `uncorrected()`), `CompassView` |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 210 | `GravityTracker` (Linear: own tilt), `rotate_into_body`, `gravity_vector`, `remove_gravity`, `GravityCheck` (calibration warning), `ResidualCorrection` (Zero / Auto-zero) |
| `track.py` | 470 | `Tracker` (own tilt, ZUPT, drift correction, Gyro heading started from a 1 s compass average), `TrackSampler` (thread), `TrackView` (with diagnostics) |
| `pi3d/` | | ANGLE DLLs for Windows, with `README.md` (origin) and `LICENSE-ANGLE.txt` (BSD) |
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
| `SceneView` (V) | 360° photo on a sphere around the camera, turning opposite to the board; works with both views. With a Sense HAT it follows the real world: the sensor's tilt and its heading to North | `SCENE_*`: photo, texture size, radius, yaw offset, detail |

Each view has `name`, `background`, `shader` and `node`. `GyroScene` keeps what they share (display, camera, gimbal, framebuffer), hangs the current view's `node` under the roll node, and draws the scene first when V is on. The scene is built on the first V press. Without `scene_360.jpg`, a panorama marked with N/E/S/W is generated.

**Settings files** (in `sensehat/`, specific to each board):
- `pihat_gyro_hardiron.json`: the H calibration
- `pihat_gyro_compass.json`: the S offsets

## Changes since the previous review (`e57f31a`)

- **Fixed at `5b23f57`:**
  - the window title error is cleared on a tab change
  - the \|B\| warning text no longer widens the window
  - a failed framebuffer resize is retried
  - Linear starts correctly while the board is moving
  - the 360° scene follows real North (sensor tilt and heading + compass offset)
- **Fixed now, remaining items 6, 7 and 13 of that review:**
  - **Gyro heading starts from a compass average** ([track.py:210](track.py:210)):
    - For the first `START_STILL` (1 s), while the board is still, the start direction is the circular mean of the compass, which is correct around 0°/360° too. After that, or from the first movement, only the gyroscope.
    - One bad first reading (metal or a magnet nearby) no longer turns the whole track. In a test with a 40° spike on the first two readings, the start was 359.4° instead of 318.3°.
  - **The Track no longer reads the orientation:**
    - It's removed from the sample interface: `read_sample()` returns `(accel, gyro, mag, timestamp)`, and `Tracker.update(accel, gyro, mag, now)`.
    - The fallback without `_imu` makes two or three reads instead of three or four ([pihat_gyro.py:691](pihat_gyro.py:691)).
  - **ANGLE licence:** `sensehat/pi3d/LICENSE-ANGLE.txt`, taken from the official ANGLE repository, and `sensehat/pi3d/README.md` with where the DLLs come from (pi3d_windll, 64-bit).
- **Tested on Windows:**
  - **Gyro heading:** the spike test above, and noise around 0°/360° (359.8°).
  - **Track fallback without `_imu`:** it ran at 64 samples/s and never read the orientation.
  - **Earlier tests:** all tabs with and without a Sense HAT, the Track, and Linear still pass.

## Bugs

None known.

## Remaining

1. **The first V press freezes the window briefly** while the photo loads: ~0.2 s on Windows, probably longer on the Pi. Loading at startup, or in the background, would avoid it.

2. **The chosen view and V aren't remembered:** the app always starts in Axes, with no scene.

3. **At 0, 0, 0 the board is seen exactly edge-on** ([pi3d_gyro.py:442](pi3d_gyro.py:442)). The camera is level with the shape, so in Solid view it's just a grey strip. Raising the camera a little and pointing it down would show the top.

4. **The Solid view relies on pi3d internals:**
   - the face order of `pi3d.Cuboid` ([pi3d_gyro.py:346](pi3d_gyro.py:346))
   - `pi3d.Display.Display.INSTANCE` ([pi3d_gyro.py:288](pi3d_gyro.py:288))

   Both are fine in pi3d 2.55; check the version on the Pi.

5. **Not checked on the Pi:**
   - the Solid shader
   - the 360° scene
   - Linear mode's own tilt (`GravityTracker`): ≈ 0 g at rest after tilting and turning the board
   - `YAW_SIGN` ([track.py:77](track.py:77)) with a track that turns in Gyro mode
   - the `MAG_AXES` Z sign ([track.py:75](track.py:75)), which only matters for the compass tilt correction

6. **The single read uses an internal attribute of sense_hat** ([pihat_gyro.py:697](pihat_gyro.py:697)). If `self.sense._imu` changes, the code falls back to three slower reads that aren't from the same instant.

7. **Two threads touching the same data:** H recording and the Track thread both go through `read_magnet()`, and the compass offset changes from Tk while the thread reads it. It works in practice, but a lock in `HardIronCalibration` would be cleaner.

8. **The Gyroscope tab needs to settle after other tabs**, since they turn off some sensors.

9. **A new image every frame** ([pihat_gyro.py:252](pihat_gyro.py:252)).

10. **Track accuracy is limited by the method:** ~1 cm per move with stops between moves; without stops it drifts within seconds. Better accuracy needs an extra sensor without drift: a mouse sensor / optical flow, wheel encoders, or camera + ArUco markers.

11. **Leftovers**
    - `self.sense.clear()` ([pihat_gyro.py:773](pihat_gyro.py:773)) isn't needed.
    - The `Raw XY heading` label shows the angle `atan2(Y, X)`, not North.
    - The off-screen window move ([pi3d_gyro.py:447](pi3d_gyro.py:447)) is no longer needed.
    - `self.mode = None` in `AccelerometerTab.__init__` ([pihat_gyro.py:537](pihat_gyro.py:537)) is only needed because `linear()` can be called early.
    - `remove_gravity` / `gravity_vector` in `acceleration.py` are no longer used by the app (Linear uses `GravityTracker`).
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
    - with a Sense HAT it uses the real tilt and heading to North, independent of C
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
  - The ANGLE DLLs are in `sensehat/pi3d/`, with their licence (`LICENSE-ANGLE.txt`).
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
