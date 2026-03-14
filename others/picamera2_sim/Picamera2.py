

_cameras_obj  = [{'Model': 'ov5647', 'Location': 2, 'Rotation': 0, 'Id': '/base/soc/i2c0mux/i2c@1/ov5647@36', 'Num': 0}, {'Model': 'UVC Camera (046d:0825)', 'Location': 0, 'Id': '/base/soc/usb@7e980000/usb1@1-1.5:1.0-046d:0825', 'Num': 2}, {'Model': 'USB2.0 PC CAMERA', 'Location': 0, 'Id': '/base/soc/usb@7e980000/usb1@1-1.4:1.0-18ec:3299', 'Num': 1}]

_cam1_prop_obj = {'Model': 'ov5647', 'UnitCellSize': (1400, 1400), 'Location': 2, 'Rotation': 0, 'PixelArraySize': (2592, 1944), 'ColorFilterArrangement': 2, 'PixelArrayActiveAreas': [(16, 6, 2592, 1944)], 'ScalerCropMaximum': (0, 0, 0, 0), 'SystemDevices': (20749, 20737, 20738, 20739)}
_cam1_sens_obj = [{'format': 'SGBRG10_CSI2P', 'unpacked': 'SGBRG10', 'bit_depth': 10, 'size': (640, 480), 'fps': 58.92, 'crop_limits': (16, 0, 2560, 1920), 'exposure_limits': (134, 4879289, 20000)}, {'format': 'SGBRG10_CSI2P', 'unpacked': 'SGBRG10', 'bit_depth': 10, 'size': (1296, 972), 'fps': 46.34, 'crop_limits': (0, 0, 2592, 1944), 'exposure_limits': (86, 3066985, 20000)}, {'format': 'SGBRG10_CSI2P', 'unpacked': 'SGBRG10', 'bit_depth': 10, 'size': (1920, 1080), 'fps': 32.81, 'crop_limits': (348, 434, 1928, 1080), 'exposure_limits': (110, 3066979, 20000)}, {'format': 'SGBRG10_CSI2P', 'unpacked': 'SGBRG10', 'bit_depth': 10, 'size': (2592, 1944), 'fps': 15.63, 'crop_limits': (0, 0, 2592, 1944), 'exposure_limits': (130, 3066985, 20000)}]

_cam2_prop_obj = {'Model': 'UVC Camera (046d:0825)', 'Location': 0, 'PixelArraySize': (1280, 960), 'PixelArrayActiveAreas': [(0, 0, 1280, 960)], 'SystemDevices': (20753,)}
_com2_sens_obj = [{'format': 'MJPEG'}, {'format': 'YUYV'}] 

_cam3_prop_obj = {'Model': 'USB2.0 PC CAMERA', 'Location': 0, 'PixelArraySize': (640, 480), 'PixelArrayActiveAreas': [(0, 0, 640, 480)], 'SystemDevices': (20751,)}
_cam3_sens_obs = [{'format': 'YUYV'}]

_call_cnt=0

def global_camera_info():
    global _call_cnt
    _call_cnt += 1
    if _call_cnt == 1:
        return _cameras_obj
    elif _call_cnt == 2:
        return [_cameras_obj[0]]
    elif _call_cnt == 3:
        return _cameras_obj[0:2]
    elif _call_cnt == 4:
        _call_cnt=0
        return [_cameras_obj[0]] + [_cameras_obj[2]]

