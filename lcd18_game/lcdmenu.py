import os
import PIL.Image as Image
import PIL.ImageDraw as ImgDraw
import PIL.ImageFont as ImgFont

LCD_SIZE=(160,128)

MENU_COL = (0, 80, 255)

fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Font')
font_nm="arialbd.ttf"
font1_sz=14
font2_sz=11
menu_cols=7

#menu_items=('Menu','item1','item2','item3','item4','item5','item6','item7','item8','item9','item10')
menu_items=('Menu','item1','item2','item3')
menu_sel=-1
menu_img=None

top_item=0

def draw_menu(img=None, items=menu_items, select=1, color=MENU_COL):
    global menu_items,menu_sel,menu_img,top_item
    menu_items=items
    menu_sel=select
    menu_img=img
    font1 = ImgFont.truetype(os.path.join(fontdir, font_nm), font1_sz)
    font2 = ImgFont.truetype(os.path.join(fontdir, font_nm), font2_sz)
    if img==None:
        img=Image.new('RGB',LCD_SIZE,color)
    draw=ImgDraw.Draw(img)
    pad=6
    #estimage menu height & draw box
    h_itms=len(menu_items)-1
    if h_itms>menu_cols:
        h_itms=menu_cols
    h_pos= pad + (font1_sz+5) + (font2_sz+2)*h_itms + 5
    draw.rectangle((pad,pad,LCD_SIZE[0]-pad,h_pos),fill=color,outline='white',width=1)
    #draw menu items
    posx=pad+3; posy=pad+2    
    draw.text((posx+5,posy),items[0],fill='white',font=font1)
    y_sz=font1_sz+5
    draw.line((pad,pad+y_sz,LCD_SIZE[0]-pad,pad+y_sz),width=1)
    #add items
    posy = pad+y_sz+2
    y_sz=font2_sz+2
    idx=1
    while True:
        if select==idx:
            draw.rectangle((posx+2,posy+1,LCD_SIZE[0]-posx-2,posy+y_sz-1),fill="white")
            draw.text((posx+5,posy),items[idx+top_item],fill=color,font=font2)
        else:    
            draw.text((posx+5,posy),items[idx+top_item],fill='white',font=font2)
        idx += 1
        if idx >= len(items):
            break
        if idx > menu_cols:
            break
        posy += y_sz        
    return img


def get_select():
    return menu_sel+top_item

def reset_select():
    global top_item
    top_item=0


def select_up():
    global menu_items,menu_sel,top_item
    menu_sel -= 1
    if menu_sel<=0:
        menu_sel=1
        if top_item>0:
            top_item -= 1
    return draw_menu(img=menu_img,select=menu_sel)


def select_down():
    global menu_items,menu_sel,top_item
    menu_sel += 1
    if menu_sel >= len(menu_items):
        menu_sel = len(menu_items)-1
    if menu_sel > menu_cols:
        menu_sel = menu_cols
        more_items=len(menu_items)-menu_cols-1
        if more_items > top_item:
            top_item += 1


    return draw_menu(img=menu_img,select=menu_sel)  
    