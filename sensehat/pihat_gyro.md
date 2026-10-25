# Review: `pihat_gyro.py` + `pi3d_gyro.py`

Reviewed at commit `fda8e1c` (branch `sense_gyro_test`) on 2026-10-25. This replaces the earlier reviews of `sense3d_test.py`.

## What the program does

It's a Tk app with a notebook of four tabs: **Gyroscope**, **Compass**, and two empty tabs for now (**Accelerometer**, **Magnetometer**).

- **Gyroscope tab:**
  - A transparent cuboid with a wireframe and X/Y/Z axes, named as on the Sense HAT (X = roll red, Y = pitch green, Z = yaw blue). It follows the Sense HAT orientation, or sliders when no Sense HAT is present.
  - **C** calibrates the shape to 0/0/0, and **R** resets the offsets. The offsets are a rotation: `R = R_offset · R_sensor`.
- **Compass tab:**
  - A 2D compass drawn on a Tk canvas.
  - North comes from the raw magnetometer X/Y (`raw_heading`, the default) or from `get_compass()`, chosen with radio buttons. A slider adds an offset from −180° to 180°, or sets North directly without a Sense HAT.
  - The info frame shows North, the raw X/Y/Z, and diagnostics: field strength |B| and the raw XY angle.
- **Sensors per tab:** `set_imu_config` is set to magnetometer only on Compass, and to all three sensors on Gyroscope. The 3D view is drawn only while the Gyroscope tab is showing, and the compass is read only while the Compass tab is showing.
- **Module split:**
  - `pihat_gyro.py` holds the Tk interface, the Sense HAT and the orientation maths.
  - `pi3d_gyro.py` holds everything pi3d: the Windows setup, the off-screen framebuffer, and the scene with its gimbal rotation. Its `GyroScene` interface (`render(orientation, size)` → RGB numpy array) means another 3D library can replace it by changing only the `import pi3d_gyro as gyro3d` line.

## Issues

### Medium

1. **The raw compass heading has no calibration or tilt correction** ([pihat_gyro.py:38-42](pihat_gyro.py:38))
   On your board the raw XY readings are already good: |B| stays at 47.5–50 µT, and each quarter turn gives 82–102° instead of exactly 90°. The remaining ±10° comes from small offsets (hard-iron) and the board not being perfectly flat. Two improvements would help:
   - **Simple calibration:** record the min/max of X and Y while turning the board one full circle, then subtract the centre `((min+max)/2)` before `atan2`. This could be done with one button.
   - **Tilt correction:** use the accelerometer's roll and pitch to project X/Y/Z onto the horizontal plane before `atan2`. This is the standard method, and it means the board doesn't have to be flat.

2. **Moving a Gyroscope slider by hand behaves differently with a Sense HAT** ([pihat_gyro.py:321](pihat_gyro.py:321))
   The sliders are a rotation applied before the sensor's. Moving one slider can also change the other two angles. C and R work exactly, but fine-tuning by hand isn't intuitive. If you want sliders that map 1:1, store C's correction as a separate rotation and apply the sliders on top as added offsets.

3. **Gyroscope info labels may be cut off on the Pi** ([pihat_gyro.py:133](pihat_gyro.py:133))
   `width=12` stays fixed, but `Pitch (Y): -123.4°` is 18 characters. The compass labels no longer have a fixed width, so they don't have this problem. Use the same approach here, or increase the width.

4. **Bold title font may come out a different size on the Pi** ([pihat_gyro.py:111](pihat_gyro.py:111), [153](pihat_gyro.py:153))
   `"TkDefaultFont 9 bold"` is read as a font *family* called "TkDefaultFont", not as the named default font. Fix:
   ```python
   bold = tkfont.nametofont("TkDefaultFont").copy(); bold.configure(weight="bold")
   ```

5. **ANGLE licence file is missing** (`sensehat/pi3d/`)
   `libEGL.dll` / `libGLESv2.dll` are BSD-licensed ANGLE builds, and the repo is public on GitHub. Add the licence file from `pi3d_windll` (or ANGLE's own) next to the DLLs.

### Low

6. **The comment about sensors per tab is out of date** ([pihat_gyro.py:230-232](pihat_gyro.py:230))
   It says "Gyroscope: gyroscope + accelerometer, without magnetometer", but the code sets `set_imu_config(True, True, True)`, which also turns the magnetometer on.

7. **Orientation takes a moment to settle after leaving the Compass tab**
   On the Compass tab, the gyroscope and accelerometer are off, so RTIMULib keeps updating its estimate from the magnetometer alone. When you switch back to Gyroscope, the estimate needs a moment to recover, so the shape may drift briefly. Pressing **C** right after switching tabs can calibrate to an orientation that hasn't settled yet.

8. **A label is misnamed** ([pihat_gyro.py:280-282](pihat_gyro.py:280))
   `Raw XY heading` shows the angle `atan2(Y, X)`, while North with the Raw source is `360 − that angle`. Renaming it to `Raw XY angle` would avoid confusion.

9. **Shown values jump when pitch is near ±90°** ([pihat_gyro.py:30-35](pihat_gyro.py:30))
   This is a limit of describing a rotation with three angles. The shape is still drawn correctly.

10. **An error stops the loops for good** ([pihat_gyro.py:241](pihat_gyro.py:241), [249](pihat_gyro.py:249))
    An exception in `render_loop` or `compass_loop`, such as an I2C error from the Sense HAT, ends that loop's `after()` chain, and that tab freezes. A `try/finally` that always schedules the next call would keep it running.

11. **No check that the framebuffer is complete** ([pi3d_gyro.py:67-89](pi3d_gyro.py:67))
    If a driver rejects it, the 3D view renders silently black. Check `glCheckFramebufferStatus(GL_FRAMEBUFFER) == 0x8CD5` after the attachments.

12. **A new image is created every frame** ([pihat_gyro.py:330](pihat_gyro.py:330))
    When the size hasn't changed, `self.tk_image.paste(...)` reuses the existing `PhotoImage`, which is cheaper on the Pi.

13. **Unneeded off-screen window move** ([pi3d_gyro.py:122](pi3d_gyro.py:122))
    `resize(y=max_height)` is no longer needed, since the window is hidden or minimized and drawing is done off-screen.

14. **Naming and leftovers**
    - The class `Transparent3DCubeApp` now holds the whole multi-tab app. Something like `SenseHatApp` would fit better.
    - `self.frame` in `pi3d_gyro.py` (the wireframe holder, [line 136](pi3d_gyro.py:136)) is easy to confuse with Tk frames. `self.wireframe` would be clearer.
    - `self.sense.clear()` isn't needed.
    - The `M` button has no command yet.
    - The section comments are numbered 1, 2, 4, 3, 5 in code order.
    - The Magnetometer tab is empty, but the Compass tab already shows the magnetometer values (raw X/Y/Z, |B|). When you fill it, those diagnostics could move there.
    - `pi3d_windll-master.zip` is untracked in `sensehat/pi3d/`. Delete it or add it to `.gitignore`.

15. **The 24 separate `pi3d.Lines` objects could be fewer** ([pi3d_gyro.py:162-216](pi3d_gyro.py:162))
    `Lines(..., strip=False)` could draw all the edges as one object and each letter as one object. This is only a speed improvement.

## Fixed since earlier reviews

- **Calibrating at a tilt:** the calibration is stored as a rotation, so later movements are exact.
- **Windows DLLs:** committed in `sensehat/pi3d/`, so a fresh clone runs on Windows.
- **3D module split:** `HIDE_PI3D_WINDOW` and its comment moved to `pi3d_gyro.py`, with corrected wording.
- **CPU:** the 3D view isn't drawn while another tab is showing.
- **Compass:** `get_compass()` gave bad headings on your board (84 → 126 → 101 → 47 for quarter turns), while the raw XY readings are clean. North now comes from the raw XY by default. The diagnostics confirmed the magnetometer hardware works (|B| ≈ 49 µT, constant).

## Platform notes

- **Windows:**
  - The ANGLE DLLs are in `sensehat/pi3d/`.
  - `d3dcompiler_47.dll` comes from System32.
  - ANGLE ignores `line_width`, so all lines are 1 pixel wide.
- **Raspberry Pi (X11):** the pi3d window is minimized with `XIconifyWindow`.
- **Sense HAT:**
  - RTIMULib's processing (`get_orientation` yaw, `get_compass`) needs calibration with `RTIMULibCal`. Copy the resulting `RTIMULib.ini` to `~/.config/sense_hat/`.
  - Without calibration, yaw and `get_compass()` are unreliable. Roll and pitch are unaffected.

## What's good

- **Clean split:** Tk interface and sensors in `pihat_gyro.py`, 3D in `pi3d_gyro.py`. The `GyroScene` interface is small and documented at the top of the module.
- **Orientation maths:** `euler_to_matrix` / `matrix_to_euler` follow the Sense HAT's angle convention. Converting to a rotation and back returns the same angles, with an error below 10⁻¹³°.
- **Per-tab sensor setup:** `get_compass()` and `get_orientation()` don't interfere with each other.
- **Compass reads:** every 20 ms for the measurements, while the display is refreshed every 100 ms to save CPU on the Pi.
- **Diagnostics:** |B| and the raw XY angle separated a library problem from a hardware problem on the first try.
- **Consistent design:** the same sunken frames, slider rows, dark canvas background and padding on both tabs.
- **Layout:** the bottom frames are packed first, so only the canvas shrinks when the window gets smaller.
