import machine
from machine import I2C
from machine import Pin as pin
from I2C_LCD import I2cLcd
import time
import random

running = True
i2c = I2C(0, scl=pin(22), sda=pin(21), freq=400000)

devices = i2c.scan()
lcd = I2cLcd(i2c, devices[0], 2, 16)

min_button = pin(4,pin.IN,pin.PULL_UP)
sec_button = pin(17,pin.IN,pin.PULL_UP)
start_button = pin(13,pin.IN,pin.PULL_UP)

all_random_pin = [5, 25, 27, 33, 23, 19, 16, 2]

def shuffle_list(lst):
    lst_copy = lst[:]
    n = len(lst_copy)
    for i in range(n - 1, 0, -1):
        j = random.getrandbits(16) % (i + 1)
        lst_copy[i], lst_copy[j] = lst_copy[j], lst_copy[i]
    return lst_copy

shuffled = shuffle_list(all_random_pin)
selected_pin = shuffled[:8]

print("working pin = ",selected_pin)
print("win_button =",selected_pin[1])
print("game_over_button_1 = ",selected_pin[3])
print("game_over_button_2 = ",selected_pin[0])
print("game_over_button_2 = ",selected_pin[6])
print("do_nothing_1 = ",selected_pin[4])
print("do_nothing_1 = ",selected_pin[5])
print("do_nothing_1 = ",selected_pin[2])
print("do_nothing_1 = ",selected_pin[7])

win_button = pin(selected_pin[1],pin.IN,pin.PULL_UP)
game_over_button_1 = pin(selected_pin[3],pin.IN,pin.PULL_UP)
game_over_button_2 = pin(selected_pin[0],pin.IN,pin.PULL_UP)
game_over_button_3 = pin(selected_pin[6],pin.IN,pin.PULL_UP)
do_nothing_1 = pin(selected_pin[4],pin.IN,pin.PULL_UP)
do_nothing_2 = pin(selected_pin[5],pin.IN,pin.PULL_UP)
do_nothing_3 = pin(selected_pin[2],pin.IN,pin.PULL_UP)
do_nothing_4 = pin(selected_pin[7],pin.IN,pin.PULL_UP)

led = pin(14,pin.OUT)
led.value(0)
buzzer = machine.PWM(pin(32))
buzzer.duty(0)
# not use yet 5 25 27 26 33 23 1s9 18 16 2 15 

minute = int(0)
sec = int(0)
senst = 0.2

lcd.clear()
time.sleep(0.2)

lcd.putstr("Boom solve V.1 ")
lcd.move_to(0, 1)
lcd.putstr("By papon k.")
time.sleep(3)
lcd.clear()

lcd.putstr("In put time ")
time.sleep(0.8)
lcd.clear()

lcd.putstr("min:sec :")
def beep(freq=0 , duration=0 , loudness = 0):
    buzzer.freq(freq)       
    buzzer.duty(loudness) #512 is how loud of speaker 0-1023         
    time.sleep(duration)     
    buzzer.duty(0)
    
def congrat_sound() :
    beep(1047, 0.15,150)
    beep(1319, 0.15,200)
    beep(1568, 0.15,250)
    beep(2093, 0.3,300)
    beep(1568, 0.15,220)
    beep(2093, 0.4,320)

def play_again() :
    led.value(0)
    buzzer.duty(0)
    lcd.clear()
    lcd.putstr("Press start btn")
    lcd.move_to(0, 1)
    lcd.putstr("to try again")
    while start_button.value() == 1 :
        time.sleep(0.2)
    machine.reset()
    
def boom_solve_V1() :
    led.value(0)
    buzzer.duty(0)
    global minute, sec
    while running :
        if min_button.value() == 0 : #when sw pressdown value == 0
            minute = minute+1
            if minute >= 60 :
                minute = 0
            time.sleep(senst)
            print("minute",minute)
            
        if sec_button.value() == 0 :
            sec = sec+1
            if sec >= 60 :
                sec = 0
                lcd.clear()
                lcd.putstr("min:sec :")
                
            time.sleep(senst)
            print("sec",sec)        
        lcd.move_to(5, 1)        
        lcd.putstr(f"{minute:02d}:{sec:02d}")    

        if start_button.value() == 0 :
            while True :
                lcd.clear()
                lcd.putstr("Time remaining :")
                lcd.move_to(5, 1)        
                lcd.putstr(f"{minute:02d}:{sec:02d}")
                
                led.value(0)
                time.sleep(1)
                led.value(1)
                sec = sec-1
                beep(1000,0.2,200)
                buzzer.duty(0)
                
                if win_button.value() == 1 : #0 is when connect 1 is disconnect
                    lcd.clear()
                    lcd.move_to(1, 0)
                    lcd.putstr("Congratuations")
                    lcd.move_to(2, 1)
                    lcd.putstr("BOMB DEFUSED")
                    congrat_sound()
                    time.sleep(1)               
                    play_again()
                    
                if game_over_button_1.value() or game_over_button_2.value() or game_over_button_3.value() == 1 : #0 is when connect 1 is disconnect
                    lcd.clear()
                    lcd.move_to(2, 0)
                    lcd.putstr("!!YOU LOSE!!")
                    lcd.move_to(2, 1)
                    lcd.putstr("BOMB ACTIVE")
                    beep(1500,2,200)                    
                    play_again()
                    
                if sec <= -1 :
                    if minute != 0:
                        minute = minute-1
                        sec = 59
                            
                    else:
                        lcd.clear()
                        lcd.move_to(1, 0)
                        lcd.putstr("!! Time OUT !!")
                        lcd.move_to(5, 1)
                        lcd.putstr(f"{minute:02d}:{sec:02d}")
                        led.value(1)
                        beep(1500,2,200) #we will config when we give this to teacher bc it too fast it make for coding
                        buzzer.duty(0)
                        led.value(0)                     
                        play_again()                       
                    print("minute",minute)
                    
while running :
    while start_button.value() == 0 :
        pass
    boom_solve_V1()
    