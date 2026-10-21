# Review: `sense3d_test.py`

Reviewed at commit `a2fdab8` (branch `sense_gyro_test`) on 2026-10-22. This replaces the first review, made at `64dfce2`.

## What the program does

It shows a transparent cuboid with a wireframe and X/Y/Z axes. The axes are named as on the Sense HAT: X = roll (red), Y = pitch (green), Z = yaw (blue). The shape follows the Sense HAT orientation, or follows sliders when no Sense HAT is present.

- **Rendering:** pi3d draws the scene into an off-screen framebuffer the same size as the canvas. The pixels are read back and shown in a Tk `Canvas`. The real pi3d window is hidden on Windows and minimized on X11.
- **Rotation:** three nested "gimbal" nodes apply the angles in the Sense HAT order: roll (pi3d X, sign flipped), then pitch (pi3d Z), then yaw (pi3d Y).
- **User interface:**
  - The `M` / `R` / `C` tool buttons sit to the left of the canvas.
  - An info frame shows the current Roll / Pitch / Yaw.
  - A slider frame controls the orientation values (no Sense HAT) or the orientation offsets (with a Sense HAT).
  - **C** calibrates: it sets the offsets so the shape reads 0/0/0. **R** resets the offsets to 0. `M` has no action yet.
- **Windows support:** two workarounds for pi3d 2.55. The ANGLE DLLs are loaded from `sensehat/pi3d/`, and SDL2 is forced to create a GLES2 context through ANGLE with its own message loop turned off.

## Issues

### Medium

1. **Calibrating at a tilt makes later movement inaccurate** ([sense3d_test.py:366](sense3d_test.py:366))
   C subtracts the sensor angles one by one, so at that moment the shape reads exactly 0/0/0. But the three angles depend on each other. If you calibrate with the board tilted (say 30° pitch), then later roll the board, the shape turns around a slightly wrong axis. The error grows with the tilt you calibrated at. Near-level calibration works fine. Making it exact means storing the calibration pose as a rotation (matrix or quaternion) and undoing it.

2. **Info labels may be cut off on the Pi** ([sense3d_test.py:276](sense3d_test.py:276))
   The labels are 12 characters wide, and they keep that width because they don't stretch. `Pitch (Y): -123.4°` is 18 characters. It fits on Windows because the font there is wide, but the Pi's default font is different. Check it on the Pi with large negative values. If it's cut off, use `fill=tk.X` with `width=0`, or go back to about 17.

3. **Bold title font may come out a different size on the Pi** ([sense3d_test.py:254](sense3d_test.py:254))
   `font="TkDefaultFont 9 bold"` is read as a font *family* called "TkDefaultFont" at size 9, not as the named default font. Fix:
   ```python
   import tkinter.font as tkfont
   bold = tkfont.nametofont("TkDefaultFont").copy(); bold.configure(weight="bold")
   ```

### Low

4. **An error stops the rendering for good** ([sense3d_test.py:358](sense3d_test.py:358))
   Any exception in `render_loop`, such as an I2C read error from `get_orientation()`, ends the `after()` chain. The window stays open but frozen. A `try/finally` that always reschedules would keep it running.

5. **No check that the framebuffer is complete** ([sense3d_test.py:64-82](sense3d_test.py:64))
   If a driver rejects the framebuffer setup, everything renders silently black. Add a check after the attachments:
   ```python
   if gl.glCheckFramebufferStatus(GL_FRAMEBUFFER) != 0x8CD5:  # GL_FRAMEBUFFER_COMPLETE
       raise RuntimeError("offscreen framebuffer incomplete")
   ```

6. **Stale comment and setting** ([sense3d_test.py:103-104](sense3d_test.py:103), [134](sense3d_test.py:134))
   The comment says to set `HIDE_PI3D_WINDOW = False` if Tk shows black. That can no longer happen since the switch to off-screen drawing. The flag now only controls whether the pi3d window is visible. The off-screen move at line 134 is also no longer needed.

7. **A new image is created every frame** ([sense3d_test.py:380-382](sense3d_test.py:380))
   When the size hasn't changed, `self.tk_image.paste(pil_img)` reuses the existing `PhotoImage`. That is cheaper on the Pi, where reading the pixels back and converting them is the main cost at larger window sizes.

8. **`M` button has no command** ([sense3d_test.py:239](sense3d_test.py:239))
   It's a placeholder, so clicking it does nothing.

9. **Naming and leftovers**
   - The class is called `Transparent3DCubeApp`, but the window is titled "Sense Gyroscope".
   - `self.frame` (the pi3d wireframe holder) is easy to confuse with the Tk frames. `self.wireframe` would be clearer.
   - `self.sense.clear()` isn't needed, because nothing is drawn on the LED matrix.
   - The section comments are numbered 7, 9, 8 in code order. The order is needed for `pack`, but the numbers are confusing.
   - `MY_W/H/D` are written like constants but are local variables. Their comments still use pi3d axis names: height is pi3d Y, which is the Sense HAT's Z.

10. **The 24 separate `pi3d.Lines` objects could be fewer** ([sense3d_test.py:174-228](sense3d_test.py:174))
    pi3d's `Lines(..., strip=False)` draws separate pairs of points, so the 12 edges could be one object and each letter could be one object. This is only a speed improvement.

## Fixed since the first review

- Values are now shown in the same −180…180 range with and without a Sense HAT (`_wrap_angle`). `-0.0°` is no longer shown.
- The info and slider labels now use the same font.
- The axis names and colours match the Sense HAT. The roll direction is flipped to match the board, as confirmed on hardware.

## Platform notes

- **Windows:**
  - It needs `libEGL.dll` / `libGLESv2.dll` in `sensehat/pi3d/`. That folder isn't in git, so a fresh clone won't run until the DLLs are copied there.
  - `d3dcompiler_47.dll` comes from System32.
  - ANGLE ignores `line_width`, so all lines are 1 pixel wide.
- **Raspberry Pi (X11):** the pi3d window is minimized with `XIconifyWindow`. If minimizing fails, a message is printed and the program carries on.
- **Sense HAT:** yaw comes from the magnetometer. It drifts unless the compass is calibrated. If only tilt matters, consider `set_imu_config(False, True, True)`.

## What's good

- Fallback chain for imports: `sense_hat` → `sense_emu` → sliders only.
- The wireframe is computed from `MY_W/H/D`, so changing the size updates everything.
- The drawing order (lines first, then the transparent body) keeps the inner axes and back edges visible.
- The gimbal nodes use only pi3d's public API, with no matrix hacking.
- The off-screen framebuffer makes the output independent of the pi3d window's size and visibility on both platforms.
- Layout: the bottom frames are packed first, so only the 3D view shrinks when the window gets smaller.
- Calibrate stores exact (unrounded) offsets, so the shape lands exactly on 0.
- The workarounds are documented in comments and limited to `sys.platform == "win32"`.
