"""
FNIRSI DPS-150 Protocol Implementation for CircuitPython
Adapted for Raspberry Pi Pico W with TinyUSB host mode
Supports direct USB CDC connection to DPS150
"""

import struct
import time
import usb.core

# Protocol Constants
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
    """Control class for FNIRSI DPS-150 power supply via USB CDC"""
    
    def __init__(self, usb_device: usb.core.Device, callback=None):
        """
        Initialize DPS150 controller
        
        Args:
            usb_port: USB CDC interface (usb_cdc.data or similar)
            callback: Optional callback function for received data
        """
        self.usb_device = usb_device
        self.callback = callback
        self.running = False
        self.buffer = bytearray()
        
    def start(self):
        """Start USB CDC communication with DPS150"""
        print(f'Starting DPS-150 via USB CDC')
        self.running = True
        
        # Initialize device
        self.usb_device.set_configuration(1)
        self._flushDevice()
        time.sleep(0.1)
        print(f'Init Command...')
        self._init_command()
        
    def stop(self):
        """Stop USB CDC communication"""
        print('Stopping DPS-150')
        self.send_command(HEADER_OUTPUT, CMD_XXX_193, 0, [0])
        self.running = False
    
    def update(self):
        data = bytearray(512)
        """Poll for new data - call this regularly from main loop"""
        if not self.running:
            return
            
        try:
            available = self.usb_device.read(0x81, data,100)
            data = data[:available]
            if available and available > 0:
                if data:
                    self.buffer.extend(data)
                    self._process_buffer()
                    
        except Exception as e:
            pass  # Silently ignore errors in polling mode
        
    def _flushDevice(self):
        read_data = bytearray(512)
        try:
            self.usb_device.write(
                1,
                bytearray([0]),
                100
            )
        except:
            pass
        try:
            self.usb_device.read(0x81, read_data,100)
        except:
            pass
    
    def _read_loop(self):
        """Deprecated - no longer used in CircuitPython (no threading)"""
                
    def _process_buffer(self):
        """Process received data buffer and extract complete packets"""
        i = 0
        while i < len(self.buffer) - 6:
            if self.buffer[i] == 0xf0 and self.buffer[i+1] == 0xa1:
                c1 = self.buffer[i]
                c2 = self.buffer[i+1]
                c3 = self.buffer[i+2]
                c4 = self.buffer[i+3]
                
                # Check if complete packet is available
                if i + 4 + c4 >= len(self.buffer):
                    break
                
                c5 = self.buffer[i+4:i+4+c4]
                c6 = self.buffer[i+4+c4]
                
                # Calculate checksum
                s6 = (c3 + c4 + sum(c5)) % 0x100
                
                # Remove processed data from buffer
                self.buffer = self.buffer[i+4+c4+1:]
                i = 0
                
                if s6 != c6:
                    continue
                
                # Parse data
                self._parse_data(c1, c2, c3, c4, c5, c6)
            else:
                i += 1
                
    def _init_command(self):
        """Initialize connection and request device info"""
        self.send_command(HEADER_OUTPUT, CMD_XXX_193, 0, [1])
        time.sleep(0.05)
        # Baudrate index: 115200 is index 4 (for serial compatibility)
        self.send_command(HEADER_OUTPUT, CMD_XXX_176, 0, [5])
        time.sleep(0.05)
        
        self.send_command(HEADER_OUTPUT, CMD_GET, MODEL_NAME, [0])
        time.sleep(0.05)
        self.send_command(HEADER_OUTPUT, CMD_GET, HARDWARE_VERSION, [0])
        time.sleep(0.05)
        self.send_command(HEADER_OUTPUT, CMD_GET, FIRMWARE_VERSION, [0])
        time.sleep(0.05)
        self.get_all()
        
    def send_command(self, c1, c2, c3, c5):
        """Send command packet to device"""
        if isinstance(c5, int):
            c5 = [c5]
        
        c4 = len(c5)
        c6 = (c3 + c4 + sum(c5)) % 0x100
        
        command = bytearray([c1, c2, c3, c4] + c5 + [c6])
        self._send_command_raw(command)
        
    def send_command_float(self, c1, c2, c3, value):
        """Send command with float value (little-endian)"""
        c5 = list(struct.pack('<f', value))  # Little-endian float
        self.send_command(c1, c2, c3, c5)
        
    def _send_command_raw(self, command):
        """Send raw command bytes via USB CDC"""
        tries = 10
        while tries > 0:
            try:
                self.usb_device.write(1,command, 100)
                tries = 0
            except:
                tries = tries - 1
                time.sleep(0.1)
        time.sleep(0.05)
        self.update()
            
    def _parse_data(self, c1, c2, c3, c4, c5, c6):
        """Parse received data"""
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
            
    def get_all(self):
        """Request all data"""
        self.send_command(HEADER_OUTPUT, CMD_GET, ALL, [0])
        
    def set_voltage(self, value):
        """Set output voltage"""
        self.send_command_float(HEADER_OUTPUT, CMD_SET, VOLTAGE_SET, value)
        
    def set_current(self, value):
        """Set output current"""
        self.send_command_float(HEADER_OUTPUT, CMD_SET, CURRENT_SET, value)
        
    def set_float_value(self, type_, value):
        """Set a float value"""
        self.send_command_float(HEADER_OUTPUT, CMD_SET, type_, value)
        
    def set_byte_value(self, type_, value):
        """Set a byte value"""
        self.send_command(HEADER_OUTPUT, CMD_SET, type_, [value])
        
    def enable(self):
        """Enable output"""
        self.set_byte_value(OUTPUT_ENABLE, 1)
        
    def disable(self):
        """Disable output"""
        self.set_byte_value(OUTPUT_ENABLE, 0)
        
    def start_metering(self):
        """Start metering"""
        self.set_byte_value(METERING_ENABLE, 1)
        
    def stop_metering(self):
        """Stop metering"""
        self.set_byte_value(METERING_ENABLE, 0)
