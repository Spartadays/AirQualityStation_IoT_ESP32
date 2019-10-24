# main.py
try:
    import pms7003
    import sim7000e
    import BME280
    import dht
    from time import sleep
    import machine
    from machine import Timer, Pin, I2C, ADC
except ImportError as i_err:
    print(i_err)

#-----OBJECTS:-----
sensor = pms7003.PMS7003()  # UART 1 (rx: 21, tx: 22)
sim = sim7000e.SIM7000E()   # UART 2 (rx: 16, tx: 17)
i2c = I2C(sda=Pin(25), scl=Pin(26), freq=10000)  # i2c for bmp280

# OBJECTS FOR DHT22 AND BME280 ARE DECLARED AFTER POWERING SENSORS IN STARTUP SECTION, DUE TO SPECIFIC INIT METHODS IN THEIR LIBRARIES

timer_0 = Timer(0)
timer_1 = Timer(1)
timer_2 = Timer(2)
timer_3 = Timer(3)

mosfet_pin = Pin(19, Pin.OUT)
# bat = ADC(Pin(34))
#--------------------

#-----GLOBAL:-----
send_flag = False
pms_flag = False
bme_flag = False
dht_flag = False
error_flag = False

thingspeak_fields = [None, None, None, None, None, None, None, None]
error_list = []
#--------------------

#-----TIMERS INTERRUPTS (for PMS7003):-----
def handle_timer_1(timer_1):
    sensor.uart_clear_trash()
    sensor.send_command("read")
    timer_2.init(mode=Timer.ONE_SHOT, period=15000, callback=handle_timer_2)
    #print("PMS: Read\n")

def handle_timer_2(timer_2):
    global thingspeak_fields
    if sensor.read_transmission():
        #sensor.print_all_data()
        thingspeak_fields[3] = str(sensor.pm1_0())
        thingspeak_fields[4] = str(sensor.pm2_5())
        thingspeak_fields[5] = str(sensor.pm10())
        thingspeak_fields[6] = str(sensor.num_of_par_0_3um_in_0_1L())
        thingspeak_fields[7] = str(sensor.num_of_par_0_5um_in_0_1L())
    else:
        #print("PMS: Error\n")
        global error_flag
        error_flag = True
        error_list.append("PMS7003: Transmission Error")
    sensor.send_command("sleep")
    global pms_flag
    pms_flag = True
    print("PMS: Sleep\n")
#--------------------

#-----TIMERS INTERRUPTS (other):-----
def handle_timer_0(timer_0):
    global thingspeak_fields
    try:
        thingspeak_fields[0] = str(bme.temperature)
        thingspeak_fields[1] = str(bme.pressure)
    except Exception:
        global error_flag
        error_flag = True
        error_list.append("BME280: Read Error")
    global bme_flag
    bme_flag = True

def handle_timer_3(timer_3):
    global thingspeak_fields
    try:
        dht_s.measure()
        thingspeak_fields[2] = str(dht_s.humidity())
    except Exception:
        global error_flag
        error_flag = True
        error_list.append("DHT22: Read Error")
    global dht_flag
    dht_flag = True
#--------------------

def mapValueFromTo(value, l_min, l_max, r_min, r_max):
    """Maps value from one range to another"""
    return r_min + (float(value - l_min) / float(l_max - l_min)* r_max - r_min)

# def read_battery():
#     """Return list with battery voltage and battery percentage"""
#     bat.atten(ADC.ATTN_6DB)
#     bat.width(ADC.WIDTH_10BIT)
#     sleep(0.2)
#     bat_adc_val = bat.read()
#     bat_div_val = mapValueFromTo(bat_adc_val, 0, 1023, 0, 2)
#     bat_val = mapValueFromTo(bat_div_val, 0, 2, 0, 4.2)
#     bat_p = mapValueFromTo(bat_val, 2.5, 4.1, 0, 100)
#     return [bat_val, bat_p]

#-----STARTUP CODE:-----
mosfet_pin.value(1)  # power on sensor and sim module
sleep(2) # wait for everything to stabilize

# Read battery state:
# [battery_voltage, battery_percentage] = read_battery()
# print(battery_voltage)
# print(battery_percentage)

try:
    bme = BME280.BME280(i2c=i2c) # bmp280 sensor (but using bme library)
except Exception:
    error_flag = True
    error_list.append("BME280: Connection Error")

try:
    dht_s = dht.DHT22(Pin(4))
except Exception:
    error_flag = True
    error_list.append("DHT22: Connection Error")

sensor.send_command("wakeup")
sensor.send_command("passive")
timer_1.init(mode=Timer.ONE_SHOT, period=60000, callback=handle_timer_1)
print("PMS: Wakeup\n")

timer_0.init(mode=Timer.ONE_SHOT, period=10000, callback=handle_timer_0)
timer_3.init(mode=Timer.ONE_SHOT, period=20000, callback=handle_timer_3)

sim.power_on(echo=True)
sim.connect_to_thingspeak(gsm_apn='internet')
#--------------------

#-----MAIN LOOP:-----
while True:
    sim.print_uart()
    if pms_flag and bme_flag and dht_flag and not send_flag:
        print(thingspeak_fields)
        sim.send_to_thinspeak(api_key='BY3E4OY6MMTCFJLR', fields=thingspeak_fields)
        sim.disconnect_from_thingspeak()
        # --SMS SECTION:--
        if error_flag:
            txt = 'Errors:\n' + str(error_list)
            # txt = 'Battery percentage: ' + str(battery_percentage) + ' [%]\n' + 'Battery voltage: ' + str(battery_voltage) + '[V]\n'
            # if error_flag:
            #     txt = txt + 'Errors:\n' + str(error_list)
            # if battery_voltage <= 3.9:
            #     txt = txt + 'Please, charge your battery.\n'
            sim.send_sms('+48783846076', txt)
        #----------------
        sim.power_off()
        send_flag = True
    if pms_flag and bme_flag and dht_flag and send_flag:
        mosfet_pin.value(0)
        x = 3600000
        print("SLEEP for " + str(x/1000) +  "seconds")
        machine.deepsleep(x)
#--------------------
