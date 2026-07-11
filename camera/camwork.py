import tkinter as tk
import Pmw as tk2
import time as tm
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import threading as thrd
import socket

import webutils as web
import sockutils as scutl
import genutils as utl
import camoptions as opt

import camplay_gui as gui


global Picamera2, Preview, Transform, Quality
global H264Encoder, MJPEGEncoder, JpegEncoder, Encoder
global FfmpegOutput, FileOutput

Picamera2 = None

def import_special_libs():
    global Picamera2, Preview, Transform, Quality
    global H264Encoder, MJPEGEncoder, JpegEncoder, Encoder
    global FfmpegOutput, FileOutput
    try:
        from picamera2 import Picamera2, Preview
        from picamera2.encoders import Quality, H264Encoder, MJPEGEncoder, JpegEncoder, Encoder
        from picamera2.outputs import FfmpegOutput, FileOutput
        from libcamera import Transform
    except Exception as e:
        print("Error importing : ", e.__str__())
        from picamera2_sim import Picamera2, Preview, Transform
        print('import simulation libs')

picamera2_inst = [None,None,None,None]

##############################################################################################

def cam_config_size(cfg,size):
        main = cfg['main']
        main['size'] = tuple(size)
        cfg['main'] = main
        raw = cfg['raw']
        if raw == None:
            return
        raw['size'] = tuple(size)
        cfg['raw'] = raw


def set_modal(win):
    win.grab_set()
    win.wait_window()
    win.grab_release()

##############################################################################################
# Camera Window Class
##############################################################################################
class camera_win:
    INFO_PROP_ID = 0
    INFO_SENSOR_ID = 1

    def __init__(self, idx, cam_model, cam_num, root=False):
        self.idx = idx
        self.cam_num = cam_num
        self.cam_model = cam_model
        self.picam = None
        self.propInf_win = None
        self.sensorInf_win = None
        self.preview_on = False
        self.pilview_on = False
        self.fullview_on = False
        self.pvimg = None
        print(f'Start camera win {self.idx}')
        #build window
        if not root:
            self.win = tk.Toplevel()
        else:
            self.win = tk.Tk()
        self.win.title(cam_model)
        self.win.geometry("420x310+150+100")
        self.win.resizable(0,0)
        self.win.bind('<Destroy>',self.__close_win)
        self.hflip = tk.IntVar()
        self.vflip = tk.IntVar()        
        #menu
        mnBar = tk.Frame(self.win, relief=tk.SUNKEN, borderwidth=1, height=20)
        mnBar.pack(fill=tk.X)
        mnBar.pack_propagate(False)
        mnBtn1 = tk.Menubutton(mnBar, text='Info', underline=0)
        mnBtn1.pack(side=tk.LEFT, padx="2m")
        mnBtn1.menu = tk.Menu(mnBtn1)
        mnBtn1.menu.add_command(label='Properties', underline=0, command=self.__info_btn)
        mnBtn1.menu.add_command(label='Sensor Modes', underline=0, command=self.__modes_btn)
        mnBtn1['menu'] = mnBtn1.menu
        #left butt form
        leftfrm = tk.Frame(self.win)
        tk.Button(leftfrm, text="Snap", command=self.snap_buffer_image, width=7).pack(side=tk.TOP, padx=2)
        tk.Button(leftfrm, text="PreView", command=self.preview_pil_video, width=7).pack(side=tk.TOP, padx=2)
        tk.Button(leftfrm, text="QTView", command=self.QTpreview_btn, width=7).pack(side=tk.TOP, padx=2)
        tk.Button(leftfrm, text="Options", command=self.__options_btn, width=7).pack(side=tk.TOP, padx=2)
        #--frame checkbuttons
        ckbtnFrm = tk.Frame(leftfrm)
        tk.Checkbutton(ckbtnFrm, text="H rot", variable=self.hflip, onvalue=1, offvalue=0, command=self.__rotate_ckbox).pack(side=tk.TOP)
        tk.Checkbutton(ckbtnFrm, text="V rot", variable=self.vflip, onvalue=1, offvalue=0, command=self.__rotate_ckbox).pack(side=tk.TOP)
        ckbtnFrm.pack(side=tk.BOTTOM, anchor=tk.W)
        leftfrm.pack(side=tk.LEFT, fill=tk.Y, pady=4)
        #image form
        canvfrm = tk.Frame(self.win, relief=tk.GROOVE,  borderwidth=2)
        self.canvas = tk.Canvas(canvfrm, bg="lightgray", width=320, height=240)
        self.canvas.bind('<Double-Button-1>',self.__bouble_click_view)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        canvfrm.pack(side=tk.TOP, padx=4, pady=4)
        #bottom butt form
        botfrm = tk.Frame(self.win)
        tk.Button(botfrm, text="Foto", command=self.take_foto).pack(side=tk.LEFT, padx=2)
        tk.Button(botfrm, text="Video", command=self.snap_video).pack(side=tk.LEFT, padx=2)
        self.recBtn = tk.Button(botfrm, text="Start Rec", command=self.start_video)
        self.recBtn.pack(side=tk.LEFT, padx=2)
        self.webBtn = tk.Button(botfrm, text="Start Web", command=self.__start_web_4)
        self.webBtn.pack(side=tk.LEFT, padx=2)
        botfrm.pack(side=tk.BOTTOM, fill=tk.X, pady=4)                
        #initialize Camera
        self.__initialize_Camera()


    def __initialize_Camera(self):
        global picamera2_inst
        if Picamera2 is None:
            import_special_libs()
        print(f'Open camera {self.cam_num}')
        if picamera2_inst[self.idx] == None:
            picamera2_inst[self.idx] = Picamera2(self.cam_num)
        self.picam = picamera2_inst[self.idx]
        self.cam_modes = self.picam.sensor_modes
        #cam_prv_cfg = self.picam.create_preview_configuration(lores={"size": (320, 240)}, display="lores", encode="lores")
        self.cam_prv_cfg = self.picam.create_preview_configuration(main={"size": (320, 240)})
        print("--------")
        utl.d_print(self.cam_prv_cfg)
        print("--------")
        self.picam.configure(self.cam_prv_cfg)
        self.picam.start()


    def __close_win(self,e):        
        if self.propInf_win != None:
            self.propInf_win.destroy()
        if self.sensorInf_win != None:
            self.sensorInf_win.destroy()
        if self.picam != None:
            self.picam.stop()
            self.picam = None
        print(f'Close camera {self.cam_num}')
        if gui.mainWin != None:
            gui.mainWin.cam_inst[self.idx] = None


    def __info_btn(self):
        print(f"Info Cam [{self.cam_num}]")
        if self.propInf_win == None:
            self.propInf_win = utl.info_win(self,self.cam_model,self.picam.camera_properties,self.INFO_PROP_ID)
        else:
            print(f"Info [{self.cam_model}] already Open!")
            self.propInf_win.on_top()


    def __modes_btn(self):
        print(f"Modes Cam [{self.cam_num}]")
        if self.sensorInf_win == None:
            self.sensorInf_win = utl.info_win(self,self.cam_model,self.cam_modes,self.INFO_SENSOR_ID)
        else:
            print(f"Modes [{self.cam_model}] already Open!")
            self.sensorInf_win.on_top()


    def __rotate_ckbox(self):
        hflp = self.hflip.get()
        vflp = self.vflip.get()
        print('hflip='+str(hflp)+'  vflip='+str(vflp))
        self.picam.stop()
        self.cam_prv_cfg["transform"] = Transform(hflip=hflp, vflip=vflp)
        self.picam.configure(self.cam_prv_cfg)
        self.picam.start()
        if self.preview_on:
            self.picam.stop_preview()
            self.picam.start_preview(Preview.QT, width=320, height=240)


    #----------------------------------
    #default QT preview using picamera2
    def QTpreview_btn(self):
        if not self.preview_on:
            self.preview_on = True
            self.picam.stop_preview()
            self.picam.start_preview(Preview.QT, width=320, height=240)
        else:
            self.preview_on = False
            self.picam.stop_preview()
            self.picam.start_preview(Preview.NULL)

    #----------------------------------
    #preview foto using PIL
    def snap_pil_image(self):
        print('snap PIL image ...')
        pilimg = self.picam.capture_image('main')
        print(pilimg.size)
        self.tkimg = ImageTk.PhotoImage(pilimg)
        self.canvas.create_image(1,1,anchor=tk.NW,image=self.tkimg)
        self.canvas.update()

    #----------------------------------
    #test foto using buffer caprure
    def snap_buffer_image(self):
        print('snap buffer image ...')
        print('--------')
        utl.d_print(self.picam.camera_configuration())
        print('--------')
        buffer = self.picam.capture_buffer()
        config = self.picam.camera_configuration()["main"]
        #pilimg = self.picam.helpers.make_image(buffer, config)
        pilimg = scutl.make_pil_image(buffer, config)
        self.tkimg = ImageTk.PhotoImage(pilimg)
        self.canvas.create_image(1,1,anchor=tk.NW,image=self.tkimg)
        self.canvas.update()


    #----------------------------------
    #preview video using PIL
    def preview_pil_video(self):
        if not self.pilview_on:
            # start PIL thread
            print('preview PIL start ...')
            self.pilview_on = True
            self.win.after(100,self.__pil_image_loop)
        else:
            self.pilview_on = False


    def __pil_image_loop(self):
        if self.fullview_on:
            return
        #pilimg = self.picam.capture_image('main')
        buffer = self.picam.capture_buffer()
        config = self.picam.camera_configuration()["main"]
        pilimg = scutl.make_pil_image(buffer, config)
        self.tkimg = ImageTk.PhotoImage(pilimg)
        #print(pilimg.size)
        if self.pvimg == None:
            self.pvimg = self.canvas.create_image(1,1,anchor=tk.NW,image=self.tkimg)
        else:
            self.canvas.itemconfig(self.pvimg, image=self.tkimg)
        if self.pilview_on:
            self.win.after(100,self.__pil_image_loop)

    #----------------------------------
    #full screen mode
    def __bouble_click_view(self,e):
        print(f'bouble_click_view of [{self.cam_model}]')
        if self.pilview_on:
            self.fullview_on=True
            view = full_screen_view(self.idx, self.cam_prv_cfg)
            if view.win!=None:
                set_modal(view.win)
            print('fullscreen exit')
            self.fullview_on=False
            self.picam.stop()
            cam_config_size(self.cam_prv_cfg, (320,240))
            self.picam.align_configuration(self.cam_prv_cfg)
            print("--------")
            utl.d_print(self.cam_prv_cfg)
            print("--------")
            try:
                self.picam.configure(self.cam_prv_cfg)
            except Exception as e:
                print("Error picam.configure: ", e.__str__())
                self.win.destroy()
                return
            self.picam.start()
            self.win.after(100,self.__pil_image_loop)

    #----------------------------------
    #take foto files support jpg, png, bmp, ...
    def take_foto(self):
        print('capture_file...')
        opt.update_options()
        self.picam.options['quality'] = opt.cam_options["foto"]["quality"]
        self.picam.options['compress_level'] = opt.cam_options["foto"]["compression"]
        capture_config = self.picam.create_still_configuration()
        capture_config["transform"] = Transform(hflip=self.hflip.get(), vflip=self.vflip.get())
        capture_config["main"]["size"] = opt.cam_options["foto"]["size"]
        #print("--------")
        #utl.d_print(capture_config)
        #print("--------")        
        foto_path = utl.get_filename(opt.cam_options,"foto")
        print('save foto to path: '+ foto_path)
        self.picam.switch_mode_and_capture_file(capture_config, foto_path)

    #----------------------------------
    def get_video_quality(self,quality):
        if quality == "very_low":
            return Quality.VERY_LOW
        if quality == "low":
            return Quality.LOW
        elif quality == "medium":
            return Quality.MEDIUM
        elif quality == "high":
            return Quality.HIGH
        elif quality == "very_high":
            return Quality.VERY_HIGH
        else:
            return Quality.MEDIUM

    #take video files 10sec in different formats using different encoders
    #auto video snap
    def snap_auto_video(self, size=(1280, 960), quality="medium", duration=10, path="test.mp4"):
        print('snap_auto_video.. duration='+str(duration)+' sec  path='+path)
        video_qual = self.get_video_quality(quality)
        video_conf = self.picam.create_video_configuration()
        video_conf["transform"] = Transform(hflip=self.hflip.get(), vflip=self.vflip.get())
        cam_config_size(video_conf, size)
        self.picam.align_configuration(video_conf)        
        self.picam.stop()
        self.picam.start_and_record_video(path, config=video_conf, duration=duration, quality=video_qual, audio=True)
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()


    def snap_h264_video(self, size=(1280, 960), quality="medium", duration=10, path="test.h264"):
        print('snap_h264_video.. duration='+str(duration)+' sec  path='+path)
        video_qual = self.get_video_quality(quality)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        video_conf["transform"] = Transform(hflip=self.hflip.get(), vflip=self.vflip.get())
        cam_config_size(video_conf, size)
        self.picam.align_configuration(video_conf)
        self.picam.configure(video_conf)
        encoder = H264Encoder()
        self.picam.start_recording(encoder, path, quality=video_qual)
        tm.sleep(duration)
        self.picam.stop_recording()
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()


    def snap_mjpeg_video(self, size=(1280, 960), quality="medium", duration=10, path="test.mjpeg"):
        print('snap_mjpeg_video.. duration='+str(duration)+' sec  path='+path)
        video_qual = self.get_video_quality(quality)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        video_conf["transform"] = Transform(hflip=self.hflip.get(), vflip=self.vflip.get())
        cam_config_size(video_conf, size)
        self.picam.align_configuration(video_conf)
        self.picam.configure(video_conf)
        encoder = MJPEGEncoder()
        self.picam.start_recording(encoder, path, quality=video_qual)
        tm.sleep(duration)
        self.picam.stop_recording()
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()


    def snap_jpeg_video(self, size=(1280, 960), quality="medium", duration=10, path="test4.jpg"):
        print('snap_jpeg_video.. duration='+str(duration)+' sec  path='+path)
        video_qual = self.get_video_quality(quality)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        video_conf["transform"] = Transform(hflip=self.hflip.get(), vflip=self.vflip.get())
        cam_config_size(video_conf, size)
        self.picam.align_configuration(video_conf)
        self.picam.configure(video_conf)
        encoder = JpegEncoder()
        self.picam.start_recording(encoder, path, quality=video_qual)
        tm.sleep(duration)
        self.picam.stop_recording()
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()


    def snap_raw_video(self, size=(1280, 960), quality="medium", duration=10, path="test.raw"):
        print('snap_raw_video.. duration='+str(duration)+' sec  path='+path)
        video_qual = self.get_video_quality(quality)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        video_conf["transform"] = Transform(hflip=self.hflip.get(), vflip=self.vflip.get())
        cam_config_size(video_conf, size)
        self.picam.align_configuration(video_conf)
        print("---video conf-----")
        utl.d_print(video_conf)
        print("--------")
        self.picam.configure(video_conf)
        encoder = Encoder()
        self.picam.start_recording(encoder, path, quality=video_qual)
        tm.sleep(duration)
        self.picam.stop_recording()
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()


    #FFMPEG video snap
    def snap_ffmpeg_video(self, size=(1280, 960), quality="medium", duration=10, path="test.mp4"):
        print('snap_ffmpeg_video.. duration='+str(duration)+' sec  path='+path)
        video_qual = self.get_video_quality(quality)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        video_conf["transform"] = Transform(hflip=self.hflip.get(), vflip=self.vflip.get())
        cam_config_size(video_conf, size)
        self.picam.align_configuration(video_conf)
        print("---video conf-----")
        utl.d_print(video_conf)
        print("--------")
        self.picam.configure(video_conf)
        print("---camera conf-----")
        utl.d_print(self.picam.camera_configuration())
        print("--------")        
        encoder = H264Encoder()
        audioSync = opt.cam_options["video"]["audio_sync"]
        output = FfmpegOutput(path, audio=True, audio_sync=audioSync)
        self.picam.start_recording(encoder, output, quality=video_qual)
        tm.sleep(duration)
        self.picam.stop_recording()
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()


    def snap_video(self):
        opt.update_options()
        encod = opt.cam_options["video"]["encoder"]
        duration = opt.cam_options["video"]["duration"]
        size = opt.cam_options["video"]["size"]
        quality = opt.cam_options["video"]["quality"]
        path = utl.get_filename(opt.cam_options,"video")
        if encod == "auto":
            self.snap_auto_video(size=size, quality=quality, duration=duration, path=path)
        elif encod == "FFMPEG":
            self.snap_ffmpeg_video(size=size, quality=quality, duration=duration, path=path)
        elif encod == "H264":    
            self.snap_h264_video(size=size, quality=quality, duration=duration, path=path)
        elif encod == "MJPEG":    
            self.snap_mjpeg_video(size=size, quality=quality, duration=duration, path=path)
        elif encod == "jpeg":    
            self.snap_jpeg_video(size=size, quality=quality, duration=duration, path=path)
        elif encod == "none":
            self.snap_raw_video(size=size, quality=quality, duration=duration, path=path)    


    #----------------------------------
    #video file support all video formats (.mp4, .avi, .ts, .mov, ...)
    def start_video(self):
        opt.update_options()
        path = utl.get_filename(opt.cam_options,"video", fix=False)
        print('start recording video to path: '+ path)
        video_qual = self.get_video_quality(opt.cam_options["video"]["quality"])
        self.recBtn.config(text="Stop Rec", fg="red", activeforeground="red", font="bold", command=self.stop_video)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        video_conf["transform"] = Transform(hflip=self.hflip.get(), vflip=self.vflip.get())
        cam_config_size(video_conf, opt.cam_options["video"]["size"])
        self.picam.align_configuration(video_conf)
        print("---video conf-----")
        utl.d_print(video_conf)
        print("--------")
        self.picam.configure(video_conf)
        print("---camera conf-----")
        utl.d_print(self.picam.camera_configuration())
        print("--------")
        encoder = H264Encoder()
        audioSync = opt.cam_options["video"]["audio_sync"]
        output = FfmpegOutput(path, audio=True, audio_sync=audioSync)
        self.picam.start_recording(encoder, output, quality=video_qual)

    def stop_video(self):
        print('stop recording video.. ')
        self.recBtn.config(text="Start Rec", fg="black", activeforeground="black", font="TkDefaultFont", command=self.start_video)
        self.picam.stop_recording()
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()

    #----------------------------------
    #standard live streams (using Ffmpeg)
    #HSL:  web/vlc: http://<IP_PI>:8000/stream.m3u8 
    #DASH: web/vlc: http://<IP_PI>:8000/stream.mpd
    #UDP:  vlc: udp://@:8000
    def __start_web(self):
        print('start live stream.. ')
        self.webBtn.config(text="Stop Web", fg="red", activeforeground="red", font="bold", command=self.__stop_web)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        cam_config_size(video_conf, [640,480])
        self.picam.align_configuration(video_conf)
        print("---video conf-----")
        utl.d_print(video_conf)
        print("--------")
        self.picam.configure(video_conf)
        print("---camera conf-----")
        utl.d_print(self.picam.camera_configuration())
        print("--------")
        encoder = H264Encoder()
        output = FfmpegOutput("-f hls -fflags nobuffer -hls_time 4 -hls_list_size 3 -hls_flags delete_segments -hls_allow_cache 0 stream.m3u8", audio=True)
        #output = FfmpegOutput("-f dash -window_size 3 -use_template 1 -use_timeline 1 stream.mpd", audio=True)
        #output = FfmpegOutput("-f mpegts udp://192.168.2.2:8000")  ##<IP_WINDOWS_PC>
        self.webserver = web.simpleServer()
        self.webserver.start()
        self.picam.start_recording(encoder, output)



    def __stop_web(self):
        print('stop web.. ')
        self.webBtn.config(text="Start Web", fg="black", activeforeground="black", font="TkDefaultFont", command=self.__start_web)
        self.picam.stop_recording()
        self.picam.stop()
        self.webserver.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()

    #----------------------------------
    #udp test:
    #pi test: rpicam-vid -t 0 --inline -o udp://<IP_WINDOWS_PC>:8000
    #vlc: udp://@:8000 or udp/h264://@:8000
    def __start_web_2(self):
        print('start udp live stream.. ')
        self.webBtn.config(text="Stop Web", fg="red", activeforeground="red", font="bold", command=self.__stop_web_2)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        cam_config_size(video_conf, [640,480])
        self.picam.align_configuration(video_conf)
        self.picam.configure(video_conf)
        #encoder = H264Encoder()
        encoder = MJPEGEncoder()
        self.sock =  socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #sock.connect(("127.0.0.1", 8000))       #<localhost>
        self.sock.connect(("192.168.2.5", 8000)) #<IP_WINDOWS_PC>
        stream = self.sock.makefile("wb")
        self.picam.start_recording(encoder, FileOutput(stream))

    def __stop_web_2(self):
        print('stop web.. ')
        self.webBtn.config(text="Start Web", fg="black", activeforeground="black", font="TkDefaultFont", command=self.__start_web_2)
        self.picam.stop_recording()
        self.picam.stop()
        self.sock.close()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()

    #----------------------------------
    #tcp test:
    #pi test: rpicam-vid -t 0 --inline --listen -o tcp://0.0.0.0:8000
    #vlc: tcp://<IP_PI>:8000 or tcp/h264://<IP_PI>:8000
    def __start_web_3(self):
        print('start tcp live stream.. ')
        self.webBtn.config(text="Stop Web", fg="red", activeforeground="red", font="bold", command=self.__stop_web_3)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        cam_config_size(video_conf, [640,480])
        self.picam.align_configuration(video_conf)
        self.picam.configure(video_conf)
        self.encoder = H264Encoder()
        #self.encoder = MJPEGEncoder()
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', 8000))
        self.server_sock.listen(1)
        self.tcp_closed = False
        self.sock = None
        self.tcp_thread=thrd.Thread(target=self.__wait_tcp_client_3)
        self.tcp_thread.start()

    def __wait_tcp_client_3(self):
        while True:
            print('Waiting for TCP connection...')
            try:
                self.sock, addr = self.server_sock.accept()
            except Exception as e:
                print(f'TCP server socket closed: {e}')
                break
            if self.tcp_closed:
                break
            print(f'Client connected from {addr}')
            self.picam.stop_recording()
            #set TCP_NODELAY to reduce latency
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            stream = self.sock.makefile("wb")
            self.picam.start_recording(self.encoder, FileOutput(stream), quality=Quality.VERY_LOW)
            print('Starting Recording to TCP stream...')

    def __stop_web_3(self):
        print('stop web.. ')
        self.webBtn.config(text="Start Web", fg="black", activeforeground="black", font="TkDefaultFont", command=self.__start_web_3)
        self.picam.stop_recording()
        self.tcp_closed = True
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()
        if self.sock!=None:
            self.sock.close()
        self.tcp_thread.join()
        print('tcp server closed.')
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()

    #----------------------------------
    #web page test
    #pc web: http://192.168.1.31:8000
    def __start_webPage(self):
        print('start web Page.. ')
        self.webBtn.config(text="Stop Web", fg="red", activeforeground="red", font="bold", command=self.__stop_webPage)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        cam_config_size(video_conf, [640,480])
        self.picam.align_configuration(video_conf)
        print("---video conf-----")
        utl.d_print(video_conf)
        print("--------")
        self.picam.configure(video_conf)
        print("---camera conf-----")
        utl.d_print(self.picam.camera_configuration())
        print("--------")
        #encoder = JpegEncoder()
        encoder = MJPEGEncoder()
        output = web.StreamingOutput()
        self.picam.start_recording(encoder, FileOutput(output))
        self.webserver = web.pageServer(output)
        self.webserver.start()


    def __stop_webPage(self):
        print('stop web.. ')
        self.webBtn.config(text="Start Web", fg="black", activeforeground="black", font="TkDefaultFont", command=self.__start_webPage)
        self.picam.stop_recording()
        self.picam.stop()
        self.webserver.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()

    #----------------------------------
    #tcp custom server:
    #send cupture buffer on request
    def __start_web_4(self):
        print('start tcp server.. ')
        self.webBtn.config(text="Stop Web", fg="red", activeforeground="red", font="bold", command=self.__stop_web_4)
        self.picam.stop()
        video_conf = self.picam.create_video_configuration()
        cam_config_size(video_conf, [640,480])
        self.picam.align_configuration(video_conf)
        self.picam.configure(video_conf)
        self.picam.start()
        #open socket ...
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', 8000))
        self.server_sock.listen(1)
        self.tcp_closed = False
        self.sock = None
        self.tcp_thread=thrd.Thread(target=self.__wait_tcp_client_4)
        self.tcp_thread.start()


    def __send_image_cfg(self):
        config = self.picam.camera_configuration()["main"]
        ackInfo = {'Cmd':scutl.CMD_IMG_CFG_ACK, 'Config':config}
        scutl.send_dict(self.sock, ackInfo)


    def __send_image_buffer(self):
        buffer = self.picam.capture_buffer()
        ackInfo = {'Cmd':scutl.CMD_IMG_BUF_ACK, 'Buffer':buffer}
        scutl.send_dict(self.sock, ackInfo)


    def __parse_tcp_cmds_4(self):
        while True:
            try:
                reqInfo = scutl.recv_dict(self.sock)
            except Exception as e:
                print(f'TCP server socket closed: {e}')
                return
            if reqInfo==None:
                    return
            #print('received dict:', reqInfo)
            try:
                if reqInfo['Cmd'] == scutl.CMG_IMG_CFG_REQ:
                    self.__send_image_cfg()
                if reqInfo['Cmd'] == scutl.CMG_IMG_BUF_REQ:
                    self.__send_image_buffer()
            except Exception as e:
                print(f'TCP server send: {e}')
                return


    def __wait_tcp_client_4(self):
        while True:
            print('Waiting for TCP connection...')
            try:
                self.sock, addr = self.server_sock.accept()
            except Exception as e:
                print(f'TCP server socket closed: {e}')
                break
            if self.tcp_closed:
                break
            print(f'Client connected from {addr}')            
            self.__parse_tcp_cmds_4()


    def __stop_web_4(self):
        print('stop tcp server.. ')
        self.webBtn.config(text="Start Web", fg="black", activeforeground="black", font="TkDefaultFont", command=self.__start_web_4)    
        self.tcp_closed = True
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()
        if self.sock!=None:
            self.sock.close()
        self.tcp_thread.join()
        print('tcp server closed.')
        self.picam.stop()
        self.picam.switch_mode(self.cam_prv_cfg)
        self.picam.start()
    #----------------------------------


    def __options_btn(self):
        print('options button pressed')
        optWin = opt.options_win(self.cam_model,self.picam.camera_properties,self.picam.sensor_modes)
        set_modal(optWin.win)


    def on_top(self):
        if self.win.winfo_exists():
            self.win.lift()
        else:
            print(f'Camera window {self.cam_num} no longer exists')


    def close(self):
        self.win.destroy()

    def run(self):
        self.win.mainloop()        

##############################################################################################
# Full Screen Preview Window Class
##############################################################################################
class full_screen_view:

    def __init__(self, cam_idx, cam_cfg):
        self.quit=False
        self.pvimg=None
        self.win = tk.Toplevel()
        self.win.attributes('-fullscreen', True)
        self.canvas = tk.Canvas(self.win, bg="black", highlightthickness=0)
        self.canvas.bind('<Double-Button-1>',self.__bouble_click_view)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        self.canvas.update()
        viewsize = [self.canvas.winfo_width(),  self.canvas.winfo_height()]
        print(f'canvas width={viewsize[0]} height={viewsize[1]}')
        if viewsize[0] > 800:
            self.time=1000
        else:
            self.time=100
        self.__initialize_Camera(cam_idx,cam_cfg,viewsize)


    def __initialize_Camera(self, idx, cfg, viewsize):
        self.picam = picamera2_inst[idx]
        self.picam.stop()
        cam_modes = self.picam.sensor_modes
        self.__select_size(cam_modes,viewsize)
        cam_config_size(cfg,viewsize)
        self.picam.align_configuration(cfg)
        print("--------")
        utl.d_print(cfg)
        print("--------")
        try:
            self.picam.configure(cfg)
        except Exception as e:
            print("Error picam.configure: ", e.__str__())
            self.win.destroy()
            self.win = None
            return
        self.picam.start()
        self.win.after(100,self.__pil_image_loop)


    def __select_size(self,modes,viewsize):
        oksize = viewsize
        for mode in modes:
            if 'size' in mode:
                modesize = mode['size']
                print(modesize)
                if modesize[0] > viewsize[0]:
                    break
                if modesize[1] > viewsize[1]:
                    break
                oksize = list(modesize)
        #use of [:] change arg viewsize
        viewsize[:] = oksize


    def __pil_image_loop(self):
        if self.quit:
            return
        #pilimg = self.picam.capture_image('main')
        buffer = self.picam.capture_buffer()
        config = self.picam.camera_configuration()["main"]
        pilimg = scutl.make_pil_image(buffer, config)
        self.tkimg = ImageTk.PhotoImage(pilimg)
        #print(pilimg.size)
        if self.pvimg == None:
            x = (self.canvas.winfo_width() - pilimg.width) / 2
            y = (self.canvas.winfo_height() - pilimg.height) / 2
            self.pvimg = self.canvas.create_image(x, y, anchor=tk.NW, image=self.tkimg)
        else:
            self.canvas.itemconfig(self.pvimg, image=self.tkimg)
        self.win.after(self.time,self.__pil_image_loop)


    def __bouble_click_view(self,e):
        self.quit=True
        self.win.destroy()
