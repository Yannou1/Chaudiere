#!/usr/bin/python3

import minimalmodbus
import time
from prj_logger import logging
from threading import Lock

from sys import platform as CURRENT_OS

RETURN_ERROR = -1
RETURN_OK    = 0
WAIT_TIME    = 0.5

if 'win32' == CURRENT_OS:
    PORT_COM = "COM3"
else:
    PORT_COM = "/dev/ttyUSB0"


class ModbusAccess:
    TIME_SLOT = 5
    WAITING_TIMEOUT = 0.4
    bimaster = 0

    def __init__(self):
        # Initialisation of Modbus
        minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = True
        self.instrument = minimalmodbus.Instrument(PORT_COM, 10)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        # seconds (0.05 par defaut)
        self.instrument.serial.timeout = 1
        self.instrument.debug = False   # True or False
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.mutex = Lock()

    def wait_time_slot(self):
        """
        Manage master/slave bus priority
        :return:
        """
        # if not in bimaster mode no need to wait
        if not self.bimaster:
            return

        # Wait a maximum of 3 cycle SLAVE => MASTER => SLAVE
        maximum_loop = 1 + int(self.TIME_SLOT * 3 / self.WAITING_TIMEOUT)
        self.instrument.serial.timeout = self.WAITING_TIMEOUT
        # read until boiler is master
        self.instrument.serial.open()
        data = b''
        number_of_wait = 0
        logging.debug("Wait the peer to be master.")
        # wait a maximum of 6 seconds
        while len(data) == 0 and number_of_wait < maximum_loop:
            data = self.instrument.serial.read(100)
            number_of_wait += 1
        if number_of_wait >= maximum_loop:
            logging.warning("Never get data from peer. Remove --bimaster flag.")
        # the master is the boiler wait for the end of data
            logging.debug("Wait the peer to be slave.")
        while len(data) != 0:
            data = self.instrument.serial.read(100)
        self.instrument.serial.close()
        self.instrument.serial.timeout = 1.0
        logging.debug("We are master.")
        # we are master for a maximum of  4.6s (5s - 400ms)

    def clear_serial_buffer(self):
        self.instrument.serial.timeout = 0.4
        self.instrument.serial.open()
        data = b''
        while len(data) != 0:
            data = self.instrument.serial.read(100)
        self.instrument.serial.close()
        self.instrument.serial.timeout = 1.0
        #time.sleep(0.1)


    def __write_simple_register(self, registeraddress, value, num_of_decimal=0):
        """
        Private method
        Boiler write access
        :param registeraddress: regiters to be writen
        :param value: value to write
        :param num_of_decimal: Optional decimal precision
        :return: 0 if Ok -1 on exception
        """
        retry = 0
        ret = RETURN_ERROR
        str_err = ""

        self.clear_serial_buffer()

        while retry < 5:
            try:
                if num_of_decimal == 1:
                    value *= 1.0
                    value = round(value * 2) / 2

                self.instrument.write_register(registeraddress, value, num_of_decimal)
                logging.debug(
                    "Write from register %d value(%s) decimal=%d" % (registeraddress, str(value), num_of_decimal))
                ret = RETURN_OK
                break

            except TypeError:
                str_err += "Retry(" + str(retry) + ") : I/O error " + str(registeraddress) + "\n"
                ret = RETURN_ERROR
            except ValueError:
                str_err += "Retry(" + str(retry) + ") : Value error " + str(registeraddress) + "\n"
                ret = RETURN_ERROR
            except IOError:
                str_err += "Retry(" + str(retry) + ") : IO error " + str(registeraddress) + "\n"
                ret = RETURN_ERROR

            time.sleep(0.3)
            retry += 1

        if RETURN_ERROR == ret:
            logging.exception(str_err)
            raise SystemExit("Bus is not available max write retries was reached for reg(%d). "
                          "Kill programm" % registeraddress)

        return ret

    def write_register(self, registeraddress, value, num_of_decimal=0):
        """
        Write a register
        :param registeraddress: regiters to be writen
        :param value: value to write
        :param num_of_decimal: Optional decimal precision
        :return: 0 if Ok -1 on exception
        """
        self.mutex.acquire()
        #self.wait_time_slot()
        ret = self.__write_simple_register(registeraddress, value, num_of_decimal)
        self.mutex.release()
        return ret

    # reg_desc list [ regId, value, Decimal ]
    def write_multiple_registers(self, reg_desc):
        """
        Write multiple non contiguous register
        :param reg_desc: Map of reg to write
        :return: 0 if Ok -1 on exception
        """
        self.mutex.acquire()
        #self.wait_time_slot()
        ret = RETURN_OK

        for i in range(len(reg_desc)):
            if ret != RETURN_ERROR:
                ret = self.__write_simple_register(reg_desc[i][0], reg_desc[i][1], reg_desc[i][2])
            else:
                break

        self.mutex.release()
        return ret

    # The number of registers that will be written is defined by the
    # length of the values list.
    def write_area(self, registeraddress, values):
        """
        Write multiple contiguous registers
        :param registeraddress: register base address
        :param values: list of value to be writen
        :return:
        """
        self.mutex.acquire()
        #self.wait_time_slot()
        retry = 0
        ret = RETURN_ERROR
        str_err = ""

        self.clear_serial_buffer()

        while retry < 5:
            try:
                self.instrument.write_registers(registeraddress, values)
                logging.debug("Write from register %d list of values(%s)" % (registeraddress, str(values)))
                ret = RETURN_OK
                break

            except TypeError:
                str_err += "Retry(" + str(retry) + ") : I/O error " + str(registeraddress) + "\n"
                ret = RETURN_ERROR
            except ValueError:
                str_err += "Retry(" + str(retry) + ") : Value error " + str(registeraddress) + "\n"
                ret = RETURN_ERROR
            except IOError:
                str_err += "Retry(" + str(retry) + ") : IO error " + str(registeraddress) + "\n"
                ret = RETURN_ERROR

            time.sleep(0.3)
            retry += 1

        self.mutex.release()
        if RETURN_ERROR == ret:
            logging.exception(str_err)
            raise SystemExit("Bus is not available max write retries was reached for reg(%d). "
                          "Kill programm" % registeraddress)

        return ret

    # Private methode don't call it directly
    def __read_simple_register(self, registeraddress, num_of_decimal=0):
        """
        Private method
        Boiler read access
        :param registeraddress: register address to access
        :param num_of_decimal: decimal precision
        :return: Register value if OK or None if error
        """
        retry = 0
        ret = None
        str_err = ""

        self.clear_serial_buffer()

        while retry < 5:
            try:
                ret = self.instrument.read_register(registeraddress, num_of_decimal)
                break
            except TypeError:
                str_err += "Retry(" + str(retry) + ") : I/O error " + str(registeraddress) + "\n"
                ret = None
            except ValueError:
                str_err += "Retry(" + str(retry) + ") : Value error " + str(registeraddress) + "\n"
                ret = None
            except IOError:
                str_err += "Retry(" + str(retry) + ") : IO error " + str(registeraddress) + "\n"
                ret = None

            time.sleep(WAIT_TIME)
            retry += 1

        if ret is None and retry != 0:
            logging.exception(str_err)
            raise SystemExit("Bus is not available max read retries was reached for reg(%d)."
                          "Kill programm" % registeraddress)

        return ret

    def read_register(self, registeraddress, num_of_decimal=0):
        """
        Read register
        :param registeraddress: resgister address
        :param num_of_decimal: Decimal precision
        :return: Register value if OK or None if error
        """
        self.mutex.acquire()
        #self.wait_time_slot()

        ret = self.__read_simple_register(registeraddress, num_of_decimal)

        self.mutex.release()
        return ret

    def read_multiple_register(self, reg_desc):
        """
        Read multiple non contiguous register
        :param reg_desc: map of register to be
        :return: Map of register read
        """
        self.mutex.acquire()
        #self.wait_time_slot()
        ret = None

        data_array = None
        for reg, decimal in reg_desc.items():
            ret = self.__read_simple_register(reg, decimal)
            if ret is not None:
                data_array[reg] = ret

        self.mutex.release()
        return data_array

    def read_area(self, base_address, number_of_value):
        """
        Read multiple contiguous register
        :param base_address: base address
        :param number_of_value: number of register to read
        :return:
        """
        self.mutex.acquire()
        #self.wait_time_slot()
        raw_values = []
        retry = 0
        ret = None
        str_err = ""

        self.clear_serial_buffer()

        while retry < 5:
            try:
                raw_values = self.instrument.read_registers(base_address, number_of_value)
                ret = raw_values
                break

            except TypeError:
                str_err += "Retry(" + str(retry) + ") : I/O error " + str(base_address) + "\n"
                ret = None
            except ValueError:
                str_err += "Retry(" + str(retry) + ") : Value error " + str(base_address) + "\n"
                ret = None
            except IOError:
                str_err += "Retry(" + str(retry) + ") : IO error " + str(base_address) + "\n"
                ret = None

            time.sleep(WAIT_TIME)
            retry += 1

        self.mutex.release()
        if ret is None and retry != 0:
            logging.exception(str_err)
            raise SystemExit("Bus is not available max read retryies was reached for reg(%d)."
                          "Kill programm" % base_address)

        logging.debug("Reading from register %d list of values(%s)" % (base_address, str(raw_values)))
        return ret
