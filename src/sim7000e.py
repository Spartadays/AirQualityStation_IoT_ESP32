# sim7000e.py
try:
    from machine import UART, Pin
    from time import sleep
except ImportError as i_err:
    print(i_err)

# Debug:
dbg_pin = Pin(23, Pin.IN, Pin.PULL_UP)
DBG = bool(dbg_pin.value() == 0)

class SIM7000E():
    """SIM7000E HAT module class"""
    def __init__(self, uart_n=2, rx=16, tx=17, pwr_pin=18):
        """Create SIM7000E object on given UART pins.
        Default is UART2, rx: 16, tx: 17, pwr: 18"""
        self.uart_n = uart_n
        self.rx = rx
        self.tx = tx

        #PWR off mode works only if you have soldered "PWR resistor" from pads B to A
        self.pwr_pin = Pin(pwr_pin, Pin.OUT)
        self.pwr_pin.value(0)

        self.sim_uart = UART(self.uart_n, 115200)
        self.sim_uart.init(baudrate=115200, parity=None, stop=1, rx=self.rx, tx=self.tx)
        if DBG:
            print("SIM: Init")

    def send_uart(self, w):
        """Send AT command to SIM module (includes 1 sec delay and prints response to serial)"""
        self.sim_uart.write(w)
        sleep(1)
        if DBG:
            self.print_uart()

    def print_uart(self):
        """Print response from SIM module over serial"""
        if self.sim_uart.any() >= 1:
            data = self.sim_uart.read()
            print(data)

    def return_uart(self):
        """Return response from SIM module"""
        if self.sim_uart.any() >= 1:
            data = self.sim_uart.read()
            return data
        return None

    def send_sms(self, number, text):
        """Send text in SMS to given number"""
        self.send_uart('AT+CMGF=1\r')
        self.send_uart('AT+CMGS="'+str(number)+'"\r')
        self.send_uart(str(text))
        self.send_uart('\x1A\r\n') # 0x1A ends data entering mode

    def power_off(self, send=True):
        """Power dowm SIM module with sending POWD command (default) or without it"""
        if send:
            self.send_uart('AT+CPOWD=1\r')
            sleep(2)
        self.pwr_pin.value(0)
        if DBG:
            print("SIM: Power off")

    def power_on(self, echo=False):
        """Power on module"""
        if DBG:
            print("SIM: Power on")
        self.pwr_pin.value(1)
        sleep(20)
        self.send_uart('AT\r')
        self.send_uart('AT\r')
        self.send_uart('AT\r')

        if echo:
            self.send_uart('ATE1\r')
        else:
            self.send_uart('ATE0\r')

        self.send_uart('AT\r')
        self.send_uart('AT+CNMI=0,0,0,0\r') # Disable all SMS notifications

    def connect_to_thingspeak(self, gsm_apn):
        """Connect to ThingSpeak server using your APN"""
        self.send_uart('AT+CNMP=13\r') # GPRS/GSM mode
        self.send_uart('AT+NBSC=1\r') # Scrambling
        self.send_uart('AT+CSTT="' + gsm_apn + '"\r') # Set APN
        self.send_uart('AT+CIICR\r') # Bring up connection
        sleep(6)
        self.send_uart('AT+CIFSR\r') # Get local address
        self.send_uart('AT+CIPSTART="TCP","api.thingspeak.com",80\r') # Start up connection
        sleep(4)

    def connect_to(self, gsm_apn, protocol, address, port):
        """Connect to some server using your APN, protocol type, address and port"""
        self.send_uart('AT+CNMP=13\r') # GPRS/GSM mode
        self.send_uart('AT+NBSC=1\r') # Scrambling
        self.send_uart('AT+CSTT="' + gsm_apn + '"\r') # Set APN
        self.send_uart('AT+CIICR\r') # Bring up connection
        sleep(6)
        self.send_uart('AT+CIFSR\r') # Get local address
        self.send_uart('AT+CIPSTART="'+protocol+'","'+address+'",'+port+'\r') # Start up connection
        sleep(4)

    def send_to_thingspeak(self, api_key, fields):
        """Send data array[8] to ThingSpeak (require your API)"""
        self.send_uart('AT+CIPSEND\r') # Send data
        self.send_uart('GET /update?api_key='+api_key+
                       '&field1='+str(fields[0])+
                       '&field2='+str(fields[1])+
                       '&field3='+str(fields[2])+
                       '&field4='+str(fields[3])+
                       '&field5='+str(fields[4])+
                       '&field6='+str(fields[5])+
                       '&field7='+str(fields[6])+
                       '&field8='+str(fields[7])+
                       '\r\n'
                       ) # Data
        self.send_uart('\x1A\r\n') # 0x1A ends data entering mode
        sleep(3)
        if DBG:
            self.print_uart()

    def disconnect_from_thingspeak(self, fast=True):
        """Disconnect"""
        if fast:
            self.send_uart('AT+CIPCLOSE=1\r')
        else:
            self.send_uart('AT+CIPCLOSE=0\r')
        # Close connection
        self.send_uart('AT+CIPSHUT\r') # Deactivate context
