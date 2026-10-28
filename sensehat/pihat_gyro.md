# Review: `pihat_gyro.py` and its modules

Reviewed at commit `4e718ca` (branch `sense_gyro_test`) on 2026-10-28. This replaces the earlier reviews.

## Structure

| File | Lines | Contents |
|---|---|---|
| `pihat_gyro.py` | 707 | Tk app with 6 tabs, Sense HAT reading, per-tab sensor setup, orientation maths |
| `pi3d_gyro.py` | 278 | 3D scene (pi3d): Windows setup, off-screen framebuffer, gimbal rotation. Interface `GyroScene` |
| `compass.py` | 150 | `raw_heading`, `xy_angle`, `CompassOffsets` (offset per source, S), `HardIronCalibration` (H), `CompassView` |
| `xyz_force.py` | 88 | `XYZForceView` (X/Y cross and Z arrows), `magnitude` |
| `acceleration.py` | 86 | `gravity_vector`, `remove_gravity`, `ResidualCorrection` (Zero / Auto-zero) |
| `track.py` | 448 | `Tracker` (own tilt, ZUPT, drift correction), `TrackSampler` (thread), `TrackView` |

**Tabs:**
- **Gyroscope:** 3D shape following the orientation, with C/R calibration.
- **Compass:** north from the raw XY or `get_compass()`, with H (hard-iron) and S (save the offsets).
- **Magnetometer:** X/Y/Z arrows and |B|, with a warning near a magnet.
- **Accelerometer:** Raw or Linear (gravity removed), with Zero / Auto-zero and an axis range choice.
- **Track:** speed and track, in Board, Gyro or Compass heading.

Each tab turns on only the sensors it needs, and reads only while it's showing.

**Settings files** (in `sensehat/`, specific to each board):
- `pihat_gyro_hardiron.json`: the H calibration
- `pihat_gyro_compass.json`: the S offsets, one for Raw XY and one for sense compass

## Changes since the previous review (`a469abc`)

**Track:**
- **Own tilt:** reset at every stop from the accelerometer's average, and following the gyroscope during movement. RTIMULib's orientation isn't used, so its slow settling no longer matters. The Pi showed `|a|` = 0.23 g at Start before this fix.
- **Drift correction at every stop:** the leftover speed corrects the whole stretch of the track for that move.
- **Trapezoidal integration**, and a **track limit of 5,000 points** (previous item 8).
- **Offset-independent stop detection:** based on the spread over a 0.2 s window, plus the gyroscope offset on 3 axes, plus recovery after 1 s. **Diagnostics** are drawn on the canvas.
- **One RTIMULib read per sample** (previous item 2), with a fallback to three reads.
- **Gyro heading:** turns from the gyroscope; north-up, starting from the compass direction.
- **Compass heading:** tilt-corrected.
- **Board axes:** forward = +y reading, right = −x reading. This fixed the track being rotated 90° and mirrored on the Pi.

**Compass:**
- Two offsets (Raw XY and sense compass).
- **S** saves them, and they're read back at startup.
- The Track uses the Raw XY offset.

**Simulated results:**

| Test | Result |
|---|---|
| 5 pushes, leftover 0.02 g | mean error 0.3 cm (originally 6.7 cm) |
| Same, leftover 0.05 g | 0.4 cm (originally 22 m) |
| Pushes right after Start, while RTIMULib's orientation is 13° wrong | 1.1 cm (before the own tilt: 25 m) |
| Gyroscope offset 0.3 rad/s, board still | stays Still |

## Issues

### Medium

1. **Linear mode in the Accelerometer tab still uses RTIMULib's orientation** ([pihat_gyro.py:639](pihat_gyro.py:639))
   `remove_gravity(raw, self.sense.get_orientation())` has the same weakness the Track had. At tab change, or right after movement, the orientation can be several degrees off, leaving 0.1–0.2 g of gravity behind (13° gave 0.23 g on the Pi). Zero / Auto-zero mask it, but don't fix it. The Track's own-tilt method (gravity at stops, gyroscope during movement) would fix this too. It could move into a shared class in `acceleration.py`.

2. **Track accuracy is limited by the method**
   With stops between moves it's ~1 cm per move; without stops it drifts within seconds. Beyond this, it needs an extra sensor without drift: a USB optical mouse or an optical-flow sensor for a table, wheel encoders for a robot, or camera + ArUco markers.

3. **The single read uses an internal attribute of sense_hat** ([pihat_gyro.py:561](pihat_gyro.py:561))
   `self.sense._imu` isn't public API. If a sense_hat version changes it, the code falls back automatically to three reads (`get_*`), so nothing breaks. But it gets slower, and the three values come from different moments.

4. **Bold titles still use `"TkDefaultFont 9 bold"`** ([pihat_gyro.py:130](pihat_gyro.py:130), [171](pihat_gyro.py:171), [254](pihat_gyro.py:254), [266](pihat_gyro.py:266), [299](pihat_gyro.py:299), [478](pihat_gyro.py:478), [500](pihat_gyro.py:500))
   This is read as a font family called "TkDefaultFont", so on the Pi the 7 titles may come out a different size. `self.bold_font` already exists (used for the |B| warning and "Moving") and should be used here too.

5. **Gyroscope info labels may be cut off on the Pi** ([pihat_gyro.py:152](pihat_gyro.py:152))
   `width=12` stays fixed, but `Pitch (Y): -123.4°` is 18 characters.

6. **ANGLE licence file is missing** (`sensehat/pi3d/`)
   The committed DLLs are BSD-licensed, and the repo is public.

### Low

7. **Not checked on the Pi:**
   - **`MAG_AXES` Z sign** ([track.py:74](track.py:74)): it only affects the compass tilt correction with the board tilted.
   - **`YAW_SIGN`** ([track.py:76](track.py:76)): the pointer looked correct in Gyro, but a track with a turn hasn't been checked.

8. **Gyro heading takes its start direction from a single compass reading** ([track.py:199](track.py:199))
   If there's metal or a magnet near the board at that moment, the whole track is turned by that error. An average over the first 1 s (`START_STILL`) would be more stable.

9. **The fallback path reads the orientation for nothing** ([pihat_gyro.py:571](pihat_gyro.py:571))
   The Track no longer uses RTIMULib's orientation, but the fallback still calls `get_orientation()`, one read out of three per sample. Removing it would raise the rate.

10. **Two threads touching the same data**
    - **H and Track:** if H is recording and the Track is running, `_read_magnet()` updates the min/max from the Track thread while the Tk thread may stop the recording.
    - **Compass offset:** the slider changes `tracker.heading_offset` from the Tk thread while the Track thread reads it.

    Both are simple variables, so in practice there's no problem, but a lock in `HardIronCalibration` would be cleaner.

11. **An error stops the Tk loops for good** ([pihat_gyro.py:382](pihat_gyro.py:382), [390](pihat_gyro.py:390), [621](pihat_gyro.py:621), [632](pihat_gyro.py:632))
    An I2C error freezes that tab. The Track thread already handles this properly: it stops and shows a message.

12. **Orientation needs to settle after switching tabs (Gyroscope tab)**
    The other tabs turn off some sensors, so in the Gyroscope tab RTIMULib needs a moment. The Track no longer has this problem.

13. **The |B| warning uses the corrected value**: the field the sensor actually sees is the uncorrected one.

14. **No error handling when saving H** ([compass.py:109](compass.py:109)). S already handles it with a message.

15. **No check that the framebuffer is complete** ([pi3d_gyro.py:67](pi3d_gyro.py:67)), and **a new image every frame** ([pihat_gyro.py:700](pihat_gyro.py:700)).

16. **Leftovers**
    - [pihat_gyro.py:97](pihat_gyro.py:97): the comment `# Κενό (προς το παρόν) tab` is above the Accelerometer tab, which is no longer empty.
    - The `M` button ([line 115](pihat_gyro.py:115)) has no command.
    - The class `Transparent3DCubeApp` ([line 66](pihat_gyro.py:66)) now holds the whole multi-tab app.
    - `self.sense.clear()` ([line 73](pihat_gyro.py:73)) isn't needed.
    - The `Raw XY heading` label shows the angle `atan2(Y, X)`, not North.
    - The off-screen window move ([pi3d_gyro.py:122](pi3d_gyro.py:122)) is no longer needed.
    - `.gitignore`: the two settings files (`pihat_gyro_hardiron.json`, `pihat_gyro_compass.json`) and `pi3d_windll-master.zip` should be added.

## Checked and correct

- **Module split:** each module has a small interface documented at the top. The 3D library can be swapped with one import.
- **Track:**
  - Gravity is removed exactly at stops, because the tilt comes from the measured gravity, including the sensor's offset and scale error.
  - Stop detection doesn't depend on offsets.
  - The drift correction at stops reduces the error about 20 times.
  - Leaving the tab stops the thread, and an error stops it with a message.
  - In the simulation of the Pi's readings, all 4 directions are correct in Board mode, and the Compass/Gyro track goes the way the pointer points.
- **Compass:**
  - The two offsets are kept separately, saved with S, and read back at startup (tested in a new process).
  - The hard-iron calibration makes |B| steady through a full turn.
- **Orientation maths and gravity removal** (Gyroscope tab, Linear mode): converting to a rotation and back returns the same angles, with an error below 10⁻¹³°, and gravity at rest is exactly 0 at any tilt, given the orientation.
- **Interface:**
  - The same design across all tabs.
  - The H, Zero and Start buttons stay orange while active, even with the pointer over them.
  - The |B| warning in colour and bold.

## Platform notes

- **Windows:**
  - The ANGLE DLLs are in `sensehat/pi3d/`.
  - SDL2's message loop is turned off (it was crashing Tk), and the SDL context is GLES2 through ANGLE.
  - Lines are 1 pixel wide.
- **Raspberry Pi (X11):** the pi3d window is minimized, and drawing is done off-screen.
- **Sense HAT / RTIMULib:**
  - It reports the direction of gravity: z = +1 g with the board flat.
  - For the Track, "forward" is the y reading and "right" is the −x reading.
  - Calibrating with `RTIMULibCal` (accelerometer `a`, magnetometer `m`) improves the Gyroscope tab, Linear mode and `get_compass()`. The Track and Raw XY don't need it: they use their own calibration (tilt from gravity, H).
- **Settings to check on the Pi** (in `track.py`):
  - `FORWARD_AXIS` / `RIGHT_AXIS`: set from the Pi.
  - `YAW_SIGN`: if the Gyro track turns the wrong way.
  - `MAG_AXES` Z sign: if the compass jumps when the board is tilted.
  - `STILL_ACCEL_STD` / `STILL_GYRO_STD`: if it shows "Moving" with the board still. Use the diagnostics on the canvas.
