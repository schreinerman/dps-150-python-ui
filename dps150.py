"""
FNIRSI DPS-150 Power Supply Control via Serial Interface
Python implementation of the DPS-150 protocol
"""

import asyncio
import struct
from typing import Callable, Optional, Dict, Any
import serial
import serial.tools.list_ports

# Constants
HEADER_INPUT = 0xf0  # 240
HEADER_OUTPUT = 0xf1  # 241

CMD_GET = 0xa1  # 161
CMD_XXX_176 = 0xb0  # 176
CMD_SET = 0xb1  # 177
CMD_XXX_192 = 0xc0  # 192
CMD_XXX_193 = 0xc1  # 193

# Float values
VOLTAGE_SET = 193
CURRENT_SET = 194

GROUP1_VOLTAGE_SET = 197
GROUP1_CURRENT_SET = 198
GROUP2_VOLTAGE_SET = 199
GROUP2_CURRENT_SET = 200
GROUP3_VOLTAGE_SET = 201
GROUP3_CURRENT_SET = 202
GROUP4_VOLTAGE_SET = 203
GROUP4_CURRENT_SET = 204
GROUP5_VOLTAGE_SET = 205
GROUP5_CURRENT_SET = 206
GROUP6_VOLTAGE_SET = 207
GROUP6_CURRENT_SET = 208

OVP = 209
OCP = 210
OPP = 211
OTP = 212
LVP = 213

METERING_ENABLE = 216
OUTPUT_ENABLE = 219

# Byte values
BRIGHTNESS = 214
VOLUME = 215

MODEL_NAME = 222
HARDWARE_VERSION = 223
FIRMWARE_VERSION = 224
ALL = 255

PROTECTION_STATES = [
    "",
    "OVP",
    "OCP",
    "OPP",
    "OTP",
    "LVP",
    "REP",
]


class DPS150:
    """Class for controlling the FNIRSI DPS-150 power supply"""
    
    def __init__(self, port: str, callback: Optional[Callable] = None):
        self.port_name = port
        self.serial_port: Optional[serial.Serial] = None
        self.callback = callback
        self.reader_task: Optional[asyncio.Task] = None
        self.running = False
        self._write_lock = asyncio.Lock()  # Lock for serial write operations
        
    async def start(self):
        """Opens the serial connection and starts the reader"""
        print(f'Starting DPS-150 on {self.port_name}')
        
        # Open serial connection
        self.serial_port = serial.Serial(
            port=self.port_name,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            rtscts=True  # Hardware Flow Control
        )
        
        self.running = True
        self.reader_task = asyncio.create_task(self._read_loop())
        await self._init_command()
        
    async def stop(self):
        """Stops the connection"""
        print('Stopping DPS-150')
        await self.send_command(HEADER_OUTPUT, CMD_XXX_193, 0, [0])
        self.running = False
        
        if self.reader_task:
            await self.reader_task
            
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            
    async def _read_loop(self):
        """Continuously reads data from the serial port"""
        print('Starting reader...')
        buffer = bytearray()
        
        while self.running and self.serial_port and self.serial_port.is_open:
            try:
                # Non-blocking read with asyncio
                await asyncio.sleep(0.01)  # Prevents CPU load
                
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    buffer.extend(data)
                    
                    # Search for packets in buffer
                    i = 0
                    while i < len(buffer) - 6:
                        if buffer[i] == 0xf0 and buffer[i+1] == 0xa1:
                            c1 = buffer[i]
                            c2 = buffer[i+1]
                            c3 = buffer[i+2]
                            c4 = buffer[i+3]
                            
                            # Check if complete packet is available
                            if i + 4 + c4 >= len(buffer):
                                break
                                
                            c5 = buffer[i+4:i+4+c4]
                            c6 = buffer[i+4+c4]
                            
                            # Calculate checksum
                            s6 = (c3 + c4 + sum(c5)) % 0x100
                            
                            # Shorten buffer
                            buffer = buffer[i+4+c4+1:]
                            i = 0
                            
                            if s6 != c6:
                                # print(f'Checksum error: {s6} != {c6}')
                                continue
                                
                            # Parse data
                            self._parse_data(c1, c2, c3, c4, c5, c6)
                        else:
                            i += 1
                            
            except Exception as e:
                print(f'Error reading: {e}')
                
    async def _init_command(self):
        """Initializes the connection"""
        await self.send_command(HEADER_OUTPUT, CMD_XXX_193, 0, [1])
        # Baudrate index: 115200 is index 4 in [9600, 19200, 38400, 57600, 115200]
        await self.send_command(HEADER_OUTPUT, CMD_XXX_176, 0, [5])
        
        await self.send_command(HEADER_OUTPUT, CMD_GET, MODEL_NAME, [0])
        await self.send_command(HEADER_OUTPUT, CMD_GET, HARDWARE_VERSION, [0])
        await self.send_command(HEADER_OUTPUT, CMD_GET, FIRMWARE_VERSION, [0])
        await self.get_all()
        
    async def send_command(self, c1: int, c2: int, c3: int, c5: list):
        """Sends a command to the device"""
        if isinstance(c5, int):
            c5 = [c5]
            
        c4 = len(c5)
        c6 = (c3 + c4 + sum(c5)) % 0x100
        
        command = bytearray([c1, c2, c3, c4] + c5 + [c6])
        await self._send_command_raw(command)
        
    async def send_command_float(self, c1: int, c2: int, c3: int, value: float):
        """Sends a float value"""
        c5 = list(struct.pack('<f', value))  # Little-endian float
        await self.send_command(c1, c2, c3, c5)
        
    async def _send_command_raw(self, command: bytearray):
        """Sends raw command (thread-safe with lock)"""
        async with self._write_lock:
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.write(command)
                await asyncio.sleep(0.05)  # Wait 50ms
            
    def _parse_data(self, c1: int, c2: int, c3: int, c4: int, c5: bytes, c6: int):
        """Parses received data"""
        if not self.callback:
            return
            
        data = {}
        
        try:
            if c3 == 192:  # Input Voltage
                data['inputVoltage'] = struct.unpack('<f', c5[0:4])[0]
            elif c3 == 195:  # Output Voltage, Current, Power
                data['outputVoltage'] = struct.unpack('<f', c5[0:4])[0]
                data['outputCurrent'] = struct.unpack('<f', c5[4:8])[0]
                data['outputPower'] = struct.unpack('<f', c5[8:12])[0]
            elif c3 == 196:  # Temperature
                data['temperature'] = struct.unpack('<f', c5[0:4])[0]
            elif c3 == 217:  # Output Capacity
                data['outputCapacity'] = struct.unpack('<f', c5[0:4])[0]
            elif c3 == 218:  # Output Energy
                data['outputEnergy'] = struct.unpack('<f', c5[0:4])[0]
            elif c3 == 219:  # Output Closed
                data['outputClosed'] = c5[0] == 1
            elif c3 == 220:  # Protection State
                data['protectionState'] = PROTECTION_STATES[c5[0]]
            elif c3 == 221:  # CC/CV Mode
                data['mode'] = "CC" if c5[0] == 0 else "CV"
            elif c3 == 222:  # Model Name
                data['modelName'] = c5.decode('ascii', errors='ignore')
            elif c3 == 223:  # Hardware Version
                data['hardwareVersion'] = c5.decode('ascii', errors='ignore')
            elif c3 == 224:  # Firmware Version
                data['firmwareVersion'] = c5.decode('ascii', errors='ignore')
            elif c3 == 226:  # Upper Limit Voltage
                data['upperLimitVoltage'] = struct.unpack('<f', c5[0:4])[0]
            elif c3 == 227:  # Upper Limit Current
                data['upperLimitCurrent'] = struct.unpack('<f', c5[0:4])[0]
            elif c3 == 255:  # All Data
                data.update({
                    'inputVoltage': struct.unpack('<f', c5[0:4])[0],
                    'setVoltage': struct.unpack('<f', c5[4:8])[0],
                    'setCurrent': struct.unpack('<f', c5[8:12])[0],
                    'outputVoltage': struct.unpack('<f', c5[12:16])[0],
                    'outputCurrent': struct.unpack('<f', c5[16:20])[0],
                    'outputPower': struct.unpack('<f', c5[20:24])[0],
                    'temperature': struct.unpack('<f', c5[24:28])[0],
                    
                    'group1setVoltage': struct.unpack('<f', c5[28:32])[0],
                    'group1setCurrent': struct.unpack('<f', c5[32:36])[0],
                    'group2setVoltage': struct.unpack('<f', c5[36:40])[0],
                    'group2setCurrent': struct.unpack('<f', c5[40:44])[0],
                    'group3setVoltage': struct.unpack('<f', c5[44:48])[0],
                    'group3setCurrent': struct.unpack('<f', c5[48:52])[0],
                    'group4setVoltage': struct.unpack('<f', c5[52:56])[0],
                    'group4setCurrent': struct.unpack('<f', c5[56:60])[0],
                    'group5setVoltage': struct.unpack('<f', c5[60:64])[0],
                    'group5setCurrent': struct.unpack('<f', c5[64:68])[0],
                    'group6setVoltage': struct.unpack('<f', c5[68:72])[0],
                    'group6setCurrent': struct.unpack('<f', c5[72:76])[0],
                    
                    'overVoltageProtection': struct.unpack('<f', c5[76:80])[0],
                    'overCurrentProtection': struct.unpack('<f', c5[80:84])[0],
                    'overPowerProtection': struct.unpack('<f', c5[84:88])[0],
                    'overTemperatureProtection': struct.unpack('<f', c5[88:92])[0],
                    'lowVoltageProtection': struct.unpack('<f', c5[92:96])[0],
                    
                    'brightness': c5[96],
                    'volume': c5[97],
                    'meteringClosed': c5[98] == 0,
                    
                    'outputCapacity': struct.unpack('<f', c5[99:103])[0],
                    'outputEnergy': struct.unpack('<f', c5[103:107])[0],
                    
                    'outputClosed': c5[107] == 1,
                    'protectionState': PROTECTION_STATES[c5[108]],
                    'mode': "CC" if c5[109] == 0 else "CV",
                    
                    'upperLimitVoltage': struct.unpack('<f', c5[111:115])[0],
                    'upperLimitCurrent': struct.unpack('<f', c5[115:119])[0],
                })
                
            if data:
                self.callback(data)
                
        except Exception as e:
            print(f'Error parsing: {e}')
            
    async def get_all(self):
        """Requests all data"""
        await self.send_command(HEADER_OUTPUT, CMD_GET, ALL, [0])
        
    async def set_float_value(self, type_: int, value: float):
        """Sets a float value"""
        await self.send_command_float(HEADER_OUTPUT, CMD_SET, type_, value)
        
    async def set_byte_value(self, type_: int, value: int):
        """Sets a byte value"""
        await self.send_command(HEADER_OUTPUT, CMD_SET, type_, [value])
        
    async def enable(self):
        """Enables the output"""
        await self.set_byte_value(OUTPUT_ENABLE, 1)
        
    async def disable(self):
        """Disables the output"""
        await self.set_byte_value(OUTPUT_ENABLE, 0)
        
    async def start_metering(self):
        """Starts metering"""
        await self.set_byte_value(METERING_ENABLE, 1)
        
    async def stop_metering(self):
        """Stops metering"""
        await self.set_byte_value(METERING_ENABLE, 0)


def list_serial_ports():
    """Lists available serial ports"""
    ports = serial.tools.list_ports.comports()
    result = []
    for port in ports:
        desc = port.description if port.description and port.description != 'n/a' else ''
        title = f"{port.device}" + (f" - {desc}" if desc else "")
        result.append({
            'device': port.device,
            'title': title,
            'description': desc
        })
    return result


# Usage example
async def main():
    """Example usage of the DPS150 class"""
    
    def on_data(data):
        print(f"Received data: {data}")
    
    # Show available ports
    ports = list_serial_ports()
    print("Available ports:", ports)
    
    if not ports:
        print("No serial ports found!")
        return
    
    # Use first port
    dps = DPS150(ports[0]['device'], callback=on_data)
    
    try:
        await dps.start()
        print("Connected!")
        
        # Command examples
        await asyncio.sleep(2)
        await dps.set_float_value(VOLTAGE_SET, 5.0)  # Set 5V
        await asyncio.sleep(1)
        await dps.set_float_value(CURRENT_SET, 1.0)  # Set 1A
        await asyncio.sleep(1)
        await dps.enable()  # Enable output
        
        # Keep running
        await asyncio.sleep(10)
        
    finally:
        await dps.stop()


if __name__ == "__main__":
    asyncio.run(main())
