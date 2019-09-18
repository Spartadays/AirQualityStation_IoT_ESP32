# sim7000e.py
try:
    from machine import UART, Pin
except ImportError as i_err:
    print(i_err)

class SIM7000E():
    """SIM7000E HAT module class"""
    def __init__(self, uart_n=None, rx=None, tx=None, pwr_pin=None):
        """Create SIM7000E object on given UART pins.
        Default is UART2, rx: 16, tx: 17, pwr: 18"""
        if uart_n is None or not isinstance(uart_n, int):
            self.uart_n = 2
        else:
            self.uart_n = uart_n
        if rx is None or not isinstance(rx, int):
            self.rx = 16
        else:
            self.rx = rx
        if tx is None or not isinstance(tx, int):
            self.tx = 17
        else:
            self.tx = tx
        if pwr_pin is None or not isinstance(pwr_pin, int):
            self.pwr_pin = 18
        else:
            self.pwr_pin = pwr_pin

        #PWR off mode works only if you have soldered "PWR resistor" from pads B to A
        self.pwr = Pin(self.pwr_pin, Pin.OUT)
        self.pwr.value(1)

        self.sim_uart = UART(self.uart_n, 115200)
        self.sim_uart.init(baudrate=115200, parity=None, stop=1, rx=self.rx, tx=self.tx)
        
        self.number_to_send_sms = None
        self.gsm_apn = None

    def send_sms(self, number, text):
        pass

    def power_off(self):
        pass

    def power_on(self):
        pass

    def send_uart(self, w):
        self.sim_uart.write(w)
    
    def print_uart(self):
        if self.sim_uart.any() >= 1:
            data = self.sim_uart.read()
            print(data)
    
