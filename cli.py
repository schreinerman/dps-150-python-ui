#!/usr/bin/env python3
"""
Simple command-line tool for controlling the DPS-150
"""

import asyncio
import sys
from dps150 import DPS150, list_serial_ports, VOLTAGE_SET, CURRENT_SET


async def main():
    """Simple CLI for DPS-150"""
    
    print("=" * 50)
    print("FNIRSI DPS-150 CLI")
    print("=" * 50)
    
    # Show available ports
    ports = list_serial_ports()
    if not ports:
        print("❌ No serial ports found!")
        sys.exit(1)
    
    print("\nAvailable Ports:")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port['device']} - {port['description']}")
    
    # Select port
    port_idx = 0
    if len(ports) > 1:
        try:
            port_idx = int(input("\nSelect port (1-{}): ".format(len(ports)))) - 1
            if port_idx < 0 or port_idx >= len(ports):
                print("Invalid selection!")
                sys.exit(1)
        except ValueError:
            print("Invalid input!")
            sys.exit(1)
    
    selected_port = ports[port_idx]['device']
    print(f"\n✓ Using port: {selected_port}")
    
    # Initialize device
    device_data = {}
    
    def on_data(data):
        device_data.update(data)
        if 'outputVoltage' in data:
            print(f"\r📊 {data['outputVoltage']:.3f}V  {data['outputCurrent']:.3f}A  {data['outputPower']:.3f}W  ", end='')
    
    dps = DPS150(selected_port, callback=on_data)
    
    try:
        print("\n🔌 Connecting...")
        await dps.start()
        await asyncio.sleep(2)  # Wait for initial data
        
        print("\n✓ Connected!")
        print(f"Model: {device_data.get('modelName', 'N/A')}")
        print(f"Hardware: {device_data.get('hardwareVersion', 'N/A')}")
        print(f"Firmware: {device_data.get('firmwareVersion', 'N/A')}")
        
        # Interactive menu
        while True:
            print("\n" + "=" * 50)
            print("Commands:")
            print("  v <value>  - Set voltage (e.g. 'v 5.0')")
            print("  i <value>  - Set current (e.g. 'i 1.0')")
            print("  on         - Enable output")
            print("  off        - Disable output")
            print("  status     - Show status")
            print("  quit       - Exit")
            print("=" * 50)
            
            cmd = input("\n> ").strip().lower().split()
            
            if not cmd:
                continue
            
            if cmd[0] == 'quit' or cmd[0] == 'q':
                break
            
            elif cmd[0] == 'v' and len(cmd) == 2:
                try:
                    voltage = float(cmd[1])
                    await dps.set_float_value(VOLTAGE_SET, voltage)
                    print(f"✓ Voltage set to {voltage}V")
                except ValueError:
                    print("❌ Invalid value!")
            
            elif cmd[0] == 'i' and len(cmd) == 2:
                try:
                    current = float(cmd[1])
                    await dps.set_float_value(CURRENT_SET, current)
                    print(f"✓ Current set to {current}A")
                except ValueError:
                    print("❌ Invalid value!")
            
            elif cmd[0] == 'on':
                await dps.enable()
                print("✓ Output enabled")
            
            elif cmd[0] == 'off':
                await dps.disable()
                print("✓ Output disabled")
            
            elif cmd[0] == 'status':
                print("\n📊 Current Status:")
                print(f"  Input Voltage:     {device_data.get('inputVoltage', 0):.2f} V")
                print(f"  Output Voltage:    {device_data.get('outputVoltage', 0):.3f} V (Set: {device_data.get('setVoltage', 0):.2f} V)")
                print(f"  Output Current:    {device_data.get('outputCurrent', 0):.3f} A (Set: {device_data.get('setCurrent', 0):.2f} A)")
                print(f"  Output Power:      {device_data.get('outputPower', 0):.3f} W")
                print(f"  Temperature:       {device_data.get('temperature', 0):.1f} °C")
                print(f"  Mode:              {device_data.get('mode', 'N/A')}")
                print(f"  Output:            {'ON' if device_data.get('outputClosed') else 'OFF'}")
                print(f"  Protection:        {device_data.get('protectionState', 'None')}")
                print(f"  Capacity:          {device_data.get('outputCapacity', 0):.3f} Ah")
                print(f"  Energy:            {device_data.get('outputEnergy', 0):.3f} Wh")
            
            else:
                print("❌ Unknown command!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        print("\n🔌 Disconnecting...")
        await dps.stop()
        print("✓ Disconnected")


if __name__ == "__main__":
    asyncio.run(main())
