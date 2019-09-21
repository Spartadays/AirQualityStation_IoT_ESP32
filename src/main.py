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
sim = sim7000e.SIM7000E('783846076', 'internet')   # UART 2 (rx: 16, tx: 17)

sim.power_on(echo=True)

timer_0 = Timer(0)
timer_1 = Timer(1)
timer_2 = Timer(2)
timer_3 = Timer(3)

led = Pin(19, Pin.OUT)

send_flag = False
pms_flag = False

thingspeak_fields = [None, None, None, None, None, None, None, None]

#--Timers for PMS7003:--
def handle_timer_0(timer_0):
    sensor.send_command("wakeup")
    sensor.send_command("passive")
    timer_1.init(mode=Timer.ONE_SHOT, period=30000, callback=handle_timer_1)
    print("PMS: Wakeup\n")

def handle_timer_1(timer_1):
    sensor.uart_clear_trash()
    sensor.send_command("read")
    timer_2.init(mode=Timer.ONE_SHOT, period=15000, callback=handle_timer_2)
    print("PMS: Read\n")

def handle_timer_2(timer_2):
    global thingspeak_fields
    if sensor.read_transmission():
        #sensor.print_all_data()
        thingspeak_fields[4-1] = str(sensor.pm1_0())
        thingspeak_fields[5-1] = str(sensor.pm2_5())
        thingspeak_fields[6-1] = str(sensor.pm10())
        thingspeak_fields[7-1] = str(sensor.num_of_par_0_3um_in_0_1L())
        thingspeak_fields[8-1] = str(sensor.num_of_par_0_5um_in_0_1L())
    else:
        print("PMS: Error\n")
        sensor.uart_reinit()
    sensor.send_command("sleep")
    global pms_flag
    pms_flag = True
    print("PMS: Sleep\n")
#----------------

def handle_timer_3(timer_3):
    sim.send_uart('AT+CCLK?\r')
    sim.print_uart()
    global send_flag
    send_flag = True

#STARTUP CODE:
timer_0.init(mode=Timer.ONE_SHOT, period=2000, callback=handle_timer_0)  # wait for uarts to initialize
timer_3.init(mode=Timer.PERIODIC, period=3000, callback=handle_timer_3)

while True:
    led.value(1)
    sleep(0.05)
    led.value(0)
    sleep(0.05)
    if send_flag and pms_flag:
        print(thingspeak_fields)
        sim.power_off()
        print("SLEEP for 60 seconds")
        machine.deepsleep(60000)

