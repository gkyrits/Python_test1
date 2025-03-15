
import PIL.Image as Image
import PIL.ImageDraw as ImgDraw
import PIL.ImageFont as ImgFont

LCD_SIZE=(160,128)

IPADDR="192.168.1.17"
TEMPER="25.5"
HUMID="65"
TIME="25-02-2025  12:00:00"

font_nm="arialbd.ttf"


def draw_main(ip_addr=IPADDR,temperture=TEMPER,humidity=HUMID,time=TIME):
    strk1 = 1
    font1 = ImgFont.truetype(font_nm, 12)
    font2 = ImgFont.truetype(font_nm, 14)
    font3 = ImgFont.truetype(font_nm, 16)
    font4 = ImgFont.truetype(font_nm, 20)
    posx=10
    posy=10
    img=Image.new('RGB',LCD_SIZE,(0, 150, 255))
    draw=ImgDraw.Draw(img)    
    draw.rectangle((0,0,LCD_SIZE[0]-1,LCD_SIZE[1]-1),fill=None,outline='red',width=1)    

    draw.text((posx,posy),'IP',fill='white',font=font3,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+40,posy),ip_addr,fill='yellow',font=font3,stroke_width=strk1,stroke_fill='black')

    posy+=20+10
    draw.text((posx,posy),'Temperture',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+80,posy-5),temperture,fill='red',font=font4,stroke_width=strk1,stroke_fill='white')

    posy+=25
    draw.text((posx,posy),'Humidity',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
    draw.text((posx+80,posy-5),humidity,fill='green',font=font4,stroke_width=strk1,stroke_fill='white')

    posy+=20+20
    #draw.text((posx,posy),'Time:',fill='white',font=font1,stroke_width=strk1,stroke_fill='black')
    draw.text((posx,posy),time,fill='white',font=font2,stroke_width=strk1,stroke_fill='black')

    return img



if __name__ == '__main__':
    draw_main().show()