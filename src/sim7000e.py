# sim7000e.py
try:
    from machine import UART
except ImportError as i_err:
    print(i_err)

class SIM7000E():
    """SIM7000E HAT module class"""
    def __init__(self, uart_n=None, rx=None, tx=None):
        """Create SIM7000E object on given UART pins.
        Default is UART2, rx: 16, tx: 17"""
        if uart_n is None or not isinstance(uart_n, int):
            self.uart_n = 2;
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

        self.sim_uart = UART(self.uart_n, 115200)
        self.sim_uart.init(baudrate=115200, parity=None, stop=1, rx=self.rx, tx=self.tx)
        
        self.number_to_send_sms = None
        self.gsm_apn = None

    def send_uart(self, w):
        self.sim_uart.write(w)
    
    def print_uart(self):
        if self.sim_uart.any() >= 1:
            data = self.sim_uart.read()
            print(data)
    
