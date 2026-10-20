# Review: `sense3d_test.py`

Reviewed at commit `64dfce2` (branch `sense_gyro_test`), with the working copy as of 2026-10-20.

## What the program does

It shows a transparent cuboid with a wireframe, X/Y/Z axes and axis letters. The shape follows the Sense HAT orientation, or follows sliders when no Sense HAT is present.

- **Rendering:** pi3d draws the scene into an off-screen framebuffer the same size as the canvas. The pixels are read back and shown in a Tk `Canvas`. The real pi3d window is hidden on Windows and minimized on X11.
- **Rotation:** three nested "gimbal" nodes apply the angles in the Sense HAT order: roll (X), then pitch (Z), then yaw (Y).
- **Windows support:** two workarounds for pi3d 2.55. The ANGLE DLLs are loaded from `sensehat/pi3d/`, and SDL2 is forced to create a GLES2 context through ANGLE with its own message loop turned off.

## Issues

### Medium

1. **Bold title font may come out a different size on the Pi** ([sense3d_test.py:238](sense3d_test.py:238))
   `font="TkDefaultFont 9 bold"` is read as a font *family* called "TkDefaultFont" at size 9, not as the named default font. On Windows it happens to look right. On the Pi, the default font is usually a different size, so the title can end up smaller or larger than the other labels. Fix:
   ```python
   import tkinter.font as tkfont
   bold = tkfont.nametofont("TkDefaultFont").copy(); bold.configure(weight="bold")
   ```

2. **Info labels may be too narrow** ([sense3d_test.py:259](sense3d_test.py:259))
   `width=12` (in average characters) is less than `Pitch (Z): 359.9°` needs, which is 17 characters. With a Sense HAT the values go up to 359.9, so the text can get cut off on the right. Check on the Pi, or go back to 15–17.

3. **Offsets are added to the Euler angles, not applied as a rotation** ([sense3d_test.py:328](sense3d_test.py:328))
   `(sensor + offset) % 360` works when only one axis is offset, or when all the angles are small. Once the board is tilted on two axes, a pitch offset no longer turns the shape around the board's own Z axis. For a real "zero" calibration, rotate by the inverse of a reference orientation (matrix or quaternion). For a test tool, the current approach is acceptable.

4. **No check that the framebuffer is complete** ([sense3d_test.py:64-82](sense3d_test.py:64))
   If a driver rejects the framebuffer setup, everything renders silently black. That is exactly how pi3d's `OffScreenTexture` failed on Windows. Add a check after the attachments:
   ```python
   if gl.glCheckFramebufferStatus(GL_FRAMEBUFFER) != 0x8CD5:  # GL_FRAMEBUFFER_COMPLETE
       raise RuntimeError("offscreen framebuffer incomplete")
   ```

### Low

5. **Stale comment and setting** ([sense3d_test.py:103-104](sense3d_test.py:103))
   The comment says to set `HIDE_PI3D_WINDOW = False` if Tk shows black. Since the switch to the off-screen framebuffer, what Tk shows no longer depends on the pi3d window. The flag now only controls whether that window is visible. The off-screen move at line 133 is also no longer needed.

6. **A new image is created every frame** ([sense3d_test.py:341-343](sense3d_test.py:341))
   Each frame creates a new `PhotoImage`. When the size hasn't changed, `self.tk_image.paste(pil_img)` reuses the existing one. That is cheaper on the Pi, where reading the pixels back and converting them is the main cost at larger window sizes.

7. **Values are shown in two different ranges**
   Without a Sense HAT the angles are shown as −180…180, the slider range. With a Sense HAT they are shown as 0…360, from the `% 360`. Pick one range for both. For example, `((a + 180) % 360) - 180` always gives −180…180.

8. **An error stops the rendering for good** ([sense3d_test.py:320](sense3d_test.py:320))
   Any exception in `render_loop`, such as an I2C read error from `get_orientation()`, ends the `after()` chain. The window stays open but frozen. A `try/finally` that always reschedules would keep it running.

9. **Naming and leftovers**
   - The class is called `Transparent3DCubeApp`, but the window is titled "Sense Gyroscope".
   - `self.frame` (the pi3d wireframe holder) is easy to confuse with the Tk frames. `self.wireframe` would be clearer.
   - `self.sense.clear()` isn't needed, because nothing is drawn on the LED matrix.
   - The section comments are numbered 7, 9, 8 in code order. The order is needed for `pack`, but the numbers are confusing.
   - `MY_W/H/D` are written like constants but are local variables. Moving them next to `CANVAS_*` would make them easier to find.

10. **The 24 separate `pi3d.Lines` objects could be fewer** ([sense3d_test.py:173-224](sense3d_test.py:173))
    Each segment is its own object and its own draw call. pi3d's `Lines(..., strip=False)` draws separate pairs of points, so the 12 edges could be one object and each letter could be one object. This is only a speed improvement.

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
- The workarounds are documented in comments and limited to `sys.platform == "win32"`.
