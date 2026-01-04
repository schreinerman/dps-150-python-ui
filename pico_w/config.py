"""
Configuration file for DPS-150 Pico W
Edit these settings before uploading to your Pico W
"""

# WiFi Access Point Settings
AP_SSID = "DPS150-Control"           # WiFi network name
AP_PASSWORD = "dps150pico"           # Password (minimum 8 characters)
AP_CHANNEL = 6                        # WiFi channel (1-13)

# Web Server Settings
WEB_PORT = 80                         # HTTP port

# USB Host Settings for DPS150
# The DPS150 uses AT32 USB controller
# Default VID/PID for AT32 USB CDC devices
USB_VID = 0x2E3C                      # Vendor ID (AT32 default)
USB_PID = 0x5740                      # Product ID (CDC ACM)

# Debug Settings
DEBUG = True                          # Enable debug output
