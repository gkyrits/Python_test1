from gpiozero import Button


key1 = Button(18)
key2 = Button(23)
key3 = Button(24)

def key_action(press,but) :
	if(press) :
		print("Key %d pressed!" % but)
	else :
		print("Key %d released!" % but)	
		
def key1_pressed():
	key_action(True,1)
	
def key2_pressed():
	key_action(True,2)
		
def key3_pressed():
	key_action(True,3)
	
def key1_released():
	key_action(False,1)
	
def key2_released():
	key_action(False,2)
	
def key3_released():
	key_action(False,3)
	
print("Press a LCD Key...")
key1.when_pressed = key1_pressed
key2.when_pressed = key2_pressed
key3.when_pressed = key3_pressed	
key1.when_released = key1_released
key2.when_released = key2_released
key3.when_released = key3_released
x = input("press enter for exit\n")
