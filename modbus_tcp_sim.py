import logging
import random
import time
import struct
from threading import Thread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext

# Logs
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s')
log = logging.getLogger()
log.setLevel(logging.INFO)

# IP y puerto del servidor Modbus
SERVER_HOST = "192.168.2.229"
SERVER_PORT = 502
SLAVE_ID = 1

# Direcciones de registros
ALM_COOLER_FREEZE_F = 0  # Entrada digital

# Holding registers (escritura/lectura)
SETPOINT_csp1 = 899
SETPOINT_csp2 = 901
SETPOINT_ice_sp = 903
SETPOINT_hsp1 = 905
SETPOINT_hsp2 = 907
SETPOINT_lim_sp1 = 909
SETPOINT_lim_sp2 = 911
SETPOINT_lim_sp3 = 913
PROTOCOL_CTRL_PNT = 3009
PROTOCOL_DEM_LIM = 3013
PROTOCOL_CHIL_S_S = 3021
PROTOCOL_EMSTOP = 3023
GENCONF_ice_cnfg = 4099
GENCONF_pow_max = 4117
GENCONF_pow_sel = 4119

# Input registers (solo lectura)
TEMP_OAT = 3
CAPACTRL_ctrl_wt = 5
TEMP_CHWSTEMP = 7
GENUNIT_CTRL_PNT = 9
GENUNIT_SP = 11
GENUNIT_CHIL_S_S = 21
GENUNIT_EMSTOP = 23
UNIT_STATUS = 41
PRESSURE_EWATPRES = 71
PRESSURE_LWATPRES = 73
ALARMRST_alarm_1c = 1099
UNIT_ALM = 1119
RECLAIM_HR_EWT = 9107
RECLAIM_HR_LWT = 9109

# Cantidad de registros
NUM_DISCRETE_INPUTS = 1
NUM_COILS = 1
NUM_HOLDING_REGISTERS = max([SETPOINT_csp1, SETPOINT_csp2, SETPOINT_ice_sp, SETPOINT_hsp1, 
                            SETPOINT_hsp2, SETPOINT_lim_sp1, SETPOINT_lim_sp2, SETPOINT_lim_sp3,
                            PROTOCOL_CTRL_PNT, PROTOCOL_DEM_LIM, PROTOCOL_CHIL_S_S, PROTOCOL_EMSTOP,
                            GENCONF_ice_cnfg, GENCONF_pow_max, GENCONF_pow_sel]) + 2

NUM_INPUT_REGISTERS = max([TEMP_OAT, CAPACTRL_ctrl_wt, TEMP_CHWSTEMP, GENUNIT_CTRL_PNT, 
                          GENUNIT_SP, GENUNIT_CHIL_S_S, GENUNIT_EMSTOP, UNIT_STATUS,
                          PRESSURE_EWATPRES, PRESSURE_LWATPRES, ALARMRST_alarm_1c, 
                          UNIT_ALM, RECLAIM_HR_EWT, RECLAIM_HR_LWT]) + 2

# Convierte float a 2 registros de 16 bits
def float_to_registers(value):
    packed = struct.pack('>f', value)
    return struct.unpack('>HH', packed)

# Convierte uint32 a 2 registros de 16 bits
def uint32_to_registers(value):
    return (value >> 16) & 0xFFFF, value & 0xFFFF

# Inicializa los bloques de memoria Modbus
def initialize_datastore():
    di_block = ModbusSequentialDataBlock(0, [0] * NUM_DISCRETE_INPUTS)
    co_block = ModbusSequentialDataBlock(0, [0] * NUM_COILS)
    hr_block = ModbusSequentialDataBlock(0, [0] * NUM_HOLDING_REGISTERS)
    ir_block = ModbusSequentialDataBlock(0, [0] * NUM_INPUT_REGISTERS)
    
    return ModbusSlaveContext(
        di=di_block,
        co=co_block,
        hr=hr_block,
        ir=ir_block
    )

# Actualiza los registros con valores aleatorios
def update_registers(context):
    store = context[SLAVE_ID]
    
    while True:
        try:
            # Entrada digital aleatoria
            store.setValues(2, ALM_COOLER_FREEZE_F, [random.choice([0, 1])])
            
            # Holding registers - floats aleatorios
            csp1 = random.uniform(44, 78.8)
            store.setValues(3, SETPOINT_csp1, list(float_to_registers(csp1)))
            
            csp2 = random.uniform(44, 78.8)
            store.setValues(3, SETPOINT_csp2, list(float_to_registers(csp2)))
            
            ice_sp = random.uniform(44, 78.8)
            store.setValues(3, SETPOINT_ice_sp, list(float_to_registers(ice_sp)))
            
            hsp1 = random.uniform(80, 145.4)
            store.setValues(3, SETPOINT_hsp1, list(float_to_registers(hsp1)))
            
            hsp2 = random.uniform(80, 145.4)
            store.setValues(3, SETPOINT_hsp2, list(float_to_registers(hsp2)))
            
            ctrl_pnt = random.uniform(-4, 153)
            store.setValues(3, PROTOCOL_CTRL_PNT, list(float_to_registers(ctrl_pnt)))
            
            # Input registers - floats aleatorios
            oat = random.uniform(-20, 50)
            store.setValues(4, TEMP_OAT, list(float_to_registers(oat)))
            
            ctrl_wt = random.uniform(40, 60)
            store.setValues(4, CAPACTRL_ctrl_wt, list(float_to_registers(ctrl_wt)))
            
            # Log info
            log.info(f"Updated - Cooling SP1: {csp1:.1f}°F | Outdoor Temp: {oat:.1f}°F | Water Temp: {ctrl_wt:.1f}°F")
            
            time.sleep(2)
        except Exception as e:
            log.error(f"Update error: {str(e)}")
            time.sleep(1)

# Inicia el servidor Modbus
def run_server():
    store = initialize_datastore()
    context = ModbusServerContext(slaves={SLAVE_ID: store}, single=False)
    
    # Hilo para simular datos
    update_thread = Thread(target=update_registers, args=(context,), daemon=True)
    update_thread.start()
    
    # Mensajes de inicio
    log.info(f"\n{'='*60}")
    log.info(f"Modbus Server running at {SERVER_HOST}:{SERVER_PORT}")
    log.info(f"Slave ID: {SLAVE_ID}")
    log.info(f"{'='*60}")
    log.info("Register Mapping:")
    log.info(f"Discrete Inputs: 1-{NUM_DISCRETE_INPUTS}")
    log.info(f"Holding Registers: 1-{NUM_HOLDING_REGISTERS}")
    log.info(f"Input Registers: 1-{NUM_INPUT_REGISTERS}")
    log.info(f"{'='*60}\n")
    
    try:
        StartTcpServer(context, address=(SERVER_HOST, SERVER_PORT))
    except KeyboardInterrupt:
        log.info("Server parado por usuario")
    except Exception as e:
        log.error(f"Error del servidor: {str(e)}")

# Arranca todo
if __name__ == "__main__":
    run_server()
