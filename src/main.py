# main.py
try:
    import pms7003
    import sim7000e
    from time import sleep
    import machine
    from machine import Timer, Pin
except ImportError as i_err:
    print(i_err)

#-----OBJECTS:-----
sensor = pms7003.PMS7003()  # UART 1 (rx: 21, tx: 22)
sim = sim7000e.SIM7000E()   # UART 2 (rx: 16, tx: 17)

timer_0 = Timer(0)
timer_1 = Timer(1)
timer_2 = Timer(2)
timer_3 = Timer(3)

led = Pin(19, Pin.OUT)
#--------------------

#-----GLOBAL:-----
send_flag = False
pms_flag = False

thingspeak_fields = [-999, -999, -999, None, None, None, None, None]
#--------------------

#-----TIMERS INTERRUPTS (for PMS7003):-----
def handle_timer_1(timer_1):
    sensor.uart_clear_trash()
    sensor.send_command("read")
    timer_2.init(mode=Timer.ONE_SHOT, period=15000, callback=handle_timer_2)
    print("PMS: Read\n")

def handle_timer_2(timer_2):
    global thingspeak_fields
    if sensor.read_transmission():
        #sensor.print_all_data()
        #TODO: Dorobic mediane z 5 nastepujacych po sobie odczytach
        thingspeak_fields[3] = str(sensor.pm1_0())
        thingspeak_fields[4] = str(sensor.pm2_5())
        thingspeak_fields[5] = str(sensor.pm10())
        thingspeak_fields[6] = str(sensor.num_of_par_0_3um_in_0_1L())
        thingspeak_fields[7] = str(sensor.num_of_par_0_5um_in_0_1L())
    else:
        print("PMS: Error\n")
        sensor.uart_reinit()
    sensor.send_command("sleep")
    global pms_flag
    pms_flag = True
    print("PMS: Sleep\n")
#--------------------

#-----STARTUP CODE:-----
sleep(2) # wait for everything to stabilize
sensor.send_command("wakeup")
sensor.send_command("passive")
timer_1.init(mode=Timer.ONE_SHOT, period=30000, callback=handle_timer_1)
print("PMS: Wakeup\n")

sim.power_on(echo=True)
sim.connect_to_thingspeak(gsm_apn='internet')
#--------------------

#-----MAIN LOOP:-----
while True:
    led.value(1)
    sleep(0.05)
    led.value(0)
    sleep(0.05)
    sim.print_uart()
    if pms_flag and not send_flag:
        print(thingspeak_fields)
        sim.send_to_thinspeak(api_key='BY3E4OY6MMTCFJLR', fields=thingspeak_fields)
        sim.disconnect_from_thingspeak()
        sim.power_off()
        global send_flag
        send_flag = True
    if pms_flag and send_flag:
        x = 3600000
        print("SLEEP for" + x/1000 +  "seconds")
        machine.deepsleep(x)
#--------------------
