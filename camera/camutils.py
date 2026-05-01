######################################
# Convert image buffer to PIL
######################################

import numpy as np
import PIL.Image as Image
import io
import cv2
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

#code is from /usr/lib/python3/dist-packages/picamera2/request.py

def _make_array_shared(buffer: np.ndarray, config: Dict[str, Any]) -> np.ndarray:
    """Makes a 2d numpy array from the named stream's buffer without copying memory.
    This method makes an array that is guaranteed to be shared with the underlying
    buffer, that is, no copy of the pixel data is made.
    """
    array = buffer
    fmt = config["format"]
    w, h = config["size"]
    stride = config["stride"]
    # Reshape the 1d array into an image, and "slice" off any padding bytes on the
    # right hand edge (which doesn't copy the pixel data).
    if fmt in ("BGR888", "RGB888"):
        if stride != w * 3:
            array = array.reshape((h, stride))
            array = array[:, :w * 3]
        image = array.reshape((h, w, 3))
    elif fmt in ("XBGR8888", "XRGB8888"):
        if stride != w * 4:
            array = array.reshape((h, stride))
            array = array[:, :w * 4]
        image = array.reshape((h, w, 4))
    elif fmt in ("BGR161616", "RGB161616"):
        if stride != w * 6:
            array = array.reshape((h, stride))
            array = array[:, :w * 6]
        array = array.view(np.uint16)
        image = array.reshape((h, w, 3))
    elif fmt in ("YUV420", "YVU420"):
        # Returning YUV420 as an image of 50% greater height (the extra bit continaing
        # the U/V data) is useful because OpenCV can convert it to RGB for us quite
        # efficiently. We leave any packing in there, however, as it would be easier
        # to remove that after conversion to RGB (if that's what the caller does).
        image = array.reshape((h * 3 // 2, stride))
    elif fmt in ("YUYV", "YVYU", "UYVY", "VYUY"):
        # These dimensions seem a bit strange, but mean that
        # cv2.cvtColor(image, cv2.COLOR_YUV2BGR_YUYV) will convert directly to RGB.
        image = array.reshape(h, stride // 2, 2)
    elif fmt == "MJPEG":
        image = np.array(Image.open(io.BytesIO(array)))  # type: ignore
    elif formats.is_raw(fmt):
        image = array.reshape((h, stride))
    else:
        raise RuntimeError("Format " + fmt + " not supported")
    return image


def _get_pil_mode(fmt):
    mode_lookup = {"RGB888": "BGR", "BGR888": "RGB", "XBGR8888": "RGBX", "XRGB8888": "BGRX"}
    mode = mode_lookup.get(fmt, None)
    if mode is None:
        raise RuntimeError(f"Stream format {fmt} not supported for PIL images")
    return mode


def _make_image(buffer: np.ndarray, config: Dict[str, Any], width: Optional[int] = None,
               height: Optional[int] = None) -> Image.Image:
    """Make a PIL image from the named stream's buffer."""
    fmt = config["format"]
    if fmt == "MJPEG":
        return Image.open(io.BytesIO(buffer))  # type: ignore
    else:
        rgb = _make_array_shared(buffer, config)
    # buffer was already a copy, so don't need to worry about an extra copy for the "RGBX" mode.
    buf = rgb
    if not rgb.data.c_contiguous:
        buf = rgb.base
    mode = _get_pil_mode(fmt)
    pil_img = Image.frombuffer("RGB", (rgb.shape[1], rgb.shape[0]), buf, "raw", mode, rgb.strides[0], 1)
    width = width or rgb.shape[1]
    height = height or rgb.shape[0]
    if width != rgb.shape[1] or height != rgb.shape[0]:
        # This will be slow. Consider requesting camera images of this size in the first place!
        pil_img = pil_img.resize((width, height))  # type: ignore
    return pil_img

    
def make_pil_image(buffer, config):
    frm = config['format']
    if frm == 'YUYV':
        size = config['size']
        width, height = size[0], size[1]
        # 1. Μετατροπή των bytes σε numpy array
        # Τα YUYV δεδομένα έχουν 2 bytes ανά pixel
        raw_array = np.frombuffer(buffer, dtype=np.uint8)
        # 2. Αναδιάταξη σε σχήμα (height, width, 2)
        yuyv_image = raw_array.reshape((height, width, 2))
        # 3. Μετατροπή από YUYV σε BGR (χρησιμοποιώντας OpenCV)
        bgr_image = cv2.cvtColor(yuyv_image, cv2.COLOR_YUV2BGR_YUYV)
        # 4. Μετατροπή από BGR σε RGB (για την Pillow)
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        # 5. Δημιουργία Pillow Image
        pilimg = Image.fromarray(rgb_image)            
    else:
        pilimg = _make_image(buffer, config)
    return pilimg


######################################
# send/receive dictonary data
######################################

import socket
import pickle
import struct

CMD_IMAGE = 1

def send_dict(sock: socket.socket, data_dict):
    data_bytes = pickle.dumps(data_dict, protocol=pickle.HIGHEST_PROTOCOL)
    length_prefix = struct.pack('!I', len(data_bytes))
    sock.sendall(length_prefix + data_bytes)


def recv_dict(sock: socket.socket):
    raw_len = _recv_exact(sock,4)
    if not raw_len:
        return None
    msg_len = struct.unpack('!I', raw_len)[0]
    body = _recv_exact(sock,msg_len)
    if not body:
        return None
    return pickle.loads(body)


def _recv_exact(sock: socket.socket, size):
    buf = b''
    while len(buf) < size:
        chunk = sock.recv(size - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf
