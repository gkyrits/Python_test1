# Review: `pihat_gyro.py` and its modules

Reviewed at commit `3e1174f` (branch `sense_gyro_test`) on 2026-10-31, together with the fixes for the first four bugs of that review. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 867 | Tk app: `PiHatGyroApp` and one class per tab |
| `pi3d_gyro.py` | 539 | 3D scene (pi3d): Windows setup, off-screen framebuffer, views `AxesView` / `SolidView`, 360° background `SceneView`, `GyroScene` (gimbal rotation, `next_view()`, `show_scene()`) |
| `compass.py` | 150 | `raw_heading`, `xy_angle`, `CompassOffsets` (offset per source, S), `HardIronCalibration` (H), `CompassView` |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 118 | `gravity_vector`, `remove_gravity`, `GravityCheck` (calibration warning), `ResidualCorrection` (Zero / Auto-zero) |
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
| `AccelerometerTab` | Raw (with "check calibration!") / Linear (with Zero / Auto-zero) |
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

## Changes since the previous review (`b3ca1d9`)

- **V button and `SceneView`:** a 360° photo behind the shape that turns with the orientation. Yaw 0 / 90 / 180 shows N / E / S.
- **Fixed, from the bugs of the review at `3e1174f`:**
  1. **An error no longer stops a tab** ([pihat_gyro.py:793](pihat_gyro.py:793)). `_run` catches it and keeps the loop going.
     - The error shows in the window title, e.g. `Sense Gyroscope - Gyroscope error: OSError: …`.
     - The traceback is printed once, until the error changes.
     - The title goes back to normal when the tab works again.
  2. **3D errors are shown.**
     - The Solid shader is checked after compiling (`_shader_errors`, [pi3d_gyro.py:293](pi3d_gyro.py:293)). On failure the GL log is printed and pi3d's `mat_light` is used, so the shape is still visible (without shine and gamma).
     - If the scene can't be built on V, a message box shows the error and V stays off ([pihat_gyro.py:196](pihat_gyro.py:196)).
  3. **Bold titles use `app.bold_font`** (7 places) instead of `"TkDefaultFont 9 bold"`.
  4. **Gyroscope info labels are `width=17`** ([pihat_gyro.py:172](pihat_gyro.py:172)): `Pitch (Y): -179.9°` fits, and the window stays the same width.
- **Tested on Windows:**
  - a tab that fails for 0.8 s then recovers: the loop continued and the title went back to normal
  - a broken shader: it fell back to `mat_light`
  - a failing scene: the message box appeared and V stayed off
  - labels at −123.4 / −179.9 / −150.5

## Bugs

1. **Linear mode leaves some gravity behind** ([pihat_gyro.py:570](pihat_gyro.py:570))
   `remove_gravity(raw, self.sense.get_orientation())` uses RTIMULib's orientation. It leaves 0.1–0.2 g while RTIMULib is still settling, e.g. after a tab change. The Track's own-tilt method (gravity at stops, gyroscope during movement) would fix it, as a shared class in `acceleration.py`.

2. **Magnetometer / H**
   - The |B| warning uses the corrected value; the field the sensor actually sees is the uncorrected one.
   - Saving H has no error handling ([compass.py:111](compass.py:111)). S already handles it.

3. **No check that the off-screen framebuffer is complete** ([pi3d_gyro.py:108](pi3d_gyro.py:108)). If it's incomplete on some GPU, the result is a black image with no message. `glCheckFramebufferStatus` with a printed message would show it.

## Remaining

4. **The scene isn't tied to real North.**
   - The scene turns with the displayed yaw, so after C (calibrate) its N is the calibration direction.
   - The Compass tab's North offset isn't used.

   Decide whether it should follow true North (the sensor's yaw plus the compass offset) or the calibrated view.

5. **The first V press freezes the window briefly** while the photo loads: ~0.2 s on Windows, probably longer on the Pi. Loading at startup, or in the background, would avoid it.

6. **The chosen view and V aren't remembered:** the app always starts in Axes, with no scene.

7. **At 0, 0, 0 the board is seen exactly edge-on** ([pi3d_gyro.py:436](pi3d_gyro.py:436)). The camera is level with the shape, so in Solid view it's just a grey strip. Raising the camera a little and pointing it down would show the top.

8. **The Solid view relies on pi3d internals:**
   - the face order of `pi3d.Cuboid` ([pi3d_gyro.py:340](pi3d_gyro.py:340))
   - `pi3d.Display.Display.INSTANCE` ([pi3d_gyro.py:282](pi3d_gyro.py:282))

   Both are fine in pi3d 2.55; check the version on the Pi.

9. **Not checked on the Pi:**
   - the Solid shader
   - the 360° scene
   - `YAW_SIGN` ([track.py:77](track.py:77)) with a track that turns in Gyro mode
   - the `MAG_AXES` Z sign ([track.py:75](track.py:75)), which only matters for the compass tilt correction

10. **Gyro heading takes its start direction from a single compass reading** ([track.py:200](track.py:200)). An average over the first 1 s would be steadier.

11. **The Track fallback reads the orientation for nothing** ([pihat_gyro.py:693](pihat_gyro.py:693)). Removing it would raise the rate when there's no `_imu`.

12. **The single read uses an internal attribute of sense_hat** ([pihat_gyro.py:683](pihat_gyro.py:683)). If `self.sense._imu` changes, the code falls back to three slower reads that aren't from the same instant.

13. **Two threads touching the same data:** H recording and the Track thread both go through `read_magnet()`, and the compass offset changes from Tk while the thread reads it. It works in practice, but a lock in `HardIronCalibration` would be cleaner.

14. **The Gyroscope tab needs to settle after other tabs**, since they turn off some sensors.

15. **A new image every frame** ([pihat_gyro.py:246](pihat_gyro.py:246)).

16. **Track accuracy is limited by the method:** ~1 cm per move with stops between moves; without stops it drifts within seconds. Better accuracy needs an extra sensor without drift: a mouse sensor / optical flow, wheel encoders, or camera + ArUco markers.

17. **ANGLE licence file is missing** (`sensehat/pi3d/`). The committed DLLs are BSD-licensed and the repo is public.

18. **Leftovers**
    - `self.sense.clear()` ([pihat_gyro.py:761](pihat_gyro.py:761)) isn't needed.
    - The `Raw XY heading` label shows the angle `atan2(Y, X)`, not North.
    - The off-screen window move ([pi3d_gyro.py:441](pi3d_gyro.py:441)) is no longer needed.
    - `self.mode = None` in `AccelerometerTab.__init__` ([pihat_gyro.py:526](pihat_gyro.py:526)) is only needed because `linear()` can be called early.
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
