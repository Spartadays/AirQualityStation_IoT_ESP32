# main.py
try:
    import pms7003
    import sim7000e
    from time import sleep
    import machine
    from machine import Timer, Pin

except ImportError as i_err:
    print(i_err)

sensor = pms7003.PMS7003()  # UART 1 (rx: 21, tx: 22)
sim = sim7000e.SIM7000E()   # UART 2 (rx: 16, tx: 17)

timer_0 = Timer(0)
timer_1 = Timer(1)
timer_2 = Timer(2)
timer_3 = Timer(3)

led = Pin(19, Pin.OUT)

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
    machine.deepsleep(60000)
    #timer_0.init(mode=Timer.ONE_SHOT, period=60000, callback=handle_timer_0)
#----------------

def handle_timer_3(timer_3):
    sim.send_uart('AT+CCLK?\r')
    sim.print_uart()

#STARTUP CODE:
timer_0.init(mode=Timer.ONE_SHOT, period=2000, callback=handle_timer_0)  # wait for uarts to initialize
timer_3.init(mode=Timer.PERIODIC, period=1000, callback=handle_timer_3)

print("STARTED")
while True:
    led.value(1)
    sleep(0.03)
    led.value(0)
    sleep(0.03)

