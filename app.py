"""
Flask web server for FNIRSI DPS-150 control
Provides REST API and WebSocket communication
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import asyncio
from threading import Thread
import json
from dps150 import (
    DPS150, list_serial_ports,
    VOLTAGE_SET, CURRENT_SET, BRIGHTNESS, VOLUME,
    OVP, OCP, OPP, OTP, LVP,
    GROUP1_VOLTAGE_SET, GROUP1_CURRENT_SET,
    GROUP2_VOLTAGE_SET, GROUP2_CURRENT_SET,
    GROUP3_VOLTAGE_SET, GROUP3_CURRENT_SET,
    GROUP4_VOLTAGE_SET, GROUP4_CURRENT_SET,
    GROUP5_VOLTAGE_SET, GROUP5_CURRENT_SET,
    GROUP6_VOLTAGE_SET, GROUP6_CURRENT_SET,
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dps150-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
dps_device = None
event_loop = None
loop_thread = None


def run_event_loop(loop):
    """Runs in a separate thread for asyncio"""
    asyncio.set_event_loop(loop)
    loop.run_forever()


def get_event_loop():
    """Returns the event loop or creates a new one"""
    global event_loop, loop_thread
    
    if event_loop is None:
        event_loop = asyncio.new_event_loop()
        loop_thread = Thread(target=run_event_loop, args=(event_loop,), daemon=True)
        loop_thread.start()
    
    return event_loop


def on_device_data(data):
    """Callback for device data - sends via WebSocket"""
    socketio.emit('device_data', data)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/ports')
def get_ports():
    """Lists available serial ports"""
    ports = list_serial_ports()
    print(f"DEBUG: Found ports: {ports}")
    
    # Mark the AT32 port as pre-selected
    for port in ports:
        port['selected'] = 'AT32' in port['description'].upper()
    
    return jsonify(ports)


@app.route('/api/connect', methods=['POST'])
def connect():
    """Connects to the device"""
    global dps_device
    
    data = request.json
    port = data.get('port')
    
    if not port:
        return jsonify({'error': 'Port required'}), 400
    
    try:
        loop = get_event_loop()
        dps_device = DPS150(port, callback=on_device_data)
        
        # Start in asyncio loop
        future = asyncio.run_coroutine_threadsafe(dps_device.start(), loop)
        future.result(timeout=5)  # Wait max 5 seconds
        
        return jsonify({'status': 'connected'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """Disconnects the connection"""
    global dps_device
    
    if dps_device:
        try:
            loop = get_event_loop()
            future = asyncio.run_coroutine_threadsafe(dps_device.stop(), loop)
            future.result(timeout=5)
            dps_device = None
            return jsonify({'status': 'disconnected'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'status': 'not connected'}), 400


@app.route('/api/set/voltage', methods=['POST'])
def set_voltage():
    """Sets the output voltage"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    data = request.json
    voltage = float(data.get('value', 0))
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(
            dps_device.set_float_value(VOLTAGE_SET, voltage), loop
        )
        future.result(timeout=2)
        return jsonify({'status': 'ok', 'voltage': voltage})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/set/current', methods=['POST'])
def set_current():
    """Sets the output current"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    data = request.json
    current = float(data.get('value', 0))
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(
            dps_device.set_float_value(CURRENT_SET, current), loop
        )
        future.result(timeout=2)
        return jsonify({'status': 'ok', 'current': current})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/output/enable', methods=['POST'])
def enable_output():
    """Enables the output"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(dps_device.enable(), loop)
        future.result(timeout=2)
        return jsonify({'status': 'enabled'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/output/disable', methods=['POST'])
def disable_output():
    """Disables the output"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(dps_device.disable(), loop)
        future.result(timeout=2)
        return jsonify({'status': 'disabled'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metering/start', methods=['POST'])
def start_metering():
    """Starts metering"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(dps_device.start_metering(), loop)
        future.result(timeout=2)
        return jsonify({'status': 'metering started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metering/stop', methods=['POST'])
def stop_metering():
    """Stops metering"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(dps_device.stop_metering(), loop)
        future.result(timeout=2)
        return jsonify({'status': 'metering stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get/all', methods=['POST'])
def get_all():
    """Requests all data"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(dps_device.get_all(), loop)
        future.result(timeout=2)
        return jsonify({'status': 'requested'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/set/brightness', methods=['POST'])
def set_brightness():
    """Sets the display brightness"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    data = request.json
    brightness = int(data.get('value', 0))
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(
            dps_device.set_byte_value(BRIGHTNESS, brightness), loop
        )
        future.result(timeout=2)
        return jsonify({'status': 'ok', 'brightness': brightness})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/set/volume', methods=['POST'])
def set_volume():
    """Sets the volume"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    data = request.json
    volume = int(data.get('value', 0))
    
    try:
        loop = get_event_loop()
        future = asyncio.run_coroutine_threadsafe(
            dps_device.set_byte_value(VOLUME, volume), loop
        )
        future.result(timeout=2)
        return jsonify({'status': 'ok', 'volume': volume})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/set/group/<int:group>', methods=['POST'])
def set_group(group):
    """Sets voltage/current for a group"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    if group < 1 or group > 6:
        return jsonify({'error': 'Group must be between 1 and 6'}), 400
    
    data = request.json
    voltage = data.get('voltage')
    current = data.get('current')
    
    group_map = {
        1: (GROUP1_VOLTAGE_SET, GROUP1_CURRENT_SET),
        2: (GROUP2_VOLTAGE_SET, GROUP2_CURRENT_SET),
        3: (GROUP3_VOLTAGE_SET, GROUP3_CURRENT_SET),
        4: (GROUP4_VOLTAGE_SET, GROUP4_CURRENT_SET),
        5: (GROUP5_VOLTAGE_SET, GROUP5_CURRENT_SET),
        6: (GROUP6_VOLTAGE_SET, GROUP6_CURRENT_SET),
    }
    
    try:
        loop = get_event_loop()
        
        if voltage is not None:
            future = asyncio.run_coroutine_threadsafe(
                dps_device.set_float_value(group_map[group][0], float(voltage)), loop
            )
            future.result(timeout=2)
        
        if current is not None:
            future = asyncio.run_coroutine_threadsafe(
                dps_device.set_float_value(group_map[group][1], float(current)), loop
            )
            future.result(timeout=2)
        
        return jsonify({'status': 'ok', 'group': group})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/set/protection', methods=['POST'])
def set_protection():
    """Sets protection parameters"""
    if not dps_device:
        return jsonify({'error': 'Not connected'}), 400
    
    data = request.json
    ovp = data.get('ovp')  # Over Voltage Protection
    ocp = data.get('ocp')  # Over Current Protection
    opp = data.get('opp')  # Over Power Protection
    otp = data.get('otp')  # Over Temperature Protection
    lvp = data.get('lvp')  # Low Voltage Protection
    
    try:
        loop = get_event_loop()
        
        if ovp is not None:
            future = asyncio.run_coroutine_threadsafe(
                dps_device.set_float_value(OVP, float(ovp)), loop
            )
            future.result(timeout=2)
        
        if ocp is not None:
            future = asyncio.run_coroutine_threadsafe(
                dps_device.set_float_value(OCP, float(ocp)), loop
            )
            future.result(timeout=2)
        
        if opp is not None:
            future = asyncio.run_coroutine_threadsafe(
                dps_device.set_float_value(OPP, float(opp)), loop
            )
            future.result(timeout=2)
        
        if otp is not None:
            future = asyncio.run_coroutine_threadsafe(
                dps_device.set_float_value(OTP, float(otp)), loop
            )
            future.result(timeout=2)
        
        if lvp is not None:
            future = asyncio.run_coroutine_threadsafe(
                dps_device.set_float_value(LVP, float(lvp)), loop
            )
            future.result(timeout=2)
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """WebSocket connection established"""
    print('Client connected')
    emit('connected', {'status': 'ok'})


@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket connection closed"""
    print('Client disconnected')


if __name__ == '__main__':
    import os
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    
    print("Starting FNIRSI DPS-150 web server...")
    print(f"Open http://localhost:{port} in your browser")
    print(f"Server running on {host}:{port}")
    print("Press Ctrl+C to exit")
    print("=" * 50)
    
    # Verwende threading mode (Python 3.13 kompatibel)
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)
