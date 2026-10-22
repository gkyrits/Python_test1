# Review: `sense3d_test.py`

Reviewed at commit `75813e0` (branch `sense_gyro_test`) on 2026-10-22. This replaces the reviews made at `64dfce2` and `a2fdab8`.

## What the program does

It shows a transparent cuboid with a wireframe and X/Y/Z axes. The axes are named as on the Sense HAT: X = roll (red), Y = pitch (green), Z = yaw (blue). The shape follows the Sense HAT orientation, or follows sliders when no Sense HAT is present.

- **Rendering:** pi3d draws the scene into an off-screen framebuffer the same size as the canvas. The pixels are read back and shown in a Tk `Canvas`. The real pi3d window is hidden on Windows and minimized on X11.
- **Rotation:** three nested "gimbal" nodes apply the angles in the Sense HAT order: roll (pi3d X, sign flipped), then pitch (pi3d Z), then yaw (pi3d Y).
- **Calibration:** the offsets are a rotation applied before the sensor's: `R = R_offset · R_sensor`. The shape's angles are read back from `R`.
  - **C** sets `R_offset` to the reverse of the current sensor rotation. The shape reads 0/0/0, and later movements are measured relative to that position.
  - **R** sets the offsets back to 0.
- **User interface:**
  - The `M` / `R` / `C` tool buttons sit to the left of the canvas. `M` has no action yet.
  - An info frame shows the current Roll / Pitch / Yaw.
  - A slider frame controls the orientation values (no Sense HAT) or the offsets (with a Sense HAT).
- **Windows support:** the ANGLE DLLs are committed in `sensehat/pi3d/` and loaded from there. SDL2 is forced to create a GLES2 context through ANGLE, with its own message loop turned off.

## Issues

### Medium

1. **Moving a slider by hand behaves differently with a Sense HAT** ([sense3d_test.py:385](sense3d_test.py:385))
   The sliders are now a rotation applied before the sensor's. Moving one slider no longer shifts the matching angle by the same amount: after calibrating, moving only the Yaw slider can also change roll and pitch. C and R work exactly, but fine-tuning by hand is less intuitive than before. If you want sliders that map 1:1, store C's correction as a separate rotation and apply the slider values on top as simple added offsets.

2. **Info labels may be cut off on the Pi** ([sense3d_test.py:296](sense3d_test.py:296))
   The labels are 12 characters wide, and they keep that width because they don't stretch. `Pitch (Y): -123.4°` is 18 characters. It fits on Windows because the font there is wide, but the Pi's default font is different. Check it on the Pi with large negative values. If it's cut off, use `fill=tk.X` with `width=0`, or go back to about 17.

3. **Bold title font may come out a different size on the Pi** ([sense3d_test.py:274](sense3d_test.py:274))
   `font="TkDefaultFont 9 bold"` is read as a font *family* called "TkDefaultFont" at size 9, not as the named default font. Fix:
   ```python
   import tkinter.font as tkfont
   bold = tkfont.nametofont("TkDefaultFont").copy(); bold.configure(weight="bold")
   ```

4. **ANGLE licence file is missing** (`sensehat/pi3d/`)
   The committed `libEGL.dll` / `libGLESv2.dll` are ANGLE builds, which are BSD-licensed. That licence asks for its notice to be included when the binaries are redistributed, and the repo is public on GitHub. Add the licence file from `pi3d_windll` (or ANGLE's own) next to the DLLs.

### Low

5. **Shown values jump when pitch is near ±90°** ([sense3d_test.py:28-33](sense3d_test.py:28))
   This is a limit of describing a rotation with three angles. At pitch ±90°, roll and yaw are no longer separate, so the displayed roll and yaw can jump suddenly. The shape itself is still drawn correctly. Since calibration, this can also happen relative to the calibrated position, e.g. calibrate with the board flat, then stand it up vertically.

6. **An error stops the rendering for good** ([sense3d_test.py:376](sense3d_test.py:376))
   Any exception in `render_loop`, such as an I2C read error from `get_orientation()`, ends the `after()` chain. The window stays open but frozen. A `try/finally` that always reschedules would keep it running.

7. **No check that the framebuffer is complete** ([sense3d_test.py:80-102](sense3d_test.py:80))
   If a driver rejects the framebuffer setup, everything renders silently black. Add a check after the attachments:
   ```python
   if gl.glCheckFramebufferStatus(GL_FRAMEBUFFER) != 0x8CD5:  # GL_FRAMEBUFFER_COMPLETE
       raise RuntimeError("offscreen framebuffer incomplete")
   ```

8. **Stale comment and setting** ([sense3d_test.py:123-124](sense3d_test.py:123), [154](sense3d_test.py:154))
   The comment says to set `HIDE_PI3D_WINDOW = False` if Tk shows black. That can no longer happen since the switch to off-screen drawing. The flag now only controls whether the pi3d window is visible. The off-screen move at line 154 is also no longer needed.

9. **A new image is created every frame** ([sense3d_test.py:398-400](sense3d_test.py:398))
   When the size hasn't changed, `self.tk_image.paste(pil_img)` reuses the existing `PhotoImage`. That is cheaper on the Pi, where reading the pixels back and converting them is the main cost at larger window sizes.

10. **`M` button has no command** ([sense3d_test.py:259](sense3d_test.py:259))
    It's a placeholder, so clicking it does nothing.

11. **Naming and leftovers**
    - The class is called `Transparent3DCubeApp`, but the window is titled "Sense Gyroscope".
    - `self.frame` (the pi3d wireframe holder) is easy to confuse with the Tk frames. `self.wireframe` would be clearer.
    - `self.sense.clear()` isn't needed, because nothing is drawn on the LED matrix.
    - The section comments are numbered 7, 9, 8 in code order. The order is needed for `pack`, but the numbers are confusing.
    - `MY_W/H/D` are written like constants but are local variables. Their comments still use pi3d axis names: height is pi3d Y, which is the Sense HAT's Z.
    - `pi3d_windll-master.zip` sits untracked in `sensehat/pi3d/`. Delete it or add it to `.gitignore`.

12. **The 24 separate `pi3d.Lines` objects could be fewer** ([sense3d_test.py:194-248](sense3d_test.py:194))
    pi3d's `Lines(..., strip=False)` draws separate pairs of points, so the 12 edges could be one object and each letter could be one object. This is only a speed improvement.

## Fixed since earlier reviews

- **Calibrating at a tilt** (`9e1b4f2`): the calibration is now stored as a rotation, so later movements are exact. Example: after calibrating at roll 10°, pitch 30°, yaw 50°, pitching the board 20° about its own axis shows 0 / 20 / 0. The old method showed 3.4 / 19.6 / 5.3.
- **Windows DLLs** (`75813e0`): they're now in git, so a fresh clone runs on Windows without copying anything by hand.
- Values are shown in the same −180…180 range in both modes (pitch −90…90 with a Sense HAT). `-0.0°` is no longer shown.
- The info and slider labels now use the same font.
- The axis names and colours match the Sense HAT. The roll direction is flipped to match the board, as confirmed on hardware.

## Platform notes

- **Windows:**
  - `libEGL.dll` / `libGLESv2.dll` are in `sensehat/pi3d/`.
  - `d3dcompiler_47.dll` comes from System32.
  - ANGLE ignores `line_width`, so all lines are 1 pixel wide.
- **Raspberry Pi (X11):** the pi3d window is minimized with `XIconifyWindow`. If minimizing fails, a message is printed and the program carries on.
- **Sense HAT:** yaw comes from the magnetometer. It drifts unless the compass is calibrated. If only tilt matters, consider `set_imu_config(False, True, True)`.

## What's good

- Fallback chain for imports: `sense_hat` → `sense_emu` → sliders only.
- `euler_to_matrix` / `matrix_to_euler` follow the Sense HAT's angle convention (RTIMULib's Z-Y-X order). Converting to a rotation and back returns the same angles, with an error below 10⁻¹³°. The `asin` input is clamped so rounding errors can't crash it.
- The wireframe is computed from `MY_W/H/D`, so changing the size updates everything.
- The drawing order (lines first, then the transparent body) keeps the inner axes and back edges visible.
- The gimbal nodes use only pi3d's public API, with no matrix hacking.
- The off-screen framebuffer makes the output independent of the pi3d window's size and visibility on both platforms.
- Layout: the bottom frames are packed first, so only the 3D view shrinks when the window gets smaller.
- The workarounds are documented in comments and limited to `sys.platform == "win32"`.
