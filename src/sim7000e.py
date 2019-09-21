# sim7000e.py
try:
    from machine import UART, Pin
    import time
except ImportError as i_err:
    print(i_err)

class SIM7000E():
    """SIM7000E HAT module class"""
    def __init__(self, number_to_send_sms, gsm_apn, uart_n=2, rx=16, tx=17, pwr_pin=18):
        """Create SIM7000E object on given UART pins.
        Default is UART2, rx: 16, tx: 17, pwr: 18"""
        self.uart_n = uart_n
        self.rx = rx
        self.tx = tx
        self.pwr_pin = pwr_pin

        #PWR off mode works only if you have soldered "PWR resistor" from pads B to A
        self.pwr = Pin(self.pwr_pin, Pin.OUT)
        self.pwr.value(1)
        time.sleep(1)

        self.sim_uart = UART(self.uart_n, 115200)
        self.sim_uart.init(baudrate=115200, parity=None, stop=1, rx=self.rx, tx=self.tx)
        
        self.number_to_send_sms = number_to_send_sms
        self.gsm_apn = gsm_apn
        print("SIM: Init\n")

    def send_sms(self, number, text):
        pass

    def power_off(self):
        self.send_uart('AT+POWD=1/r')
        time.sleep(2)
        self.pwr.value(0)
        print("SIM: Power off\n")

    def power_on(self, echo=False):
        self.pwr.value(1)
        time.sleep(2)
        if echo:
            self.send_uart('ATE1\r')
        else:
            self.send_uart('ATE0\r')
        print("SIM: Power on\n")

    def send_uart(self, w):
        self.sim_uart.write(w)

    def print_uart(self):
        if self.sim_uart.any() >= 1:
            data = self.sim_uart.read()
            print(data)
