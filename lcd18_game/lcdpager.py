import time
import os
import PIL.Image as Image
import PIL.ImageDraw as ImgDraw
import PIL.ImageFont as ImgFont

######################
#  SPI/PIN config
######################
SPI_DEV=1    #spi0,spi1
SPI_CS=0     #cs0,cs1,cs2
DC_GPIO=6    #lcd command/data  //6        //24
RST_GPIO=26  #lcd reset          //5 26     //25
BL_GPIO=13   #lcd backlight     //13(PWM1) //22
#---------------------


LCD_SIZE=(160,128)
IPADDR="192.168.1.17"
TEMPER="25.5"
HUMID="65"
PRESSUSE="1024"
TIME="25-02-2025  12:00:00"

font_nm="arialbd.ttf"

disp = None
main_img_cnt=0
imglist = ['01','03','04','05','06','07','08','14','16','17','18','19','20']
imgidx=0
seconds_cnt=0

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font')

def get_main_img():
    global imgidx,imglist,seconds_cnt
    seconds_cnt+=1
    if seconds_cnt==60:
        seconds_cnt=0
        imgidx+=1
        if imgidx >= len(imglist):
            imgidx=0
    image_name =  os.path.join(picdir, "Sample" + imglist[imgidx] + ".jpg")
    img = Image.open(image_name)
    img = img.resize((LCD_SIZE[0], LCD_SIZE[1]), resample = Image.BILINEAR)
    return img


def get_curr_img():
    global imgidx,imglist
    image_name =  os.path.join(picdir, "Sample" + imglist[imgidx] + ".jpg")
    img = Image.open(image_name)
    img = img.resize((LCD_SIZE[0], LCD_SIZE[1]), resample = Image.BILINEAR)
    return img
  

def draw_main(ip_addr=IPADDR,temperture=TEMPER,humidity=HUMID,time=TIME, pressure=PRESSUSE, desc='IN'):
    strk1 = 1    
    font1 = ImgFont.truetype(os.path.join(fontdir, font_nm), 12)
    font2 = ImgFont.truetype(os.path.join(fontdir, font_nm), 14)
    font3 = ImgFont.truetype(os.path.join(fontdir, font_nm), 16)
    font4 = ImgFont.truetype(os.path.join(fontdir, font_nm), 28)
    posx=10
    posy=3
    #img=Image.new('RGB',LCD_SIZE,(0, 80, 255))
    img=get_main_img()
    draw=ImgDraw.Draw(img)    
    draw.rectangle((0,0,LCD_SIZE[0]-1,LCD_SIZE[1]-1),fill=None,outline='red',width=1)    

    draw.text((posx,posy),'IP',fill='white',font=font3,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+35,posy),ip_addr,fill='yellow',font=font3,stroke_width=strk1,stroke_fill='black')

    posy+=20
    draw.text((posx,posy),desc,fill='magenta',font=font2,stroke_width=strk1,stroke_fill='black')    

    posy+=20
    draw.text((posx,posy),'Temperture',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+80,posy-15),temperture,fill='red',font=font4,stroke_width=strk1,stroke_fill='white')    

    posy+=22
    draw.text((posx,posy),'Humidity',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+80,posy-8),humidity,fill='green',font=font4,stroke_width=strk1,stroke_fill='white')
    
    posy+=22
    if(pressure!='0'):
        draw.text((posx,posy),'Pressure',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
        draw.text((posx+80,posy),pressure,fill='cyan',font=font3,stroke_width=strk1,stroke_fill='blue')

    posy+=20
    draw.text((posx,posy),time,fill='white',font=font2,stroke_width=strk1,stroke_fill='black')

    return img



def draw_imageSlide():
    global imgidx,imglist    
    image_name =  os.path.join(picdir, "Sample" + imglist[imgidx] + ".jpg")
    img = Image.open(image_name)
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
    disp = lcd.LCD_1inch8(spi_dev=SPI_DEV,spi_cs=SPI_CS,dc=DC_GPIO,rst=RST_GPIO,bl=BL_GPIO)
    disp.Init()
    # Clear display.
    disp.clear()
    #Set the backlight
    disp.bl_DutyCycle(50)

def lcd_close():
    if disp != None:
        disp.Close()

def ldc_backlight(value):
    #print("set backlight:{}".format(value))
    if disp != None:
        disp.bl_DutyCycle(int(value))

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

