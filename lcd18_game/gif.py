# Copyright (c) 2014 Adafruit Industries
# Author: Phil Howard, Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import time

from PIL import Image

import lcd18driver as lcd

print("""
gif.py - Display a gif on the LCD.

If you're using Breakout Garden, plug the 0.96" LCD (SPI)
breakout into the front slot.
""")

if len(sys.argv) > 1:
    image_file = sys.argv[1]
else:
    #print(f"Usage: {sys.argv[0]} <filename.gif>")
    image_file = "pic/deployrainbows.gif"

# Create TFT LCD display class.
disp = lcd.LCD_1inch8()

# Initialize display.
disp.Init()
# Clear display.
disp.clear()
#Set the backlight to 100
disp.bl_DutyCycle(50)

width = disp.width
height = disp.height

# Load an image.
print(f"Loading gif: {image_file}...")
image = Image.open(image_file)

print("Drawing gif, press Ctrl+C to exit!")

frame = 0

while True:
    try:
        image.seek(frame)
        img_r = image.resize((width, height))
        disp.ShowImage(img_r)
        frame += 1
        time.sleep(0.05)

    except EOFError:
        frame = 0
