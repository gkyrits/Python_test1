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


def clear_matrix(col):
    if sense is None:
        return
    led_matrix[:] = [col.copy() for _ in led_matrix]


def set_matrix(x, y, col):
    if sense is None:
        return
    if not (0 <= x < 8 and 0 <= y < 8):
        raise ValueError("x and y must be between 0 and 7")
    if len(col) != 3:
        raise ValueError("col must contain three RGB values")
    led_matrix[y * 8 + x] = list(col)


def intro():
    test_matrix()
    tm.sleep(2)
    clear_matrix(Black_col)
    set_matrix(4,4,get_color(9))
    sense.set_pixels(led_matrix)
    tm.sleep(2)
    clear_matrix(Black_col)
    sense.set_pixels(led_matrix)


def draw_rect(x, y, w, h, col):
    if sense is None:
        return
    if not (0 <= x < 8 and 0 <= y < 8):
        raise ValueError("x and y must be between 0 and 7")
    if not (1 <= abs(w) <= 8 and 1 <= abs(h) <= 8):
        raise ValueError("w and h must be between 1 and 8 or -1 and -8")
    if len(col) != 3:
        raise ValueError("col must contain three RGB values")
    # direction depends on the sign of w/h; size is abs(w)/abs(h) cells
    x_dir = 1 if w > 0 else -1
    y_dir = 1 if h > 0 else -1
    x_end = x + (abs(w) - 1) * x_dir
    y_end = y + (abs(h) - 1) * y_dir
    x0, x1 = sorted((x, x_end))
    y0, y1 = sorted((y, y_end))
    # clip the drawable range to the matrix bounds (0-7)
    xr0, xr1 = max(0, x0), min(7, x1)
    yr0, yr1 = max(0, y0), min(7, y1)
    # top and bottom edges
    for xi in range(xr0, xr1 + 1):
        if 0 <= y0 <= 7:
            set_matrix(xi, y0, col)
        if y1 != y0 and 0 <= y1 <= 7:
            set_matrix(xi, y1, col)
    # left and right edges
    for yi in range(yr0, yr1 + 1):
        if 0 <= x0 <= 7:
            set_matrix(x0, yi, col)
        if x1 != x0 and 0 <= x1 <= 7:
            set_matrix(x1, yi, col)


def intro2(delay): #delay in sec
    clear_matrix(Black_col)
    draw_rect(3,3,2,2,White_col)
    sense.set_pixels(led_matrix)
    tm.sleep(delay)
    clear_matrix(Black_col)
    draw_rect(2,2,4,4,White_col)
    sense.set_pixels(led_matrix)
    tm.sleep(delay)
    clear_matrix(Black_col)
    draw_rect(1,1,6,6,White_col)
    sense.set_pixels(led_matrix)
    tm.sleep(delay)    
    clear_matrix(Black_col)
    draw_rect(0,0,8,8,White_col)
    sense.set_pixels(led_matrix)
    tm.sleep(delay)
    clear_matrix(Black_col)
    sense.set_pixels(led_matrix)


def cli():
    while True:
        print('\n1.exit\n2.clear\n3.colors\n4.hello\n5.intro')
        try:
            choice = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            choice = '1'
        if choice=='1':
            sense.clear()
            return()
        elif choice=='2':
            clear_matrix(Black_col)
            sense.set_pixels(led_matrix)
        elif choice=='3':
            colors()
        elif choice=='4':
            hello()
        elif choice=='5':
            intro2(0.2)
        else:
            print('unknown option: ' + choice)


if __name__ == '__main__':
    print("Start PiHat")
    if not init():
        print("Fail Start. End.")
        exit()
    cli()
    print("End.")
