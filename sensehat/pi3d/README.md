# ANGLE DLLs for pi3d on Windows

`libEGL.dll` and `libGLESv2.dll` (64-bit) are builds of the [ANGLE project](https://chromium.googlesource.com/angle/angle), taken from the 64-bit folder of [pi3d_windll](https://github.com/pi3d/pi3d_windll).

On Windows, ANGLE provides OpenGL ES 2.0 for pi3d. `pi3d_gyro.py` loads the DLLs from this folder; on the Raspberry Pi they're not used.

ANGLE is distributed under a BSD licence; see [LICENSE-ANGLE.txt](LICENSE-ANGLE.txt).
