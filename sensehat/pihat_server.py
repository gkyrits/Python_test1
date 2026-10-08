import time as tm

LED_LUM_HI	= 255
LED_LUM_LOW	= 128
sense=None

White_col = [LED_LUM_HI, LED_LUM_HI, LED_LUM_HI]  # White
Black_col = [0, 0, 0]  # Black
O = Black_col
X = White_col

led_matrix = [
O, O, O, O, O, O, O, O,  
O, O, O, O, O, O, O, O,
O, O, O, O, O, O, O, O,
O, O, O, O, O, O, O, O,
O, O, O, O, O, O, O, O,
O, O, O, O, O, O, O, O,
O, O, O, O, O, O, O, O,
O, O, O, O, O, O, O, O
]

def init():
    global sense
    try:
        from sense_hat import SenseHat
        sense = SenseHat()
    except Exception as e:
        print("Error importing SenseHat: ", e.__str__())
        return False
    sense.clear()
    sense.set_rotation(0)
    return True


def hello():
    if sense == None:
        return         
    sense.show_message("Hello", text_colour=[0,       LED_LUM_LOW, 0])
    sense.show_message("Sense", text_colour=[0,       0,       LED_LUM_LOW])
    sense.show_message("Hat"  , text_colour=[LED_LUM_LOW, 0,       0])    


def exist():
    if sense != None:
        return True
    else:
        return False

def colors():
    col_ar = (LED_LUM_HI,LED_LUM_LOW,0)
    idx=0
    x=0
    y=0
    for R in col_ar:
        for G in col_ar:
            for B in col_ar:
                col = (R,G,B)
                sense.set_pixel(x,y,col)
                idx = idx+1
                print(idx,':',x,y,col)
                x=x+1
                if x>7:
                    x=0
                    y=y+1


def get_color(idx):
    col_ar = (LED_LUM_HI, LED_LUM_LOW, 0)
    if not 1 <= idx <= len(col_ar) ** 3:
        raise ValueError("idx must be between 1 and 27")

    idx -= 1  # Convert the displayed 1-based index to a 0-based offset
    return (
        col_ar[idx // 9],
        col_ar[(idx // 3) % 3],
        col_ar[idx % 3],
    )


def test_matrix():
    if sense is None:
        return
    matrix_size = len(led_matrix)    
    for x in range(0,matrix_size):
        led_matrix[x]=Black_col
    sense.set_pixels(led_matrix)
    tm.sleep(2)
    for x in range(0,matrix_size):
        led_matrix[x]=White_col
    sense.set_pixels(led_matrix)  


def clear_matrix():
    if sense is None:
        return
    led_matrix[:] = [Black_col.copy() for _ in led_matrix]


def set_matrix(x, y, col):
    if sense is None:
        return
    if not (0 <= x < 8 and 0 <= y < 8):
        raise ValueError("x and y must be between 0 and 7")
    if len(col) != 3:
        raise ValueError("col must contain three RGB values")
    led_matrix[y * 8 + x] = list(col)
    #sense.set_pixels(led_matrix)



if __name__ == '__main__':
    print("Start PiHat")
    if not init():
        print("Fail Start. End.")
        exit()
    #hello()    
    colors()
    tm.sleep(2)
    test_matrix()
    tm.sleep(2)
    clear_matrix()
    set_matrix(4,4,get_color(9))
    sense.set_pixels(led_matrix)
    tm.sleep(2)
    clear_matrix()
    sense.set_pixels(led_matrix)
    print("End.")
