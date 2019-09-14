# main.py
import pms7003
from time import sleep
import machine
from machine import UART, Timer, Pin

sensor = pms7003.PMS7003()  # UART 1 (rx: 21, tx: 22)

timer_0 = Timer(0)
timer_1 = Timer(1)
timer_2 = Timer(2)

uart2 = UART(2, 115200)
uart2.init(115200)

led = Pin(18, Pin.OUT)

flag = False

#--Timers loop (for PMS7003):--
def handle_timer_0(timer_0):
    sensor.send_command("wakeup")
    sensor.send_command("passive")
    timer_1.init(mode=Timer.ONE_SHOT, period=30000, callback=handle_timer_1)

def handle_timer_1(timer_1):
    sensor.uart_clear_trash()
    sensor.send_command("read")
    timer_2.init(mode=Timer.ONE_SHOT, period=15000, callback=handle_timer_2)
    
def handle_timer_2(timer_2):
    if sensor.read_transmission():
        sensor.print_all_data()
    else:
        print("Error")
        sensor.uart_reinit()
    sensor.send_command("sleep")
    print("SLEEP")
    global flag
    flag = True
    machine.deepsleep(60000)
    #timer_0.init(mode=Timer.ONE_SHOT, period=60000, callback=handle_timer_0)
#----------------

#STARTUP CODE:
timer_0.init(mode=Timer.ONE_SHOT, period=2000, callback=handle_timer_0)  # wait for uarts to initialize

print("STARTED")
while True:
    led.value(1)
    sleep(0.1)
    led.value(0)
    sleep(0.1)