# main.py
try:
    import pms7003
    import sim7000e
    import BME280
    import dht
    from time import sleep
    import machine
    from machine import Pin, I2C, WDT
except ImportError as i_err:
    print(i_err)

#---Debug helper:---
dbg_pin = Pin(23, Pin.IN, Pin.PULL_UP)
DBG = bool(dbg_pin.value() == 0)

#---WDT:---
wdt = WDT(timeout=150000)

#---Fields list:---
thingspeak_fields = [None, None, None, None, None, None, None, None]

#---Error flag and list:---
error_flag = False
error_list = []

#---Mosfet pin:---
mosfet_pin = Pin(19, Pin.OUT)

#---Init SIM7000E module:---
try:
    sim = sim7000e.SIM7000E()  # UART2(rx:16, tx:17)
except Exception:
    error_flag = True
    error_list.append('"SIM7000E": "Init Error"')

#---Init PMS7003 sensor:---
try:
    pms_sensor = pms7003.PMS7003()  # UART1(rx:21, tx:22)
except Exception:
    error_flag = True
    error_list.append('"PMS7003": "Init Error"')

#---Power on mosfet:---
mosfet_pin.value(1)  # Power on mosfet
sleep(0.5)
if DBG:
    print("MOSFET: ON")

#---Init BMP280 sensor:---
try:
    i2c = I2C(sda=Pin(25), scl=Pin(26), freq=10000)  # i2c for bmp280
    bme = BME280.BME280(i2c=i2c) # bmp280 sensor (but using bme library)
except Exception:
    error_flag = True
    error_list.append('"BME280": "Init Error"')

#---Init DHT22 sensor:---
try:
    dht_s = dht.DHT22(Pin(4))
except Exception:
    error_flag = True
    error_list.append('"DHT22": "Init Error"')

#---Start PMS sensor:---
pms_sensor.send_command("wakeup")
pms_sensor.send_command("passive")

#---Wait 10 seconds:---
sleep(10)

#---Read from BMP280:---
try:
    thingspeak_fields[0] = str(bme.temperature)
    thingspeak_fields[1] = str(bme.pressure)
except Exception:
    error_flag = True
    error_list.append('"BME280": "Read Error"')

#---Read from DHT22:---
try:
    dht_s.measure()
    thingspeak_fields[2] = str(dht_s.humidity())
except Exception:
    error_flag = True
    error_list.append('"DHT22": "Read Error"')

#---Wait 30 seconds:---
sleep(30)

#---Read request PMS7003:---
pms_sensor.uart_clear_trash()
pms_sensor.send_command("read")

#---Wait 15 seconds:---
sleep(15)

#---Read response from PMS7003:---
if pms_sensor.read_transmission():
    thingspeak_fields[3] = str(pms_sensor.pm1_0())
    thingspeak_fields[4] = str(pms_sensor.pm2_5())
    thingspeak_fields[5] = str(pms_sensor.pm10())
    thingspeak_fields[6] = str(pms_sensor.num_of_par_0_3um_in_0_1L())
    thingspeak_fields[7] = str(pms_sensor.num_of_par_0_5um_in_0_1L())
else:
    error_flag = True
    error_list.append('"PMS7003": "Transmission Error"')

#---Sleep PMS7003:---
pms_sensor.send_command("sleep")

#---Power on SIM7000E module, connect to ThingSpeak, send data and disconnect:---
sim.power_on(echo=bool(DBG))
sim.connect_to_thingspeak(gsm_apn='internet')
if DBG:
    print(thingspeak_fields)
sim.send_to_thingspeak(api_key='BY3E4OY6MMTCFJLR', fields=thingspeak_fields)
sim.disconnect_from_thingspeak()

#---Send SMS with errors:---
if error_flag:
    txt = '"Errors:"\n' + str(error_list)
    sim.send_sms('+48783846076', txt)

#---Power off SIM7000E module:---
sim.power_off()

#---Power off mosfet:---
mosfet_pin.value(0)

#---ESP32 deepsleep:---
wdt.feed()
x = 3600000
if DBG:
    print("SLEEP for " + str(3) +  "seconds")
    machine.deepsleep(3000)
else:
    machine.deepsleep(x)
