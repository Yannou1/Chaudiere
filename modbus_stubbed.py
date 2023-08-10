#!/usr/bin/python

import time
import random
from prj_logger import logging
from threading import Lock
import register_definition as reg

SUMMER_FLAG_FEATURE = 1

RETURN_OK    = 0
RETURN_ERROR = -1

boiler_reg = {}
MODULO_VAL = 5
READ_SEQ_NBR = 0
BOILER_WINTER = not SUMMER_FLAG_FEATURE

if not BOILER_WINTER:
    boiler_reg[reg.FREEFROST_DAY] = 0

boiler_reg[reg.DEROGATION_CIRCUIT_A] = 8
boiler_reg[reg.DEROGATION_CIRCUIT_B] = 8
boiler_reg[reg.DEROGATION_REMOTE_1]  = 0x10
boiler_reg[reg.REG_DAY_PROG_ECS]  = 65535
boiler_reg[reg.REG_DAY_PROG_AUX]  = 65535
boiler_reg[reg.REG_DAY_PROG_ECS+6]  = 65535
boiler_reg[reg.REG_DAY_PROG_AUX+6]  = 65535

class ModbusStubbed:

    def __init__(self):
        self.mutex = Lock()

    def __write_simple_register(self, registeraddress, value, num_of_decimal=0):
        """
        Private method
        Boiler write access
        :param registeraddress: regiters to be writen
        :param value: value to write
        :param num_of_decimal: Optional decimal precision
        :return: 0 if Ok -1 on exception
        """
        if num_of_decimal == 1:
            value = value * 1.0
            value = round(value * 2) / 2

        if (724 == registeraddress):
            if value == 0:
                if 1 == boiler_reg.get(reg.DEROGATION_CIRCUIT_A):
                    boiler_reg[reg.DEROGATION_CIRCUIT_A] = 8
                    boiler_reg[reg.DEROGATION_CIRCUIT_B] = 8
            else:
                if 1 != boiler_reg.get(reg.DEROGATION_CIRCUIT_A):
                    boiler_reg[reg.DEROGATION_CIRCUIT_A] = 1
                    boiler_reg[reg.DEROGATION_CIRCUIT_B] = 1

        logging.info("Stubbed write reg %d value %s" % (registeraddress, str(value)))
        boiler_reg[registeraddress] = value

        return RETURN_OK

    def write_register(self, registeraddress, value, num_of_decimal=0):
        """
        Write a register
        :param registeraddress: regiters to be writen
        :param value: value to write
        :param num_of_decimal: Optional decimal precision
        :return: 0 if Ok -1 on exception
        """
        self.mutex.acquire()
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
        ret = RETURN_OK

        for i in range(len(reg_desc)):
            if RETURN_ERROR != ret:
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
        start_time = time.time()

        for i in range(len(values)):
            reg = registeraddress + i
            boiler_reg[reg] = values[i]

        mystr = "Stubbed write from reg " + str(registeraddress) + " values " + str(values)
        logging.info(mystr)

        duration = time.time() - start_time
        logging.debug("Write take %1.3fs", duration)
        self.mutex.release()
        return RETURN_OK

    # Private methode don't call it directly
    def __read_simple_register(self, registeraddress, num_of_decimal=0):
        """
        Private method
        Boiler read access
        :param registeraddress: register address to access
        :param num_of_decimal: decimal precision
        :return: Register value if OK or None if error
        """
        global READ_SEQ_NBR

        value = boiler_reg.get(registeraddress)
        if value is None or (READ_SEQ_NBR % MODULO_VAL == 0):
            if registeraddress == reg.DEROGATION_REMOTE_1:
                value = BOILER_WINTER
                boiler_reg[reg.DEROGATION_CIRCUIT_A] = 8
                boiler_reg[reg.DEROGATION_CIRCUIT_B] = 8
            elif registeraddress == reg.DEROGATION_CIRCUIT_A or registeraddress == reg.DEROGATION_CIRCUIT_B:
                reg94 = boiler_reg.get(reg.DEROGATION_REMOTE_1)
                if reg94 is None:
                    boiler_reg[reg.DEROGATION_REMOTE_1] = BOILER_WINTER

                rand = random.randint(0, 2)
                derog = (2, 4, 8)
                value = derog[rand]
            elif (registeraddress >= reg.REG_DAY_PROG_ECS and registeraddress <= reg.REG_DAY_PROG_ECS + 21) \
                or (registeraddress >= reg.REG_DAY_PROG_AUX and registeraddress <= reg.REG_DAY_PROG_AUX + 21):
                if boiler_reg.get(registeraddress) is None:
                   value = 0
            else:
                value = random.randint(0, 70)
                if registeraddress == reg.FREEFROST_DAY:
                    if value == 0:
                        if boiler_reg.get(reg.DEROGATION_CIRCUIT_B) is None:
                            boiler_reg[reg.DEROGATION_CIRCUIT_B] = 8
                            boiler_reg[reg.DEROGATION_CIRCUIT_A] = 8
                        elif boiler_reg.get(reg.DEROGATION_CIRCUIT_B) <= 1:
                            boiler_reg[reg.DEROGATION_CIRCUIT_B] = 8
                            boiler_reg[reg.DEROGATION_CIRCUIT_A] = 8
                        else:
                            pass
                    else:
                        if BOILER_WINTER is False:
                            value = 0
                        boiler_reg[reg.DEROGATION_CIRCUIT_B] = 1

            boiler_reg[registeraddress] = value
            logging.info("Reading register %d new value=%s" % (registeraddress, str(value)))
        else:
            #print("Read from cache register(%d) value=%d " % (registeraddress, value))
            pass

        READ_SEQ_NBR += 1

        return value

    def read_register(self, registeraddress, num_of_decimal=0):
        """
        Read register
        :param registeraddress: resgister address
        :param num_of_decimal: Decimal precision
        :return: Register value if OK or None if error
        """
        self.mutex.acquire()

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

        data_array = {}

        for reg, decimal in reg_desc.items():
            data_array[reg] = self.__read_simple_register(reg, decimal)

        ret = data_array

        self.mutex.release()
        return ret

    def read_area(self, base_address, number_of_value):
        """
        Read multiple contiguous register
        :param base_address: base address
        :param number_of_value: number of register to read
        :return:
        """
        global READ_SEQ_NBR
        raw_values = []
        update_val = 0

        self.mutex.acquire()
        start_time = time.time()

        #if READ_SEQ_NBR % MODULO_VAL == 0:
        #    update_val = 1

        for i in range(0, number_of_value):
            value = boiler_reg.get(base_address+i)

            if value is None :
                boiler_reg[base_address + i] = value = random.randint(0, 1) * 0

            raw_values.append(value)

        if value is None or (update_val == 1):
            my_string = "Reading from register " + str(base_address) + " new value ==>" + str(raw_values)
        else:
            my_string = "Reading from cache register " + str(base_address) + " new value ==>" + str(raw_values)

        logging.debug(my_string)

        READ_SEQ_NBR += 1
        duration = time.time() - start_time
        logging.debug("Read take %1.3fs", duration)

        self.mutex.release()
        return raw_values

