#-*- coding: latin-1 -*-#
import RPi.GPIO as GPIO
import spidev, time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

GPIO.setmode(GPIO.BOARD) #GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
print("balance.py")

# SH1106 connections and settings
A0 = 22 #GPIO pin for A0 pin : 0 -> command; 1 -> display data RAM
RESN = 18 #GPIO pin for display reset (active low)
spi = spidev.SpiDev()
spi.open(0, 0) #bus = 0 , device = 0
spi.max_speed_hz = 1000000
spi.mode = 0b00
spi.bits_per_word = 8
spi.threewire
SETCOLADDRHIGH   = "00" #1. Set Column Address 4 lower bits  0x00->0x0F
SETCOLADDRLOW    = "10" #2. Set Column Address 4 higher bits 0x10->0x1F
SETDISPON        = "AF" #7. Set Entire Display OFF/ON    0xA4 / 0xA5
SETPAGEADDR      = "B0" #12. Set Page Add 0xB0->0xB7 page @ to load RAM
fontpath = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
fontsize = 25
font = ImageFont.truetype(fontpath, fontsize)

# HX711 connections and settings
CtrlPin = 13
DTPin = 15
SCKPin = 16
cal_zero =  73100 #this value is to be adjusted first with no load on scale so it displays 0.000 kg
cal_1kg  = -280000 #this value is to be adjusted after zero calibration with a reference 1kg load so it displays 1.000 kg
avgnr = 4 #nr of reading averaged to display the measured weight
maxtimeread = 0.001560 #empiric filtering to remove measures that took too long
GPIO.setup(CtrlPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) #PUD_UP PUD_DOWN
GPIO.setup(DTPin,   GPIO.IN, pull_up_down=GPIO.PUD_UP) #PUD_UP PUD_DOWN
GPIO.setup(SCKPin,  GPIO.IN, pull_up_down=GPIO.PUD_UP) #PUD_UP PUD_DOWN
SCK_count = 25 #(25 -> ch.A,gain 128 / 26 -> cha.B, gain 32 / 27 -> cha.A, gain 64)
cntr = 0
intgpoids = 0.0
startt = time.time()
stopt= time.time()

# init HX711 clock to 'Low'
GPIO.setup(SCKPin, GPIO.OUT, initial=GPIO.LOW) #setup HX711 clock to 'Low'
# init SH1106 reset
GPIO.setup(A0, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(RESN, GPIO.OUT, initial=GPIO.HIGH)
time.sleep(0.1)
GPIO.output(RESN, 0)
time.sleep(0.1)
GPIO.output(RESN, 1)
time.sleep(0.1)

def write_command(data): #write command register to SH1106 display circuit
    GPIO.output(A0, 0)
    for a in range (len(data)): spi.xfer([int(data[a],16)])

def write_display_ram(data): #write display ram to SH1106 display circuit
    GPIO.output(A0, 1)
    for a in range (len(data)): spi.xfer([int(data[a],16)])

def display_img(image): #write an image to display ram
    write_command([SETDISPON])
    data_set=[]
    data_slice=[[],[],[],[],[],[],[],[]]
    for p in range (0,8):
        data_set = ['0', '0']
        for c in range (0,128):
            by = 0x00
            for b in range (0,8):
                by = by>>1 | (image.getpixel((c, p*8+b))& 0x80)
            data_set.append("{0:02x}".format(by))
        data_slice[p]=data_set
    for p in range (0,8):
        data_set = ["{:02x}".format(int(SETPAGEADDR, 16)+p)]
        data_set.append(SETCOLADDRHIGH)
        data_set.append(SETCOLADDRLOW)
        write_command(data_set)
        write_display_ram(data_slice[p])

def display_text(texte):
    img = Image.new('1', (128, 64), color = 'black')
    ImageDraw.Draw(img).text((1,16), texte, font=font, fill=255)
    display_img(img)

########################################################################
img = Image.open("8TN.png").convert('1')
display_img(img)
time.sleep(1)

while GPIO.input(CtrlPin)==1:
    time.sleep(0.01)
    val = 0x0

    while GPIO.input(DTPin)==1: #wait data ready to be read from HX711
        time.sleep(0.01)

    startt = time.time()

    for a in range (0, 24): #read 24 bits
        GPIO.output(SCKPin, 1)
        val = val*2 + GPIO.input(DTPin)
        GPIO.output(SCKPin, 0)

    for a in range (0, SCK_count - 24): #additonal clk pulse
        GPIO.output(SCKPin, 1)
        GPIO.output(SCKPin, 0)

    stopt = time.time()

    if val == 16777215 or val==16449535 or val==16433151 or val==16515071 or val==16424959 or val==16420863: #empiric values firltering
        if val >= 8388608: val -= 16777216
        poids = (val - cal_zero)/cal_1kg
    elif stopt-startt >= maxtimeread:
        if val >= 8388608: val -= 16777216
        poids = (val - cal_zero)/cal_1kg
    else:
        if val >= 8388608: val -= 16777216
        poids = (val - cal_zero)/cal_1kg
        if 0==1:
            pass
        else:
            cntr += 1
            intgpoids += poids
            if cntr == avgnr:
                print("  {0:8.3f}".format(intgpoids/avgnr), " kg  ", end='')
                display_text("  {0:2.3f}".format(intgpoids/avgnr)+ "kg")
                cntr = 0
                intgpoids = 0.0
    print(end='\r')

GPIO.cleanup()
print("---end---")
