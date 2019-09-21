# pms7003.py
try:
    from machine import UART
except ImportError as i_err:
    print(i_err)

# COMMANDS:
active = "active"
passive = "passive"
sleep = "sleep"
wakeup = "wakeup"
read = "read"

# Data index in measures list:
DATA_1 = PM1_0CF1 = 0  # PM1.0 concentration unit ug/m3 (CF = 1, standard particle)
DATA_2 = PM2_5CF1 = 1  # PM2.5 concentration unit ug/m3 (CF = 1, standard particle)
DATA_3 = PM10CF1 = 2  # PM10 concentration unit ug/m3 (CF = 1, standard particle)
DATA_4 = PM1_0 = 3  # PM1.0 concentration unit ug/m3 (under atmospheric environment)
DATA_5 = PM2_5 = 4  # PM2.5 concentration unit ug/m3 (under atmospheric environment)
DATA_6 = PM10 = 5  # PM10 concentration unit ug/m3 (under atmospheric environment)
DATA_7 = NUM_OF_PAR_0_3_UM_IN_0_1_L_OF_AIR = 6  # Number of particles with diameter beyond 0.3 um in 0.1 L of air
DATA_8 = NUM_OF_PAR_0_5_UM_IN_0_1_L_OF_AIR = 7  # Number of particles with diameter beyond 0.5 um in 0.1 L of air
DATA_9 = NUM_OF_PAR_1_UM_IN_0_1_L_OF_AIR = 8  # Number of particles with diameter beyond 1.0 um in 0.1 L of air
DATA_10 = NUM_OF_PAR_2_5_UM_IN_0_1_L_OF_AIR = 9  # Number of particles with diameter beyond 2.5 um in 0.1 L of air
DATA_11 = NUM_OF_PAR_5_0_UM_IN_0_1_L_OF_AIR = 10  # Number of particles with diameter beyond 5.0 um in 0.1 L of air
DATA_12 = NUM_OF_PAR_10_UM_IN_0_1_L_OF_AIR = 11  # Number of particles with diameter beyond 10 um in 0.1 L of air
# Call Factor: CF=1 should be used in the factory environment

class PMS7003():
    """PMS7003 air quality sensor class"""
    def __init__(self, uart_num=1, rx=21, tx=22, reset_pin=None, set_pin=None):
        """Create PMS7003 sensor object on given UART pins.
        Default is UART1, rx: 21, tx: 22"""
        self.uart_num = uart_num
        self.rx = rx
        self.tx = tx
        self.pms_uart = UART(self.uart_num, 9600)
        self.pms_uart.init(baudrate=9600, parity=None, stop=1, rx=self.rx, tx=self.tx)
        self.uart_flag = True
        self.read_flag = False
        self.measures = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ##COMMENT CODE BELOW IF YOU DO IT IN YOUR SCRIPT AFTER INITIALIZATION:##
        #self.send_command(passive)
        #utime.sleep(2)
        #self.pms_uart.read()  # Clear all trash from uart buffer
        ##END##
        print("PMS: Init\n")

    def uart_deinit(self):
        self.pms_uart.deinit()
        self.uart_flag = False

    def uart_reinit(self):
        self.pms_uart = UART(self.uart_num, 9600)
        self.pms_uart.init(baudrate=9600, parity=None, stop=1, rx=self.rx, tx=self.tx)
        self.uart_flag = True

    def uart_clear_trash(self):
        self.pms_uart.read()

    def read_transmission(self):
        """Read serial data, process them and update class variables"""
        if self.pms_uart.any() >= 1:
            data = self.pms_uart.read(32)
        else:
            print("Empty uart")
            self.read_flag = False
            return False

        if data[0] == 0x42 and data[1] == 0x4d:
            start_bits_flag = True
        else:
            start_bits_flag = False
            print('Start Bits ERROR')

        if int.from_bytes(data[2:4], "big") == 28:
            data_length_flag = True
        else:
            data_length_flag = False
            print("Transmission Length ERROR")

        check_code = int.from_bytes(data[30:32], "big")
        my_sum = sum(data[:30])

        if my_sum == check_code:
            check_code_flag = True
        else:
            check_code_flag = False
            print("Check Sum ERROR")

        if start_bits_flag is True and data_length_flag is True and check_code_flag is True:
            for c in range(len(self.measures)):
                self.measures[c] = int.from_bytes(data[c*2+4 : c*2+6], "big")
            self.read_flag = True
            return True
        else:
            self.read_flag = False
            return False

    def print_all_data(self):
        """Prints list of measures in console"""
        print('PM1.0 = ' + str(self.measures[DATA_1]) + ' ug/m3, factory environment')
        print('PM2.5 = ' + str(self.measures[DATA_2]) + ' ug/m3, factory environment')
        print('PM10 = ' + str(self.measures[DATA_3]) + ' ug/m3, factory environment')
        print('PM1.0 = ' + str(self.measures[DATA_4]) + ' ug/m3, atmospheric environment')
        print('PM2.5 = ' + str(self.measures[DATA_5]) + ' ug/m3, atmospheric environment')
        print('PM10 = ' + str(self.measures[DATA_6]) + ' ug/m3, atmospheric environment')
        print('Number of particles with diameter beyond 0.3 um in 0.1L of air = ' + str(self.measures[DATA_7]))
        print('Number of particles with diameter beyond 0.5 um in 0.1L of air = ' + str(self.measures[DATA_8]))
        print('Number of particles with diameter beyond 1.0 um in 0.1L of air = ' + str(self.measures[DATA_9]))
        print('Number of particles with diameter beyond 2.5 um in 0.1L of air = ' + str(self.measures[DATA_10]))
        print('Number of particles with diameter beyond 5.0 um in 0.1L of air = ' + str(self.measures[DATA_11]))
        print('Number of particles with diameter beyond 10 um in 0.1L of air = ' + str(self.measures[DATA_12]))

    def pm1_0(self, cf=0):
        if cf == 0:
            return self.measures[DATA_4]
        else:
            return self.measures[DATA_1]

    def pm2_5(self, cf=0):
        if cf == 0:
            return self.measures[DATA_5]
        else:
            return self.measures[DATA_2]

    def pm10(self, cf=0):
        if cf == 0:
            return self.measures[DATA_6]
        else:
            return self.measures[DATA_3]

    def num_of_par_0_3um_in_0_1L(self):
        return self.measures[DATA_7]

    def num_of_par_0_5um_in_0_1L(self):
        return self.measures[DATA_8]

    def send_command(self, command):
        """Send command to sensor. Modes: active(default) or passive. States: sleep or wakeup(default)"""
        start_b1 = 0x42
        start_b2 = 0x4d
        if command == active:
            cmd = 0xe1
            data_h = 0x00
            data_l = 0x01
            lrc_h = 0x01
            lrc_l = 0x71
        elif command == sleep:
            cmd = 0xe4
            data_h = 0x00
            data_l = 0x00
            lrc_h = 0x01
            lrc_l = 0x73
        elif command == wakeup:
            cmd = 0xe4
            data_h = 0x00
            data_l = 0x01
            lrc_h = 0x01
            lrc_l = 0x74
        elif command == read:
            cmd = 0xe2
            data_h = 0x00
            data_l = 0x00
            lrc_h = 0x01
            lrc_l = 0x71
        elif command == passive:
            cmd = 0xe1
            data_h = 0x00
            data_l = 0x00
            lrc_h = 0x01
            lrc_l = 0x70
        else:
            return
        protocol = bytearray([start_b1, start_b2, cmd, data_h, data_l, lrc_h, lrc_l])
        self.pms_uart.write(protocol)

    def sleep(self, transistor_pin=None):
        self.send_command(sleep)
        pass
