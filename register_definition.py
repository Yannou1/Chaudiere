import os, sys

MODE_HIVER = 1
MODE_ETE   = 0

NEGATIVE_VALUE_POINT = 3276.8  #32768/10

TYPE_THERMOSTAT  = 50
TYPE_ECS         = 51
TYPE_TEMPERATURE = 52
TYPE_PROG        = 53
TYPE_HEATER      = 54
TYPE_ALERT       = 55
TYPE_DEROG       = 56
TYPE_REMOTE      = 57
TYPE_ECS_WEEK    = 58



# DE DIETRICH DIEMATIC M3 REGISTER DESCRIPTION
FREEFROST_DAY               = 724   # OK
# ANTI_FROST_TEMP             = 300   # Not used
OUTSIDE_TEMP                 = 601   # OK
ECS_TEMP                     = 603   # OK ou 459
TEMP_SETPOINT_ECS            = 672   # TO BE CHECKED
TEMP_AMBIANT_CIRCUIT_A       = 614   # OK Not monitored because no sensor in floor1
TEMP_SETPOINT_CONFORT_A      = 650   # OK
TEMP_SETPOINT_ECO_A          = 651   # OK
TEMP_SETPOINT_FREEFROST_A    = 652   # OK
TEMP_AMBIANT_CIRCUIT_B       = 616   # OK
TEMP_SETPOINT_CONFORT_B      = 656   # OK
AMBIANT_TEMP                 = TEMP_AMBIANT_CIRCUIT_B   # OK Non monitoré car temp bas

TEMP_SETPOINT_ECO_B          = 657   # OK
TEMP_SETPOINT_FREEFROST_B    = 658   # OK
PROG_NUM_A                   = 231   # OK
PROG_NUM_B                   = 232   # OK
BOILER_SW_MODE               = 400  # Virtual register not present in boiler
DEROGATION_REMOTE_1          = 94    # OK Read only
DEROGATION_CIRCUIT_A         = 653   # OK
DEROGATION_CIRCUIT_B         = 659

REG_DAY_PROG_ECS             = 189  # ECS Lundi 0-->8H
REG_DAY_PROG_AUX             = 210  # ECS Lundi 0-->8H

REG_DAY_DELTA_ECS_AUX        = REG_DAY_PROG_AUX - REG_DAY_PROG_ECS

ECS_MON                      = REG_DAY_PROG_AUX
ECS_TUE                      = ECS_MON + 3
ECS_WED                      = ECS_MON + 6
ECS_THU                      = ECS_MON + 9
ECS_FRI                      = ECS_MON + 12
ECS_SAT                      = ECS_MON + 15
ECS_SUN                      = ECS_MON + 18

REG_DAY_AUX_LAST_ID          = ECS_SUN + 2
REG_DAY_ECS_LAST_ID          = (REG_DAY_AUX_LAST_ID - REG_DAY_PROG_AUX + REG_DAY_PROG_ECS)

VIRTUAL_IDX                  = 800    # Monitored but not updated on domoticz

ECS_ALL_DAYS_IN_WEEK         = 300



NO_PERIOD = None
MONITORED = True

# Column name
COL_IDX               = 0
COL_REGISTER          = 1
COL_SENSOR_TYPE       = 2
COL_MON               = 3
COL_MONITORING_PERIOD = 4
COL_NOT_ALLOWED_VALUE = 5


if ("pytest" in sys.modules) or ("1" == os.environ.get("STUBBED_MODE")):
    TEMP_PERIOD = 300  # 1min
    ECS_PERIOD  = 60
    IDX_FREEFROST_DAY = 1

    CONFIG_TABLE = (
         (  IDX_FREEFROST_DAY,              FREEFROST_DAY,         TYPE_ALERT,     MONITORED,            60,   []),
                        (   3,               OUTSIDE_TEMP,   TYPE_TEMPERATURE,     MONITORED,     TEMP_PERIOD, []),
                        (   4,               AMBIANT_TEMP,   TYPE_TEMPERATURE,     MONITORED,     TEMP_PERIOD, []),
                        (   5,                   ECS_TEMP,   TYPE_TEMPERATURE,     MONITORED,     TEMP_PERIOD, []),
                        (   6,          TEMP_SETPOINT_ECS,    TYPE_THERMOSTAT,     MONITORED,     TEMP_PERIOD, []),
      #                 (   7,     TEMP_AMBIANT_CIRCUIT_A,   TYPE_TEMPERATURE, NOT_MONITORED,     NO_PERIOD,   []),
                        (   8,    TEMP_SETPOINT_CONFORT_A,    TYPE_THERMOSTAT,     MONITORED,     TEMP_PERIOD, []),
                        (   9,        TEMP_SETPOINT_ECO_A,    TYPE_THERMOSTAT,     MONITORED,     TEMP_PERIOD, []),
                        (  10,  TEMP_SETPOINT_FREEFROST_A,    TYPE_THERMOSTAT,     MONITORED,     TEMP_PERIOD, []),
      #                 (  11,     TEMP_AMBIANT_CIRCUIT_B,   TYPE_TEMPERATURE,     MONITORED,     NO_PERIOD,   []),
                        (  12,    TEMP_SETPOINT_CONFORT_B,    TYPE_THERMOSTAT,     MONITORED,     TEMP_PERIOD, []),
                        (  13,        TEMP_SETPOINT_ECO_B,    TYPE_THERMOSTAT,     MONITORED,     TEMP_PERIOD, []),
                        (  14,  TEMP_SETPOINT_FREEFROST_B,    TYPE_THERMOSTAT,     MONITORED,     TEMP_PERIOD, []),
                        (  15,             BOILER_SW_MODE,        TYPE_HEATER,     MONITORED,             30,  []),
                        (  16,       DEROGATION_CIRCUIT_A,         TYPE_DEROG,     MONITORED,             10,  []),
                        (  17,       DEROGATION_CIRCUIT_B,         TYPE_DEROG,     MONITORED,             10,  []),
                        (  34,        DEROGATION_REMOTE_1,        TYPE_REMOTE,     MONITORED,             60,  []),
                        (  22,                    ECS_MON,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  822,                  ECS_MON+1,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  922,                  ECS_MON+2,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                        (  23,                    ECS_TUE,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  823,                  ECS_TUE+1,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  923,                  ECS_TUE+2,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                        (  24,                    ECS_WED,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  824,                  ECS_WED+1,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  924,                  ECS_WED+2,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                        (  25,                    ECS_THU,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  825,                  ECS_THU+1,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  925,                  ECS_THU+2,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                        (  26,                    ECS_FRI,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  826,                  ECS_FRI+1,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  926,                  ECS_FRI+2,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                        (  27,                    ECS_SAT,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  827,                  ECS_SAT+1,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  927,                  ECS_SAT+2,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                        (  28,                    ECS_SUN,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  828,                  ECS_SUN+1,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (  928,                  ECS_SUN+2,           TYPE_ECS,     MONITORED,     ECS_PERIOD,  []),
                       (   35,       ECS_ALL_DAYS_IN_WEEK,      TYPE_ECS_WEEK, not MONITORED,     NO_PERIOD,   []),
                       (   36,       ECS_ALL_DAYS_IN_WEEK,      TYPE_ECS_WEEK, not MONITORED,     NO_PERIOD,   []),
                       (  100,                 PROG_NUM_A,          TYPE_PROG, not MONITORED,     NO_PERIOD,   []),
                       (  101,                 PROG_NUM_B,          TYPE_PROG, not MONITORED,     NO_PERIOD,   []),

                        #(  101,                 PROG_NUM_B,          TYPE_PROG, not MONITORED,    NO_PERIOD,   []),
                        )
else:
    REGULAR_PERIOD = 30
    TEMP_PERIOD = 300  # 5min
    ECS_PERIOD  = 120
    IDX_FREEFROST_DAY = 10
    #                      idx,        sensor function,         sensors type
    CONFIG_TABLE = (
         (  IDX_FREEFROST_DAY,             FREEFROST_DAY,          TYPE_ALERT,  MONITORED, REGULAR_PERIOD,    []),
      #                 (   12,            ANTI_FROST_TEMP,  TYPE_TEMPERATURE,  MONITORED,    TEMP_PERIOD,    []),
                        (  12,               OUTSIDE_TEMP,   TYPE_TEMPERATURE, MONITORED,     TEMP_PERIOD,    []),
                        (  13,               AMBIANT_TEMP,   TYPE_TEMPERATURE, MONITORED,     TEMP_PERIOD,    []),
                        (  14,                   ECS_TEMP,   TYPE_TEMPERATURE, MONITORED,     TEMP_PERIOD,    []),
                        (  15,          TEMP_SETPOINT_ECS,    TYPE_THERMOSTAT, MONITORED,     TEMP_PERIOD,    []),
      #                 (  16,     TEMP_AMBIANT_CIRCUIT_A,   TYPE_TEMPERATURE, not MONITORED, TEMP_PERIOD,    []),
                        (  17,    TEMP_SETPOINT_CONFORT_A,    TYPE_THERMOSTAT, MONITORED,     TEMP_PERIOD,    []),
                        (  18,        TEMP_SETPOINT_ECO_A,    TYPE_THERMOSTAT, MONITORED,     TEMP_PERIOD,    []),
                        (  19,  TEMP_SETPOINT_FREEFROST_A,    TYPE_THERMOSTAT, MONITORED,     TEMP_PERIOD,    []),
                        (  20,     TEMP_AMBIANT_CIRCUIT_B,   TYPE_TEMPERATURE, MONITORED,     TEMP_PERIOD,    []),
                        (  21,    TEMP_SETPOINT_CONFORT_B,    TYPE_THERMOSTAT, MONITORED,     TEMP_PERIOD,    []),
                        (  22,        TEMP_SETPOINT_ECO_B,    TYPE_THERMOSTAT, MONITORED,     TEMP_PERIOD,    []),
                        (  23,  TEMP_SETPOINT_FREEFROST_B,    TYPE_THERMOSTAT, MONITORED,     TEMP_PERIOD,    []),
                        (  24,       DEROGATION_CIRCUIT_A,         TYPE_DEROG, MONITORED,  REGULAR_PERIOD,    [0]),
                        (  25,       DEROGATION_CIRCUIT_B,         TYPE_DEROG, MONITORED,  REGULAR_PERIOD,    [0]),
                        (  26,        DEROGATION_REMOTE_1,        TYPE_REMOTE, MONITORED,2*REGULAR_PERIOD,    []),
                        (  27,             BOILER_SW_MODE,        TYPE_HEATER, MONITORED,  REGULAR_PERIOD,    []),
                        (  29,                    ECS_MON,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 829,                ECS_MON + 1,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 929,                ECS_MON + 2,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        (  30,                    ECS_TUE,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 830,                ECS_TUE + 1,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 930,                ECS_TUE + 2,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        (  31,                    ECS_WED,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 831,                ECS_WED + 1,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 931,                ECS_WED + 2,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        (  32,                    ECS_THU,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 832,                ECS_THU + 1,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 932,                ECS_THU + 2,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        (  33,                    ECS_FRI,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 833,                ECS_FRI + 1,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 933,                ECS_FRI + 2,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        (  34,                    ECS_SAT,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 834,                ECS_SAT + 1,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 934,                ECS_SAT + 2,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        (  35,                    ECS_SUN,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 835,                ECS_SUN + 1,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        ( 935,                ECS_SUN + 2,           TYPE_ECS, MONITORED,      ECS_PERIOD,    []),
                        (  41,       ECS_ALL_DAYS_IN_WEEK,       TYPE_ECS_WEEK, not MONITORED, NO_PERIOD,     []), #On
                        (  40,       ECS_ALL_DAYS_IN_WEEK,       TYPE_ECS_WEEK, not MONITORED, NO_PERIOD,     []), #Off
                        (  43,                 PROG_NUM_A,           TYPE_PROG, not MONITORED, REGULAR_PERIOD,     []),
                        (  44,                 PROG_NUM_B,           TYPE_PROG, not MONITORED, REGULAR_PERIOD,     []),
                        )
# Boiler status defines
STATE_ABSENT  = 10   # "ABSENT"
STATE_WEEKEND = 20   # "WEEK-END"
STATE_PRESENT = 30   # "PRESENT"

valid_parameter = [STATE_ABSENT, STATE_WEEKEND, STATE_PRESENT]


#BOILER_CFG = (STATE_ABSENT, STATE_PRESENT, STATE_WEEKEND)
NBR_CONFIG = 3

SIZE_OF_ECS_CONFIG = 21
ECS_INITIALIZED = 0

def get_system_config():
    return CONFIG_TABLE

def is_valid_state(state):
    valid_parameter = [STATE_ABSENT, STATE_WEEKEND, STATE_PRESENT]
    if state not in valid_parameter:
        return False
    else:
        return True