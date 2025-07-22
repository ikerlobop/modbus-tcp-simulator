import logging
import random
import time
import struct
from threading import Thread
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusSequentialDataBlock
from pymodbus.datastore import ModbusServerContext

# Configure logging
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s')
log = logging.getLogger()
log.setLevel(logging.INFO)

# Server configuration
SERVER_HOST = "192.168.2.229"
SERVER_PORT = 502
SLAVE_ID = 255

# Definición de todas las variables con sus propiedades
VARIABLES = [
    # Discrete Inputs (1-bit BOOL)
    {
        'name': 'ALM_COOLER_FREEZE_F',
        'block': 2,  # DI
        'address': 0,  # Modbus address 1
        'data_type': 'bool',
        'min': 0,
        'max': 1
    },
    
    # Holding Registers (32-bit)
    {
        'name': 'SETPOINT_csp1',
        'block': 3,  # HR
        'address': 899,  # Modbus address 900
        'data_type': 'float32',
        'min': -28.88,
        'max': 26.00
    },
    {
        'name': 'SETPOINT_csp2',
        'block': 3,
        'address': 901,  # Modbus address 902
        'data_type': 'float32',
        'min': -28.88,
        'max': 26.00
    },
    {
        'name': 'SETPOINT_ice_sp',
        'block': 3,
        'address': 903,  # Modbus address 904
        'data_type': 'float32',
        'min': -28.88,
        'max': 26.00
    },
    {
        'name': 'SETPOINT_hsp1',
        'block': 3,
        'address': 905,  # Modbus address 906
        'data_type': 'float32',
        'min': -28.88,
        'max': 26.00
    },
    {
        'name': 'SETPOINT_hsp2',
        'block': 3,
        'address': 907,  # Modbus address 908
        'data_type': 'float32',
        'min': -28.88,
        'max': 26.00
    },
    {
        'name': 'SETPOINT_lim_sp1',
        'block': 3,
        'address': 909,  # Modbus address 910
        'data_type': 'uint32',
        'min': 0,
        'max': 100
    },
    {
        'name': 'SETPOINT_lim_sp2',
        'block': 3,
        'address': 911,  # Modbus address 912
        'data_type': 'uint32',
        'min': 0,
        'max': 100
    },
    {
        'name': 'SETPOINT_lim_sp3',
        'block': 3,
        'address': 913,  # Modbus address 914
        'data_type': 'uint32',
        'min': 0,
        'max': 100
    },
    {
        'name': 'PROTOCOL_CTRL_PNT',
        'block': 3,
        'address': 3009,  # Modbus address 3010
        'data_type': 'float32',
        'min': -4,
        'max': 153
    },
    {
        'name': 'PROTOCOL_DEM_LIM',
        'block': 3,
        'address': 3013,  # Modbus address 3014
        'data_type': 'uint32',
        'min': 0,
        'max': 100
    },
    {
        'name': 'PROTOCOL_CHIL_S_S',
        'block': 3,
        'address': 3021,  # Modbus address 3022
        'data_type': 'uint32',
        'min': 0,
        'max': 1
    },
    {
        'name': 'PROTOCOL_EMSTOP',
        'block': 3,
        'address': 3023,  # Modbus address 3024
        'data_type': 'uint32',
        'min': 0,
        'max': 1
    },
    {
        'name': 'GENCONF_ice_cnfg',
        'block': 3,
        'address': 4099,  # Modbus address 4100
        'data_type': 'uint32',
        'min': 0,
        'max': 1
    },
    {
        'name': 'GENCONF_pow_max',
        'block': 3,
        'address': 4117,  # Modbus address 4118
        'data_type': 'float32',
        'min': 0,
        'max': 2000
    },
    {
        'name': 'GENCONF_pow_sel',
        'block': 3,
        'address': 4119,  # Modbus address 4120
        'data_type': 'uint32',
        'min': 0,
        'max': 1
    },
    
    # Input Registers (32-bit)
    {
        'name': 'TEMP_OAT',
        'block': 4,  # IR
        'address': 3,  # Modbus address 4
        'data_type': 'float32',
        'min': -20,
        'max': 50
    },
    {
        'name': 'CAPACTRL_ctrl_wt',
        'block': 4,
        'address': 5,  # Modbus address 6
        'data_type': 'float32',
        'min': 40,
        'max': 60
    },
    {
        'name': 'TEMP_CHWSTEMP',
        'block': 4,
        'address': 7,  # Modbus address 8
        'data_type': 'float32',
        'min': 40,
        'max': 60
    },
    {
        'name': 'GENUNIT_CTRL_PNT',
        'block': 4,
        'address': 9,  # Modbus address 10
        'data_type': 'float32',
        'min': -4,
        'max': 153
    },
    {
        'name': 'GENUNIT_SP',
        'block': 4,
        'address': 11,  # Modbus address 12
        'data_type': 'float32',
        'min': -20,
        'max': 78.8
    },
    {
        'name': 'GENUNIT_CHIL_S_S',
        'block': 4,
        'address': 21,  # Modbus address 22
        'data_type': 'uint32',
        'min': 0,
        'max': 1
    },
    {
        'name': 'GENUNIT_EMSTOP',
        'block': 4,
        'address': 23,  # Modbus address 24
        'data_type': 'uint32',
        'min': 0,
        'max': 1
    },
    {
        'name': 'UNIT_STATUS',
        'block': 4,
        'address': 41,  # Modbus address 42
        'data_type': 'uint32',
        'min': 0,
        'max': 10
    },
    {
        'name': 'PRESSURE_EWATPRES',
        'block': 4,
        'address': 71,  # Modbus address 72
        'data_type': 'float32',
        'min': 0,
        'max': 100
    },
    {
        'name': 'PRESSURE_LWATPRES',
        'block': 4,
        'address': 73,  # Modbus address 74
        'data_type': 'float32',
        'min': 0,
        'max': 100
    },
    {
        'name': 'ALARMRST_alarm_1c',
        'block': 4,
        'address': 1099,  # Modbus address 1100
        'data_type': 'uint32',
        'min': 0,
        'max': 10
    },
    {
        'name': 'UNIT_ALM',
        'block': 4,
        'address': 1119,  # Modbus address 1120
        'data_type': 'uint32',
        'min': 0,
        'max': 10
    },
    {
        'name': 'RECLAIM_HR_EWT',
        'block': 4,
        'address': 9107,  # Modbus address 9108
        'data_type': 'float32',
        'min': 40,
        'max': 60
    },
    {
        'name': 'RECLAIM_HR_LWT',
        'block': 4,
        'address': 9109,  # Modbus address 9110
        'data_type': 'float32',
        'min': 40,
        'max': 60
    }
]

def float_to_registers(value):
    """Convert float to two Modbus registers (big-endian)."""
    packed = struct.pack('>f', value)
    return struct.unpack('>HH', packed)

def uint32_to_registers(value):
    """Convert uint32 to two Modbus registers (big-endian)."""
    return (value >> 16) & 0xFFFF, value & 0xFFFF

def calculate_block_sizes():
    """Calculate required sizes for each Modbus block."""
    # Discrete Inputs (DI)
    di_size = 1  # Minimum size
    
    # Holding Registers (HR)
    hr_max_address = 0
    for var in VARIABLES:
        if var['block'] == 3:  # HR block
            end_address = var['address'] + (1 if var['data_type'] == 'bool' else 2)
            if end_address > hr_max_address:
                hr_max_address = end_address
    hr_size = hr_max_address + 1
    
    # Input Registers (IR)
    ir_max_address = 0
    for var in VARIABLES:
        if var['block'] == 4:  # IR block
            end_address = var['address'] + (1 if var['data_type'] == 'bool' else 2)
            if end_address > ir_max_address:
                ir_max_address = end_address
    ir_size = ir_max_address + 1
    
    return di_size, 1, hr_size, ir_size  # (di, co, hr, ir)

def initialize_datastore(di_size, co_size, hr_size, ir_size):
    """Initialize all required datastores."""
    di_block = ModbusSequentialDataBlock(0, [0] * di_size)
    co_block = ModbusSequentialDataBlock(0, [0] * co_size)
    hr_block = ModbusSequentialDataBlock(0, [0] * hr_size)
    ir_block = ModbusSequentialDataBlock(0, [0] * ir_size)
    
    return ModbusSlaveContext(
        di=di_block,  # Discrete Inputs (1-bit, read-only)
        co=co_block,  # Coils (1-bit, read-write)
        hr=hr_block,  # Holding Registers (16-bit, read-write)
        ir=ir_block   # Input Registers (16-bit, read-only)
    )

def update_registers(context):
    """Update all registers with simulated values."""
    store = context[SLAVE_ID]
    
    while True:
        try:
            log_str = "Updated: "
            
            for var in VARIABLES:
                # Generate random value based on data type
                if var['data_type'] == 'bool':
                    value = random.choice([0, 1])
                    store.setValues(var['block'], var['address'], [value])
                    
                elif var['data_type'] == 'float32':
                    value = random.uniform(var['min'], var['max'])
                    regs = float_to_registers(value)
                    store.setValues(var['block'], var['address'], list(regs))
                    log_str += f"{var['name']}: {value:.1f} | "
                    
                elif var['data_type'] == 'uint32':
                    value = random.randint(int(var['min']), int(var['max']))
                    regs = uint32_to_registers(value)
                    store.setValues(var['block'], var['address'], list(regs))
                    log_str += f"{var['name']}: {value} | "
            
            log.info(log_str)
            time.sleep(2)
            
        except Exception as e:
            log.error(f"Update error: {str(e)}")
            time.sleep(1)

def run_server():
    """Start the Modbus TCP server."""
    # Calculate block sizes
    di_size, co_size, hr_size, ir_size = calculate_block_sizes()
    
    # Initialize datastore
    store = initialize_datastore(di_size, co_size, hr_size, ir_size)
    context = ModbusServerContext(slaves=store, single=True)  # Ignora slave IDs
    
    # Start update thread
    update_thread = Thread(target=update_registers, args=(context,), daemon=True)
    update_thread.start()
    
    # Server info
    log.info(f"\n{'='*60}")
    log.info(f"Modbus Server running at {SERVER_HOST}:{SERVER_PORT}")
    log.info(f"Slave ID: {SLAVE_ID}")
    log.info(f"{'='*60}")
    log.info("Register Block Sizes:")
    log.info(f"Discrete Inputs: {di_size}")
    log.info(f"Coils: {co_size}")
    log.info(f"Holding Registers: {hr_size}")
    log.info(f"Input Registers: {ir_size}")
    log.info(f"{'='*60}")
    log.info("Simulating ALL variables with random values:")
    for var in VARIABLES:
        log.info(f"{var['name']} ({'DI' if var['block']==2 else 'HR' if var['block']==3 else 'IR'})")
    log.info(f"{'='*60}\n")
    
    try:
        StartTcpServer(context, address=(SERVER_HOST, SERVER_PORT))
    except KeyboardInterrupt:
        log.info("Server stopped by user")
    except Exception as e:
        log.error(f"Server error: {str(e)}")

if __name__ == "__main__":
    run_server()
