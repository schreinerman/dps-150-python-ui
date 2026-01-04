"""  
FNIRSI DPS-150 Control for Raspberry Pi Pico W
Main entry point - creates WiFi Access Point and starts web server
Uses TinyUSB in host mode for direct USB connection to DPS150
"""
import usb.core
import wifi
import socketpool
import time
import board
import json
from dps150_pico import DPS150
import gc
import traceback
from config import (
    AP_SSID, AP_PASSWORD, AP_CHANNEL, WEB_PORT,
    USB_VID, USB_PID, USB_MODE, PIO_USB_DP_PIN, PIO_USB_DM_PIN, DEBUG
)

# Global device instance
dps_device = None
latest_data = {}
usb_cdc = None
usb_port_available = None  # Stores USB port if found during startup
start_device_async = False

def setup_access_point():
    """Create WiFi Access Point for web interface access"""
    try:
        # Stop any existing connections
        wifi.radio.stop_station()
        
        # Start Access Point
        wifi.radio.start_ap(ssid=AP_SSID, password=AP_PASSWORD, channel=AP_CHANNEL)
        
        print("Access Point active")
        print(f"SSID: {AP_SSID}")
        print(f"Password: {AP_PASSWORD}")
        print(f"IP: {wifi.radio.ipv4_address_ap}")
        
        return wifi.radio
    except Exception as e:
        print(f"Failed to activate Access Point: {e}")
        return None

def on_device_data(data):
    """Callback for DPS150 data updates"""
    global latest_data
    latest_data.update(data)

def setup_usb_host():
    """Initialize USB host mode and find DPS150 device"""
    try:
        print("Waiting for DPS150...")
        device = usb.core.find(idVendor=USB_VID, idProduct=USB_PID)
        if device:
            print(f"Found USB device:")
            print(f"  VID:PID = {hex(device.idVendor)}:{hex(device.idProduct)}")
            if device.idVendor == USB_VID and device.idProduct == USB_PID:
                print("✓ DPS150 found!")
                return device
    except Exception as e:
        print(f"✗ ERROR: {e}")
        traceback.print_exception(e)
        return None

def find_dps150_port():
    """Find and return USB CDC interface to DPS150"""
    return setup_usb_host()

def handle_api_request(method, path, body):
    """Handle API requests"""
    global dps_device, latest_data
    
    # GET /api/ports
    if method == "GET" and path == "/api/ports":
        return json.dumps([{"port": "USB0", "description": "DPS150 USB", "selected": True}])
    
    # POST /api/connect
    elif method == "POST" and path == "/api/connect":
        try:
            global usb_port_available
            global start_device_async
            
            start_device_async = True
            
            return json.dumps({"status": "connected"})
        except Exception as e:
            if DEBUG:
                print(f"Connect error: {e}")
            import traceback
            traceback.print_exception(e)
            return json.dumps({"error": f"Connection failed: {str(e)}"})
    
    # POST /api/disconnect
    elif method == "POST" and path == "/api/disconnect":
        if dps_device:
            dps_device.stop()
            dps_device = None
        return json.dumps({"status": "disconnected"})
    
    # POST /api/set/voltage
    elif method == "POST" and path == "/api/set/voltage":
        print("BODY RAW:", body)
        if not dps_device:
            return json.dumps({"error": "Not connected"})
        try:
            data = json.loads(body) if body else {}
            voltage = float(data.get("value", 0))
            dps_device.set_voltage(voltage)
            return json.dumps({"status": "ok", "voltage": str(voltage)})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    # POST /api/set/current
    elif method == "POST" and path == "/api/set/current":
        if not dps_device:
            return json.dumps({"error": "Not connected"})
        try:
            data = json.loads(body) if body else {}
            current = float(data.get("value", 0))
            dps_device.set_current(current)
            return json.dumps({"status": "ok", "current": str(current)})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    # POST /api/output/enable
    elif method == "POST" and path == "/api/output/enable":
        if not dps_device:
            return json.dumps({"error": "Not connected"})
        dps_device.enable()
        return json.dumps({"status": "enabled"})
    
    # POST /api/output/disable
    elif method == "POST" and path == "/api/output/disable":
        if not dps_device:
            return json.dumps({"error": "Not connected"})
        dps_device.disable()
        return json.dumps({"status": "disabled"})
    
    # GET /api/data - Polling endpoint for device data
    elif method == "GET" and path == "/api/data":
        return json.dumps(latest_data)
    
    return json.dumps({"error": "Unknown endpoint"})

def parse_http_request(request):
    try:
        if isinstance(request, bytes):
            text = request.decode("utf-8", "ignore")
        else:
            text = request  # schon ein String

        # (Chrome, Firefox)
        if "\r\n\r\n" in text:
            header, body = text.split("\r\n\r\n", 1)
        # Safari / iOS
        elif "\n\n" in text:
            header, body = text.split("\n\n", 1)
        # Safari: body starts direct after \r\n
        elif "\r\n{" in text:
            header, body = text.split("\r\n{", 1)
            body = "{" + body
        else:
            return None, None, None

        # Request line parsen
        first_line = header.splitlines()[0]
        parts = first_line.split(" ")
        if len(parts) < 2:
            return None, None, None

        method = parts[0]
        path = parts[1].split("?")[0]

        return method, path, body.strip()
    except Exception as e:
        print("Parse error:", e)
        return None, None, None
    
    
def send_response_raw(client, status, content_type, body):
    if isinstance(body, str):
        body = body.encode("utf-8")

    header = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode("utf-8")

    client.send(header)
    client.send(body)
    
def send_response(client, status, content_type, body):
    """Send HTTP response"""
    # Convert body to bytes and ensure newline
    if isinstance(body, str):
        body = body.encode('utf-8')

    # Build response with correct Content-Length
    response = f"HTTP/1.1 {status}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += "Access-Control-Allow-Origin: *\r\n"
    response += "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
    response += "Access-Control-Allow-Headers: *\r\n"
    response += f"Content-Length: {len(body)}\r\n"
    response += "Connection: close\r\n\r\n"
    
    # Send header
    client.send(response.encode('utf-8'))
    
    # Send body in chunks to avoid buffer overflow
    chunk_size = 512
    
    # Small JSON-responses → one send(), np chunking
    if len(body) < chunk_size:
        client.send(body)
        return
    
    for i in range(0, len(body), chunk_size):
        chunk = body[i:i + chunk_size]
        client.send(chunk)
        time.sleep(0.001)  # Small delay between chunks

def load_file(filename):
    """Load file from filesystem"""
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return None

def recv_full_request(client):
    buffer = bytearray(4096)
    n = client.recv_into(buffer)
    if n <= 0:
        return None, None

    text = buffer[:n].decode("utf-8", "ignore")

    # Split Header/Body
    if "\r\n\r\n" in text:
        header, body = text.split("\r\n\r\n", 1)
    elif "\n\n" in text:
        header, body = text.split("\n\n", 1)
    else:
        # no Body, only Header
        return text, ""

    # search Content-Length
    content_length = 0
    for line in header.splitlines():
        if line.lower().startswith("content-length:"):
            try:
                content_length = int(line.split(":")[1].strip())
            except:
                content_length = 0

    # If no Body or Size is correct
    if len(body) >= content_length:
        return header, body

    remaining = content_length - len(body)
    while remaining > 0:
        chunk = bytearray(1024)
        n = client.recv_into(chunk)
        if n <= 0:
            break
        body += chunk[:n].decode("utf-8", "ignore")
        remaining -= n

    return header, body


def run_web_server(ap):
    global start_device_async, usb_port_available, dps_device
    """Run minimal web server"""
    pool = socketpool.SocketPool(wifi.radio)
    s = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
    s.setsockopt(pool.SOL_SOCKET, pool.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', WEB_PORT))
    s.listen(5)
    s.setblocking(False)  # Non-blocking socket
    
    print(f"Web server listening on http://{wifi.radio.ipv4_address_ap}:{WEB_PORT}")
    print("Ready to accept connections")
    
    while True:
        try:
            gc.collect()  # Clean up memory
            
            if start_device_async:
                start_device_async = False
                # Try to find USB port if not already available
                if not usb_port_available:
                    print("Searching for USB device...")
                    usb_port_available = find_dps150_port()
                
                if not usb_port_available:
                    print("No USB device found. Please connect DPS150 and refresh.")
                else:
                    print("Creating DPS150 instance...")
                    dps_device = DPS150(usb_port_available, callback=on_device_data)
                    dps_device.start()
                    print("DPS150 connected successfully")
                

            # Poll DPS150 device for new data
            if dps_device:
                dps_device.update()
            
            # Try to accept connection (non-blocking)
            try:
                client, addr = s.accept()
            except OSError:
                # No connection waiting, continue polling
                time.sleep(0.01)
                continue
                
            client.settimeout(30)  # Longer timeout for CircuitPython
            
            try:
                # CircuitPython uses recv_into() instead of recv()
                header, body = recv_full_request(client)
                if header is None:
                    client.close()
                    continue

                method, path, parsed_body = parse_http_request(header + "\r\n\r\n" + body)
                
                if method is None:
                    client.close()
                    continue
                
                if DEBUG:
                    print(f"{method} {path}")
                
                # Handle OPTIONS for CORS preflight (Safari)
                if method == "OPTIONS":
                    print("SAFARI PRELIGHT RECEIVED")
                    response = (
                        "HTTP/1.1 204 No Content\r\n"
                        "Access-Control-Allow-Origin: *\r\n"
                        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
                        "Access-Control-Allow-Headers: Content-Type\r\n"   # << NICHT '*'
                        "Access-Length: 0\r\n"
                        "Connection: keep-alive\r\n\r\n"
                    )
                    client.send(response.encode("utf-8"))
                    client.close()
                    continue
                
                # Handle root
                elif path == "/" or path == "/index.html":
                    content = load_file("index.html")
                    if content:
                        send_response(client, "200 OK", "text/html", content)
                    else:
                        send_response(client, "404 Not Found", "text/plain", "File not found")
                
                # Handle static files
                elif path.startswith("/static/"):
                    filename = path[1:]  # Remove leading /
                    content = load_file(filename)
                    
                    if content:
                        # Determine content type
                        if filename.endswith('.js'):
                            ct = "application/javascript"
                        elif filename.endswith('.css'):
                            ct = "text/css"
                        elif filename.endswith('.html'):
                            ct = "text/html"
                        else:
                            ct = "application/octet-stream"
                        
                        send_response_raw(client, "200 OK", ct, content)
                    else:
                        send_response(client, "404 Not Found", "text/plain", "File not found")
                
                # Handle API
                elif path.startswith("/api/"):
                    response = handle_api_request(method, path, body)
                    send_response(client, "200 OK", "application/json", response)
                
                else:
                    send_response(client, "404 Not Found", "text/plain", "Not found")
                
            except Exception as e:
                print(f"Error handling request: {e}")
            finally:
                time.sleep(0.05)  # Safari needs a small grace period
                client.close()
                
        except OSError as e:
            if e.args[0] == 11:  # EAGAIN
                time.sleep(0.1)
            else:
                print(f"Socket error: {e}")
                time.sleep(1)
        except Exception as e:
            print(f"Server error: {e}")
            time.sleep(1)

def main():
    """Main entry point"""
    global usb_port_available
    global start_device_async
    
    start_device_async = False
    print("=" * 50)
    print("FNIRSI DPS-150 Control for Raspberry Pi Pico W")
    print("TinyUSB Host Mode - Direct USB Connection")
    print("=" * 50)
    
    # Setup Access Point
    ap = setup_access_point()
    if not ap:
        print("Failed to start - no Access Point")
        return
    
    # Try to find USB device at startup (non-blocking)
    print("\nLooking for DPS150 USB device...")
    usb_port_available = find_dps150_port()
    if usb_port_available:
        print("✓ USB device found and ready")
    else:
        print("✗ No USB device found")
        print("You can connect it later and click 'Connect' in the web UI")
    
    # Start web server
    try:
        run_web_server(ap)
    except KeyboardInterrupt:
        print("\nShutting down...")
        if dps_device:
            dps_device.stop()

if __name__ == "__main__":
    main()
