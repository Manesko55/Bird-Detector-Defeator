import time,sys
import RPi.GPIO as GPIO
import time
from DRV8825 import DRV8825
import smbus
import math

if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)

# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62 # address to change rgb
DISPLAY_TEXT_ADDR = 0x3e # address to change text

# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)


# set display text \n for second line(or auto wrap)
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))


#Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    while len(text) < 32: #clears the rest of the screen
        text += ' '
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))


################################################################
# motor functionailty
Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor2 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

def pitch_mirror(c):
    global direction
    direction = ""
    Motor2.SetMicroStep('hardward','fullstep')
    if (c >= 0):
        direction = "forward"
    elif (c < 0):
        direction = "backward"
        c *= -1

    if (direction == "forward"):
        setText_norefresh("up: " + str(c) + " steps " + "/ " + str(round(((360/2048)*c),2)) + " deg")
    else:
        setText_norefresh("down: -" + str(c) + " steps " + "/ -" + str(round(((360/2048)*c),2)) + " deg")


    Motor2.TurnStep(Dir = direction, steps = c, stepdelay = 0.001)      
    Motor2.Stop()
    
    
     
def turn_mirror(c):
    global direction
    direction = ""
    Motor1.SetMicroStep('hardward','fullstep')
    if (c >= 0):
        direction = "forward"
    elif (c < 0):
        direction = "backward"
        c *= -1

    if (direction == "forward"):
        setText_norefresh("l/r: " + str(c) + " steps " + "/ " + str(round(((360/2048)*c),2)) + " deg")
    else:
        setText_norefresh("l/r: -" + str(c) + " steps " + "/ -" + str(round(((360/2048)*c),2)) + " deg")


    Motor1.TurnStep(Dir = direction, steps = c, stepdelay = 0.001)      
    Motor1.Stop()

def stop_motors():
    Motor1.Stop()
    Motor2.Stop()


################################################################
# laser functionailty
GPIO.setup(26, GPIO.OUT)

# turns laser on
def laser_on():
    GPIO.output(26, GPIO.HIGH)
# turns laser off
def laser_off():
    GPIO.output(26, GPIO.LOW)
# laser on and off, on for t seconds
def laser(t):
    GPIO.output(26, GPIO.HIGH)
    time.sleep(t)
    GPIO.output(26, GPIO.LOW)
# strobes laser for t seconds, strobe_freq of 10 or 20 Hz are good values
def strobe_laser(strobe_for, strobe_freq):
    ct = time.time()
    while (time.time() <= (ct+strobe_for)):
        laser((1/strobe_freq)/2)
        time.sleep((1/strobe_freq)/2)




################################################################
# lcd functionality
def write_lcd(text):
    setText_norefresh(text)

# old
# def lcd_colour(rgb):
#     rgb_list = rgb.split(",")
#     setRGB(int(rgb_list[0]), int(rgb_list[1]), int(rgb_list[2]))      

def lcd_colour(r, g, b):
    setRGB(r, g, b)


"""
strobe_laser(5, 10)
"""

"""
pitch_mirror(-512)
turn_mirror(512)
pitch_mirror(512)
turn_mirror(-512)
"""

"""
write_lcd("Procedures end")
lcd_colour(248, 90, 66)
"""