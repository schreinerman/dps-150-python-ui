# 📁 Project Structure

```
dps-150-python-ui-rpi-pico-w/
│
├── 🖥️ PC Version (Desktop & Web)
│   ├── app.py                    # Flask Web Server
│   ├── gui_app.py               # PyQt6 Desktop App
│   ├── cli.py                   # Command Line Interface
│   ├── dps150.py                # DPS-150 Protocol (asyncio)
│   ├── translations.py          # Multi-language support
│   │
│   ├── requirements.txt         # Web dependencies
│   ├── requirements-gui.txt     # Desktop dependencies
│   ├── requirements-build.txt   # Build dependencies
│   │
│   ├── build.sh / build.bat     # Build scripts
│   ├── build.py                 # Build automation
│   │
│   ├── templates/
│   │   └── index.html          # Web UI template
│   │
│   └── static/
│       ├── translations.js      # Frontend translations
│       └── libs/               # External libraries
│           ├── vue.global.min.js
│           ├── vuetify.min.js
│           ├── plotly.min.js
│           └── socket.io.min.js
│
└── 🔌 Raspberry Pi Pico W Version (NEW!)
    └── pico_w/
        ├── 📄 Core Files (upload to Pico W)
        │   ├── main.py              # Entry point & Web Server
        │   ├── dps150_pico.py       # DPS-150 Protocol (CircuitPython)
        │   ├── config.py            # Configuration
        │   └── index.html           # Standalone Web UI
        │
        ├── 📖 Documentation
        │   ├── README.md            # Complete installation guide
        │   ├── QUICKSTART.md        # 5-minute quick start
        │   ├── WIRING.txt           # Hardware connection diagrams
        │   └── IMPLEMENTATION_NOTES.md # Technical summary
        │
        ├── 🛠️ Upload Tools
        │   ├── upload.py            # Python upload (cross-platform)
        │   ├── upload.sh            # Shell script (Linux/Mac)
        │   ├── upload.bat           # Batch script (Windows)
        │   └── requirements-pico.txt # Upload tool dependencies
        │
        └── 📝 Notes
            • Direct USB connection via TinyUSB host mode
            • Requires CircuitPython (not standard MicroPython)
            • 4 files total: main.py, dps150_pico.py, config.py, index.html
            • ~50 KB total size
```

## 🎯 Which Version is Right for Me?

### PC Version (Desktop & Web)
**Use when:**
- ✅ You have a PC/laptop available
- ✅ You need graphs and advanced features
- ✅ You want multi-language support
- ✅ You prefer desktop app or browser interface

**Features:**
- Full GUI with graphs
- WebSocket real-time updates
- Multi-language (EN, DE, FR, ES, CN)
- Portable executables possible

### Raspberry Pi Pico W Version
**Use when:**
- ✅ You want a standalone solution
- ✅ No PC available/desired
- ✅ Mobile/portable operation
- ✅ Low power consumption important
- ✅ Cost-effective solution (~$10)

**Features:**
- WiFi Access Point
- Web interface
- Completely autonomous
- Battery operation possible
- Direct USB connection (TinyUSB)

## 🔄 Detailed Differences

| Feature | PC Version | Pico W Version |
|---------|-----------|----------------|
| Hardware | PC/Laptop | Raspberry Pi Pico W + USB OTG |
| Power Consumption | ~20-50W | ~0.5-1W |
| Cost | Free (software) | ~$10-15 (hardware) |
| USB Connection | Direct | Via USB OTG adapter |
| Web Server | Flask + SocketIO | CircuitPython HTTP |
| Real-time Updates | WebSocket | HTTP Polling |
| Graphs | ✅ Plotly | ❌ Not available |
| Languages | 5 languages | English only |
| Mobile Use | ⚠️ PC required | ✅ Fully mobile |
| Memory Required | ~100 MB | ~50 KB |
| Setup Time | 5 minutes | 10-15 minutes |
| Software | Python 3.11+ | CircuitPython 8.0+ |

## 🚀 Quick Comparison: What Can I Do?

### Both Versions Can:
- ✅ Set voltage and current
- ✅ Enable/disable output
- ✅ Display measurements (V, A, W, °C)
- ✅ Configure protection settings
- ✅ Control via web interface

### PC Version Only:
- 📊 Graphical display of measurements
- 🌍 Multi-language interface
- 💾 Data logging possible
- 🖥️ Native desktop app

### Pico W Version Only:
- 📱 Usable without PC
- 🔋 Battery operation possible
- 📡 Own WiFi hotspot
- 💰 Very cost-effective
- 🔌 Direct USB connection

## 📥 Installation - Quick Overview

### PC Version
```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

### Pico W Version
```bash
# 1. Flash CircuitPython to Pico W
# 2. Upload files:
cd pico_w
pip install -r requirements-pico.txt
python upload.py
# → WiFi: "DPS150-Control"
# → http://192.168.4.1
```

## 🤝 Can I Use Both?

**Yes!** The versions are fully compatible:
- Same hardware (DPS-150)
- Same protocol
- You can switch between versions
- Simply reconnect DPS-150

## 📚 More Information

- **PC Version:** See [README.md](README.md) in main directory
- **Pico W Version:** See [pico_w/README.md](pico_w/README.md)
- **Quick Start Pico W:** See [pico_w/QUICKSTART.md](pico_w/QUICKSTART.md)
- **Hardware Setup:** See [pico_w/WIRING.txt](pico_w/WIRING.txt)
- **Technical Details:** See [pico_w/IMPLEMENTATION_NOTES.md](pico_w/IMPLEMENTATION_NOTES.md)
