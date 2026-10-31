# Review: `pihat_gyro.py` and its modules

Reviewed at commit `e57f31a` (branch `sense_gyro_test`) on 2026-10-31, together with the fixes for the five bugs found in it. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 896 | Tk app: `PiHatGyroApp` and one class per tab |
| `pi3d_gyro.py` | 551 | 3D scene (pi3d): Windows setup, off-screen framebuffer, views `AxesView` / `SolidView`, 360° background `SceneView`, `GyroScene` (gimbal rotation, `next_view()`, `show_scene()`) |
| `compass.py` | 155 | `raw_heading`, `xy_angle`, `CompassOffsets` (offset per source, S), `HardIronCalibration` (H, `uncorrected()`), `CompassView` |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 210 | `GravityTracker` (Linear: own tilt), `rotate_into_body`, `gravity_vector`, `remove_gravity`, `GravityCheck` (calibration warning), `ResidualCorrection` (Zero / Auto-zero) |
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
| `SceneView` (V) | 360° photo on a sphere around the camera, turning opposite to the board; works with both views. With a Sense HAT it follows the real world: the sensor's tilt and its heading to North | `SCENE_*`: photo, texture size, radius, yaw offset, detail |

Each view has `name`, `background`, `shader` and `node`. `GyroScene` keeps what they share (display, camera, gimbal, framebuffer), hangs the current view's `node` under the roll node, and draws the scene first when V is on. The scene is built on the first V press. Without `scene_360.jpg`, a panorama marked with N/E/S/W is generated.

**Settings files** (in `sensehat/`, specific to each board):
- `pihat_gyro_hardiron.json`: the H calibration
- `pihat_gyro_compass.json`: the S offsets

## Changes since the previous review (`70e9432`)

- **Fixed at `e57f31a`:**
  - Linear mode has its own tilt (`acceleration.GravityTracker`): gravity measured at stops, turned by the gyroscope while moving
  - the |B| warning is judged on the field the sensor actually sees
  - saving H shows an error message if it fails
  - the off-screen framebuffer is checked with `glCheckFramebufferStatus`
- **Fixed now, the five bugs found in `e57f31a`:**
  1. **The error in the window title is cleared on a tab change** (`_on_tab_changed`, [pihat_gyro.py:827](pihat_gyro.py:827)). Before, it stayed after leaving the failing tab. If the new tab also fails, it shows its own error.
  2. **The \|B\| warning no longer makes the window wider** ([pihat_gyro.py:878](pihat_gyro.py:878)). The sensor value is shown more briefly, e.g. `|B|: 284.4 µT (406) too close!`, so the window stays 399 px wide.
  3. **A failed framebuffer resize no longer leads to a crash** ([pi3d_gyro.py:521](pi3d_gyro.py:521)). `offscreen_size` is cleared with `offscreen`, so the next render tries again, even at the old size.
  4. **Linear starts correctly while the board is moving** ([acceleration.py:123](acceleration.py:123)):
     - Stillness is judged from 3 samples (`MIN_SAMPLES`), so movement right after a tab change or switching to Linear is seen at once and doesn't go into gravity.
     - The gyro bias is measured only with a full steady window.
     - Starting while turning, the error went from 0.26 g to 0.02 g.
  5. **The scene follows real North** ([pihat_gyro.py:242](pihat_gyro.py:242)):
     - With a Sense HAT, the 360° background uses the sensor's tilt without the C offsets.
     - Its yaw is the board's heading plus the Compass tab's "sense compass" offset, as in the Compass tab, so the photo's N is North.
     - The shape still shows the calibrated orientation.
     - `GyroScene.render()` takes an optional `scene_orientation`.
     - Without a Sense HAT, the scene follows the sliders as before.
- **Tested on Windows:**
  - **Title:** a failing Gyroscope tab, then Compass: the title went back to normal.
  - **Magnetometer:** the window stayed 399 px wide with the warning.
  - **Framebuffer:** a forced resize failure, then the old size: the image came back.
  - **Linear started while turning:** 0.02 g error, with no wrong gyro bias.
  - **Scene after C, with a 12.5° offset:** the shape was 0, 0, 0; the scene was 5, −3, 92.5 (the sensor's tilt, yaw 80 + 12.5).
  - **Earlier tests:** all still pass (all tabs with and without a Sense HAT, M, V, Linear, \|B\|).

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

6. **Gyro heading takes its start direction from a single compass reading** ([track.py:200](track.py:200)). An average over the first 1 s would be steadier.

7. **The Track fallback reads the orientation for nothing** ([pihat_gyro.py:707](pihat_gyro.py:707)). Removing it would raise the rate when there's no `_imu`.

8. **The single read uses an internal attribute of sense_hat** ([pihat_gyro.py:697](pihat_gyro.py:697)). If `self.sense._imu` changes, the code falls back to three slower reads that aren't from the same instant.

9. **Two threads touching the same data:** H recording and the Track thread both go through `read_magnet()`, and the compass offset changes from Tk while the thread reads it. It works in practice, but a lock in `HardIronCalibration` would be cleaner.

10. **The Gyroscope tab needs to settle after other tabs**, since they turn off some sensors.

11. **A new image every frame** ([pihat_gyro.py:252](pihat_gyro.py:252)).

12. **Track accuracy is limited by the method:** ~1 cm per move with stops between moves; without stops it drifts within seconds. Better accuracy needs an extra sensor without drift: a mouse sensor / optical flow, wheel encoders, or camera + ArUco markers.

13. **ANGLE licence file is missing** (`sensehat/pi3d/`). The committed DLLs are BSD-licensed and the repo is public.

14. **Leftovers**
    - `self.sense.clear()` ([pihat_gyro.py:775](pihat_gyro.py:775)) isn't needed.
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
