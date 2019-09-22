# sim7000e.py
try:
    from machine import UART, Pin
    from time import sleep
except ImportError as i_err:
    print(i_err)

class SIM7000E():
    """SIM7000E HAT module class"""
    def __init__(self, uart_n=2, rx=16, tx=17, pwr_pin=18):
        """Create SIM7000E object on given UART pins.
        Default is UART2, rx: 16, tx: 17, pwr: 18"""
        self.uart_n = uart_n
        self.rx = rx
        self.tx = tx
        self.pwr_pin = pwr_pin

        #PWR off mode works only if you have soldered "PWR resistor" from pads B to A
        self.pwr = Pin(self.pwr_pin, Pin.OUT)
        self.pwr.value(1)
        sleep(1)

        self.sim_uart = UART(self.uart_n, 115200)
        self.sim_uart.init(baudrate=115200, parity=None, stop=1, rx=self.rx, tx=self.tx)
        print("SIM: Init\n")

    def send_uart(self, w):
        self.sim_uart.write(w)
        sleep(1)
        self.print_uart()

    def print_uart(self):
        if self.sim_uart.any() >= 1:
            data = self.sim_uart.read()
            print(data)

    def send_sms(self, number, text):
        pass #TODO

    def power_off(self):
        self.send_uart('AT+POWD=0/r')
        sleep(2)
        self.pwr.value(0)
        print("SIM: Power off\n")

    def power_on(self, echo=False):
        self.pwr.value(1)
        sleep(20)
        self.send_uart('AT\r')
        self.send_uart('AT\r')
        self.send_uart('AT\r')

        if echo:
            self.send_uart('ATE1\r')
        else:
            self.send_uart('ATE0\r')

        self.send_uart('AT\r')
        print("SIM: Power on\n")

    def send_to_thinspeak(self, gsm_apn, api_key, fields):
        self.send_uart('AT+CNMP=13\r') # GPRS/GSM mode
        self.send_uart('AT+NBSC=1\r') # Scrambling
        self.send_uart('AT+COPS?\r') # Signal quality
        sleep(4)
        self.send_uart('AT+CGATT?\r') # Attach check
        sleep(2)
        self.send_uart('AT+CSTT?\r') # Query available APN
        self.send_uart('AT+CSTT="' + gsm_apn + '"\r') # Set APN
        self.send_uart('AT+CIICR\r') # Bring up connection
        sleep(6)
        self.send_uart('AT+CIFSR\r') # Get local address
        self.send_uart('AT+CIPSTART="TCP","api.thingspeak.com",80\r') # Start up connection
        sleep(4)
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
        self.send_uart('\x1A\r\n')
        sleep(3)
        self.print_uart()
        self.send_uart('AT+CIPCLOSE=0\r') # Close connection
        self.send_uart('AT+CIPSHUT\r') # Deactivate context
        #TODO: Podzielic na connect, send i disconnect potem uzywac ich odpowiednio na starcie, w petli po ustawieniu flagi odczytu z pms i po wyslaniu
