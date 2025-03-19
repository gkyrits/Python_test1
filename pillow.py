#import PIL
import PIL.Image as Image
import PIL.ImageDraw as ImgDraw
import PIL.ImageFont as ImgFont

img_size=(160,128)
font_nm="arialbd.ttf"

ip_addr="192.168.1.17"
temperture="25.5"
humidity="65"
time="25-02-2025  12:00:00"

#get available fonts
def print_fonts():
        import matplotlib.font_manager
        system_fonts = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
        for i in system_fonts:
            print(i)


def test1():
    img=Image.new('RGB',img_size,(0, 150, 255))
    draw=ImgDraw.Draw(img)
    myFont = ImgFont.truetype(font_nm, 16)
    draw.rectangle((0,0,img_size[0]-1,img_size[1]-1),fill=None,outline='red',width=1)
    #draw.text((10,5),'hello',fill='white',font=myFont)
    draw.text((10,5),'hello',fill='white',font=myFont,stroke_width=1,stroke_fill='black')
    img2=Image.open('pillow/home2-300x300.png')
    img2=img2.resize((img_size[0]-10,img_size[1]-30))
    img.paste(img2,(5,25),mask=img2)
    img.show()



def test2():
    strk1 = 1
    font1 = ImgFont.truetype(font_nm, 12)
    font2 = ImgFont.truetype(font_nm, 14)
    font3 = ImgFont.truetype(font_nm, 16)
    font4 = ImgFont.truetype(font_nm, 20)
    posx=10
    posy=10
    img=Image.new('RGB',img_size,(0, 150, 255))
    draw=ImgDraw.Draw(img)    
    draw.rectangle((0,0,img_size[0]-1,img_size[1]-1),fill=None,outline='red',width=1)    

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

    img.show()



if __name__ == '__main__':
    print_fonts()
    #test2()
