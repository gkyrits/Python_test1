import time
import PIL.Image as Image
import PIL.ImageDraw as ImgDraw
import PIL.ImageFont as ImgFont


LCD_SIZE=(160,128)

WINDOWS=0
if WINDOWS:
    WORK_PATH="C:\MyFiles\WORK\python\Python_test1\lcd18_game"
else:    
    WORK_PATH="/home/gkyr/Work/Python_test1/lcd18_game/"

IPADDR="192.168.1.17"
TEMPER="25.5"
HUMID="65"
TIME="25-02-2025  12:00:00"

font_nm=WORK_PATH+"Font/arialbd.ttf"

disp = None
main_img_cnt=0
imglist = ['01','03','04','05','06','07','08','14','16','17','18','19','20']
imgidx=0
seconds_cnt=0

def get_main_img():
    global imgidx,imglist,seconds_cnt
    seconds_cnt+=1
    if seconds_cnt==60:
        seconds_cnt=0
        imgidx+=1
        if imgidx >= len(imglist):
            imgidx=0
    image_file = WORK_PATH+"pic/Sample" + imglist[imgidx] + ".jpg"
    img = Image.open(image_file)
    img = img.resize((LCD_SIZE[0], LCD_SIZE[1]), resample = Image.BILINEAR)
    return img
  

def draw_main(ip_addr=IPADDR,temperture=TEMPER,humidity=HUMID,time=TIME):
    strk1 = 1    
    font1 = ImgFont.truetype(font_nm, 12)
    font2 = ImgFont.truetype(font_nm, 14)
    font3 = ImgFont.truetype(font_nm, 16)
    font4 = ImgFont.truetype(font_nm, 24)
    posx=10
    posy=10
    #img=Image.new('RGB',LCD_SIZE,(0, 80, 255))
    img=get_main_img()
    draw=ImgDraw.Draw(img)    
    draw.rectangle((0,0,LCD_SIZE[0]-1,LCD_SIZE[1]-1),fill=None,outline='red',width=1)    

    draw.text((posx,posy),'IP',fill='white',font=font3,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+40,posy),ip_addr,fill='yellow',font=font3,stroke_width=strk1,stroke_fill='black')

    posy+=30
    draw.text((posx,posy),'Temperture',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+80,posy-5),temperture,fill='red',font=font4,stroke_width=strk1,stroke_fill='white')

    posy+=30
    draw.text((posx,posy),'Humidity',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+80,posy-5),humidity,fill='green',font=font4,stroke_width=strk1,stroke_fill='white')

    posy+=35
    #draw.text((posx,posy),'Time:',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
    draw.text((posx,posy),time,fill='white',font=font2,stroke_width=strk1,stroke_fill='black')

    return img



def draw_imageSlide():
    global imgidx,imglist    
    image_file = WORK_PATH+"pic/Sample" + imglist[imgidx] + ".jpg"
    img = Image.open(image_file)
    img = img.resize((LCD_SIZE[0], LCD_SIZE[1]), resample = Image.BILINEAR)
    imgidx+=1
    if imgidx >= len(imglist):
        imgidx=0
    return img    


def lcd_init():
    global disp
    try:
        import lcd18driver as lcd           
    except Exception as e:
        print("Error importing lcd18driver: ", e.__str__())
        return        
    disp = lcd.LCD_1inch8()
    disp.Init()
    # Clear display.
    disp.clear()
    #Set the backlight to 100
    disp.bl_DutyCycle(50)

def lcd_show(img):
    if disp != None:
        disp.ShowImage(img)

def lcd_show2(img):
    if disp != None:
        disp.ShowImage2(img)        

def lcd_testShow():
    lcd_init()
    lcd_show(draw_main())
    while True:
        time.sleep(1)


if __name__ == '__main__':
    #draw_main().show()
    lcd_testShow()

