# Review: `pihat_gyro.py` and its modules

Reviewed at commit `52e6269` (branch `sense_gyro_test`) on 2026-10-31. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 1130 | Tk app: `PiHatGyroApp`, one class per tab, `Tooltip` (balloon help) |
| `pi3d_gyro.py` | 558 | 3D scene (pi3d): Windows setup, off-screen framebuffer, `lit_shader()`, views `AxesView` / `SolidView`, 360° background `SceneView`, `GyroScene` (gimbal rotation, `next_view()`, `show_scene()`) |
| `pi3d_game.py` | 131 | 3D scene of the game: `GameScene` (board, walls, hole, ball, shadow), sharing the pi3d display, framebuffer and `lit_shader()` of `pi3d_gyro` |
| `game.py` | 235 | Game physics, no graphics: `Game` (tilt, jump on an upward flick, walls, hole, levels, best times), `Ball`, `LEVELS` |
| `compass.py` | 155 | `raw_heading`, `xy_angle`, `CompassOffsets` (offset per source, S), `HardIronCalibration` (H, `uncorrected()`), `CompassView` |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 210 | `GravityTracker` (Linear: own tilt), `rotate_into_body`, `gravity_vector`, `remove_gravity`, `GravityCheck` (calibration warning), `ResidualCorrection` (Zero / Auto-zero) |
| `track.py` | 470 | `Tracker` (own tilt, ZUPT, drift correction, Gyro heading started from a 1 s compass average), `TrackSampler` (thread), `TrackView` (with diagnostics) |
| `pi3d/` | | ANGLE DLLs for Windows, with `README.md` (origin) and `LICENSE-ANGLE.txt` (BSD) |
| `scene_360.jpg` | 415 KB | 360° photo for V: "Kiara 1 Dawn" by Greg Zaal (polyhaven.com, CC0), 2048×1024 |

**Classes in `pihat_gyro.py`:**

| Class | Role |
|---|---|
| `Tooltip` | balloon help on any widget: shown after `TOOLTIP_DELAY` (500 ms), hidden on leave or press |
| `Tab` | base: the tab's frame, `period`, `update()`, `imu_config()`, `hide()`, `close()`, last `error` |
| `GyroscopeTab` | 3D shape following the orientation, M (view), V (360° scene), R, C, orientation sliders |
| `CompassTab` | compass (Raw XY / sense compass), North slider (offset per source), H, S |
| `VectorTab` | base: the shared X/Y/Z design (simulation sliders, Axes range, info with `total_tip`, canvases) |
| `MagnetometerTab` | magnetometer with hard-iron correction, \|B\| warning |
| `AccelerometerTab` | Raw (with "check calibration!") / Linear (own tilt, with Zero / Auto-zero) |
| `TrackTab` | Start/Stop/Reset, Board/Gyro/Compass heading, thread |
| `GameTab` | the game: R (restart), C (level = current tilt), L (next level), J (jump); tilt sliders without a Sense HAT |
| `PiHatGyroApp` | Sense HAT, notebook, shared calibrations (H, compass offsets), `read_magnet()`, `show_field()`, sensors per tab (`apply_imu_config`), one loop per tab (`_run`, which survives errors) |

**3D in `pi3d_gyro.py` and `pi3d_game.py`:**

| Part | What it shows | Settings |
|---|---|---|
| `AxesView` ("Axes", M) | transparent shape with edges, X/Y/Z axes and letters | `*_LINE_WIDTH`, `BACKGROUND_COLOR`, `SHAPE_COLOR`, `SHAPE_ALPHA`, `EDGE_COLOR`, `AXIS_*_COLOR`, `LABEL_*_COLOR` |
| `SolidView` ("Solid", M) | solid shape, no axes: top white-yellow, bottom green, sides grey, lit per pixel | `SOLID_*`: background, face colours, key and fill lights, sky/ground light, shine (shared by `lit_shader()`) |
| `SceneView` (V) | 360° photo on a sphere around the camera, turning opposite to the board; works with both views. With a Sense HAT it follows the real world: the sensor's tilt and its heading to North | `SCENE_*`: photo, texture size, radius, yaw offset, detail |
| `GameScene` (Game tab) | wood board tilted towards the camera, walls, black hole, steel ball, a shadow that shrinks while jumping; the camera distance fits the whole board to any canvas shape | `GAME_*`: colours, board tilt and position, fit margin; `HOLE_LIFT` / `SHADOW_LIFT` |

Each view has `name`, `background`, `shader` and `node`. `GyroScene` keeps what they share (display, camera, gimbal, framebuffer), hangs the current view's `node` under the roll node, and draws the scene first when V is on. The scene is built on the first V press. Without `scene_360.jpg`, a panorama marked with N/E/S/W is generated.

**The game (`game.py`, Game tab):**
- **Tilt:** the accelerometer x/y gives the slope, and the ball rolls with 5/7 of it (a rolling ball), with friction (`DAMPING`) and bounces (`BOUNCE`).
- **Jump:** an upward flick, with z above its average by `JUMP_FORCE`, makes the ball jump (`JUMP_SPEED`), with a push in the tilt direction (`JUMP_PUSH`). While the ball rises, walls only hold it back, so it can clear a wall even from touching it.
- **Hole:** the ball falls in, then "In the hole!" with the time. The next level follows after `GAME_NEXT_LEVEL_DELAY` (2 s).
- **3 levels:**
  1. a wall with a gap
  2. a zigzag
  3. a hole inside a walled box (you must jump in)
- **Physics steps:** at most 4 ms (`MAX_STEP`), so the ball doesn't pass through walls.

**Balloon help:** on every button (tool columns, Zero, Start, Reset), radio button (compass source, accelerometer mode, track heading), the Auto-zero checkbutton, and the Field \|B\|, \|B\|, Raw XY heading and \|a\| labels. The long label texts are `FIELD_TIP` and `ACCEL_TOTAL_TIP`.

**Settings files** (in `sensehat/`, specific to each board):
- `pihat_gyro_hardiron.json`: the H calibration
- `pihat_gyro_compass.json`: the S offsets

## Changes since the previous review (`5b23f57`)

- **Fixed at `77cd4fb`:**
  - the Gyro heading starts from a 1 s compass average
  - the Track no longer reads the orientation
  - the ANGLE licence was added
- **New Game tab** (`b21244c`): `game.py` (physics) and `pi3d_game.py` (3D). The lit shader moved into `lit_shader()`. Tabs close in reverse order, because the game uses the Gyroscope's pi3d display.
  - **Fixed while building it:**
    - a jump from against a wall lost its push on the wall's side
    - the substeps after a fall restarted the fall, so the level was never won
    - the board didn't fit narrow canvases
- **Balloon help and two game fixes** (`52e6269`):
  - `Tooltip` on all buttons, radio buttons, Auto-zero and the \|B\| / \|a\| / Raw XY heading labels.
  - **Bug fixed:** without a Sense HAT, `hide()` wasn't called on a tab change, so the game didn't pause. `apply_imu_config` now calls it before the Sense HAT check ([pihat_gyro.py:1071](pihat_gyro.py:1071)).
  - **Bug fixed:** the hole and the shadow were 0.003 / 0.006 above the floor, at the limit of the 16-bit depth buffer (z-fighting risk). They're now 0.02 / 0.03 (`HOLE_LIFT`, [pi3d_game.py:27](pi3d_game.py:27)).
- **Tested on Windows:**
  - **Game physics, on its own:**
    - rolling direction
    - stop at a wall
    - jumping over a wall, including from touching it
    - the hole and the best time
    - calibration (C)
    - start and hole clear in all 3 levels
  - **In the app:**
    - with a fake Sense HAT: the tilt, a flick jump over the wall, and only the accelerometer switched on
    - with sliders and J
    - winning, then the next level after 2 s
    - switching between Gyroscope and Game
    - the board fitting normal, wide and tall canvases
  - **Tooltips:** they appear after 0.5 s, hide on leave and press, wrap long texts, and also work on disabled controls.
  - **Earlier tests:** all tabs with and without a Sense HAT, M, V, Linear, \|B\|, the error title and the framebuffer retry still pass.

## Bugs

None known.

## Remaining

1. **Game tuning to check on the Pi** (top of `game.py`):
   - the tilt direction (`RIGHT_TILT` / `FORWARD_TILT`, [game.py:47](game.py:47)), worked out from the Track's axes
   - the flick sensitivity (`JUMP_FORCE`, [game.py:35](game.py:35))
   - the feel (`GRAVITY`, `DAMPING`, `JUMP_SPEED`, `JUMP_PUSH`)

2. **The flick also moves x/y.** The jump push uses the tilt at that moment ([game.py:144](game.py:144)), so a hard flick could push the ball in an unintended direction. If it does on the Pi, the push can use the tilt from just before the flick.

3. **Best times aren't saved:** they're kept only while the app runs.

4. **Not every control has balloon help:** the Axes range boxes (Accelerometer), the sliders and the Track info labels. Optional; one line each.

5. **The first V press freezes the window briefly** while the photo loads: ~0.2 s on Windows, probably longer on the Pi. Loading at startup, or in the background, would avoid it.

6. **The chosen view and V aren't remembered:** the app always starts in Axes, with no scene.

7. **At 0, 0, 0 the Gyroscope board is seen exactly edge-on** ([pi3d_gyro.py:449](pi3d_gyro.py:449)). The camera is level with the shape, so in Solid view it's just a grey strip. Raising the camera a little and pointing it down would show the top.

8. **The Solid view relies on pi3d internals:**
   - the face order of `pi3d.Cuboid` ([pi3d_gyro.py:353](pi3d_gyro.py:353))
   - `pi3d.Display.Display.INSTANCE` ([pi3d_gyro.py:288](pi3d_gyro.py:288)), also used by `pi3d_game`

   Both are fine in pi3d 2.55; check the version on the Pi.

9. **Not checked on the Pi:**
   - the Solid shader
   - the 360° scene
   - Linear mode's own tilt (`GravityTracker`): ≈ 0 g at rest after tilting and turning the board
   - the Game tab
   - the tooltips (overrideredirect windows under X11)
   - `YAW_SIGN` ([track.py:77](track.py:77)) with a track that turns in Gyro mode
   - the `MAG_AXES` Z sign ([track.py:75](track.py:75)), which only matters for the compass tilt correction

10. **The single read uses an internal attribute of sense_hat** ([pihat_gyro.py:792](pihat_gyro.py:792)). If `self.sense._imu` changes, the code falls back to slower separate reads that aren't from the same instant.

11. **Two threads touching the same data:** H recording and the Track thread both go through `read_magnet()`, and the compass offset changes from Tk while the thread reads it. It works in practice, but a lock in `HardIronCalibration` would be cleaner.

12. **The Gyroscope tab needs to settle after other tabs**, since they turn off some sensors.

13. **A new image every frame** in the Gyroscope ([pihat_gyro.py:316](pihat_gyro.py:316)) and Game ([pihat_gyro.py:975](pihat_gyro.py:975)) tabs. The Game tab runs at 50 fps, so it's the most likely place to be slow on the Pi.

14. **Track accuracy is limited by the method:** ~1 cm per move with stops between moves; without stops it drifts within seconds. Better accuracy needs an extra sensor without drift: a mouse sensor / optical flow, wheel encoders, or camera + ArUco markers.

15. **Leftovers**
    - `self.sense.clear()` ([pihat_gyro.py:1005](pihat_gyro.py:1005)) isn't needed.
    - The `Raw XY heading` label shows the angle `atan2(Y, X)`, not North (its balloon help says so).
    - The off-screen window move ([pi3d_gyro.py:454](pi3d_gyro.py:454)) is no longer needed.
    - `self.mode = None` in `AccelerometerTab.__init__` ([pihat_gyro.py:617](pihat_gyro.py:617)) is only needed because `linear()` can be called early.
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
  - **Game scene:**
    - the whole board is visible at any canvas shape
    - the shadow shrinks while the ball jumps
    - the Gyroscope tab still renders correctly after the game, and back
- **Game:**
  - the ball rolls the way the board tilts
  - it stops at walls without passing through them
  - it clears a wall with a jump, even from touching it
  - a jump with no tilt goes straight up
  - it falls into the hole, the level is won once, and the best time is kept
  - C makes the current tilt count as level
  - the time doesn't count while the tab isn't showing, with or without a Sense HAT
- **Tab structure:**
  - Each tab builds its design, states its sensors (`imu_config`), and runs only while it's showing.
  - Leaving a tab calls `hide()`, which stops the Track's thread and pauses the game, also without a Sense HAT.
  - Closing calls `close()` on every tab, in reverse order (the Game before the Gyroscope's display).
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
  - balloon help on all buttons, radio buttons, Auto-zero and the measurement labels

## Platform notes

- **Windows:**
  - The ANGLE DLLs are in `sensehat/pi3d/`, with their licence (`LICENSE-ANGLE.txt`).
  - SDL2's message loop is turned off (it was crashing Tk), and the SDL context is GLES2 through ANGLE.
  - Lines are 1 pixel wide, whatever `*_LINE_WIDTH` says.
  - The Solid shader, the scene and the game are tested here (GLES2).
- **Raspberry Pi (X11):**
  - The pi3d window is minimized, and drawing is done off-screen.
  - The lit shader (Solid view, game) is converted for GLES2 or GLES3; if it fails, the error is printed and `mat_light` is used.
  - The scene texture is 2048×1024.
  - The off-screen depth buffer is 16-bit, which is why the game's hole and shadow sit 0.02 / 0.03 above the floor.
- **Sense HAT / RTIMULib:**
  - It reports the direction of gravity: z = +1 g with the board flat.
  - **Accelerometer calibration (`RTIMULibCal`, `a`):** use 6 positions, slowly, holding still in each, **no shaking**. Afterwards `AccelCalMin/Max` should be about ±1.0 on all axes. A wrong calibration scales all readings (seen as 0.42 g on the Pi).
  - The magnetometer can be calibrated with `RTIMULibCal` `m` (for `get_compass()`), or with the app's H (for Raw XY, the Magnetometer tab and the Track).
- **Settings to check on the Pi:**
  - In `track.py`:
    - `FORWARD_AXIS` / `RIGHT_AXIS`: confirmed.
    - `YAW_SIGN`, and the `MAG_AXES` Z sign.
    - `STILL_ACCEL_STD` / `STILL_GYRO_STD` / `GRAVITY_TOLERANCE`: use the diagnostics on the Track canvas.
  - In `game.py`: `RIGHT_TILT` / `FORWARD_TILT`, `JUMP_FORCE`.
