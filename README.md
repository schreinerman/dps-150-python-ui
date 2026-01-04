# FNIRSI DPS-150 Control - Python Edition

Multi-language control software for the FNIRSI DPS-150 programmable power supply with native desktop application and web interface.

## � Available Versions

- **Desktop/Web (PC)** - Full Version with all Features (Root folder)
- **[Raspberry Pi Pico W](pico_w/)** - Standalone WiFi-Solution (see also [pico_w/README.md](pico_w/README.md))

## �🌍 Multi-Language Support

The application automatically detects your system language and supports:
- 🇬🇧 English
- 🇩🇪 Deutsch (German)
- 🇫🇷 Français (French)
- 🇪🇸 Español (Spanish)
- 🇨🇳 中文 (Chinese)

### Changing Language

#### Desktop Application (GUI)
Use the menu bar: `Language / Sprache / 语言` → Select your preferred language → Restart the application

#### Web Application
The language is automatically detected from your browser settings. Translations are applied dynamically.

## ✨ Features

- **Native Desktop Application** - Cross-platform GUI built with PyQt6
  - Real-time measurement display (voltage, current, power)
  - Interactive graphs with PyQtGraph
  - Output control and protection settings
  - Display brightness adjustment
  - Multi-language menu

- **Web Application** - Modern web interface with Flask & Vue.js
  - Real-time WebSocket updates
  - RESTful API
  - Responsive design with Vuetify
  - Interactive Plotly graphs
  - Multi-language support (auto-detection)

- **CLI Tool** - Simple command-line interface for quick control

- **Raspberry Pi Pico W** - Portable standalone solution 🆕
  - WiFi Access Point
  - No PC required
  - Low power consumption
  - See [pico_w/README.md](pico_w/) for details

## 🚀 Quick Start

### Desktop Application

```bash
# Install dependencies
pip install -r requirements-gui.txt

# Run the application
python gui_app.py

# Or build standalone executable
./build.sh  # macOS/Linux
build.bat   # Windows
```

The application will be created in the `dist/` folder.

### Web Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Open http://localhost:5000 in your browser.

### CLI Tool

```bash
python cli.py
```

## 📦 Installation

### Requirements
- Python 3.11+
- Serial port access
- FNIRSI DPS-150 power supply

### Dependencies

#### Desktop Application
```bash
pip install -r requirements-gui.txt
```

#### Web Application
```bash
pip install -r requirements.txt
```

#### Build Tools (for creating executables)
```bash
pip install -r requirements-build.txt
```

## 🛠️ Building Executables

### All Platforms
```bash
python build.py
```

### Platform-Specific Scripts

**macOS/Linux:**
```bash
./build.sh
```

**Windows:**
```bash
build.bat
```

The compiled application will be in the `dist/` directory.

## 🔧 Development

### Project Structure
```
dps-150-python-ui/
├── app.py                  # Flask web server
├── gui_app.py             # PyQt6 desktop application
├── dps150.py              # DPS-150 serial protocol implementation
├── cli.py                 # Command-line interface
├── translations.py        # i18n translation system
├── templates/             # Web application HTML templates
│   └── index.html
├── static/                # Static files for web app
│   └── translations.js    # JavaScript translations
├── build.py               # PyInstaller build script
├── build.sh               # Unix build script
├── build.bat              # Windows build script
└── requirements*.txt      # Python dependencies
```

### API Reference

#### DPS150 Class

```python
from dps150 import DPS150, VOLTAGE_SET, CURRENT_SET

async def main():
    dps = DPS150('/dev/ttyUSB0', callback=on_data)
    await dps.start()
    
    # Set voltage and current
    await dps.set_float_value(VOLTAGE_SET, 12.0)
    await dps.set_float_value(CURRENT_SET, 2.5)
    
    # Enable output
    await dps.enable()
    
    # Get all parameters
    await dps.get_all()
    
    await dps.stop()
```

#### Translation System

```python
from translations import set_language, tr

# Set language
set_language('de')  # German

# Translate text
text = tr('connect')  # Returns "Verbinden"
text = tr('connected_to', port='/dev/ttyUSB0')  # Returns "Verbunden mit /dev/ttyUSB0"
```

## 🌐 CI/CD

### GitLab CI/CD

The project includes a `.gitlab-ci.yml` configuration for automatic builds on:
- macOS
- Linux (Docker)
- Windows

Artifacts are automatically created for each platform and available for download.

### Requirements
- GitLab Runner with tags: `macos`, `linux`, `windows`
- Python 3.11+ on all runners

## 📡 Serial Communication

The DPS-150 uses a custom binary protocol over RS-232 (115200 baud, 8N1, RTS/CTS flow control).

### Automatic Port Detection

Both applications automatically detect and select the DPS-150 if "AT32" appears in the port description.

### Protocol Implementation

See `dps150.py` for full protocol details including:
- Float value commands (voltage, current, power limits)
- Byte value commands (brightness, volume)
- Protection parameters (OVP, OCP, OPP, OTP, LVP)
- Group settings (6 memory groups)
- Real-time measurements

## 🔒 Thread Safety

The DPS-150 class uses `asyncio.Lock` to ensure thread-safe serial communication, preventing command corruption when multiple threads access the device.

## 📝 License

See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

### Adding New Languages

1. **Desktop App:** Edit `translations.py` and add your language to the `TRANSLATIONS` dictionary
2. **Web App:** Edit `static/translations.js` and add your language to the `translations` object
3. Test the application with your new language
4. Submit a pull request

## 📞 Support

For issues, questions, or feature requests, please use the GitHub issue tracker.

---

## 🌍 Sprachunterstützung / Language Support

**English:** This application supports multiple languages including English, German, French, Spanish, and Chinese. The language is automatically detected from your system settings.

**Deutsch:** Diese Anwendung unterstützt mehrere Sprachen, darunter Englisch, Deutsch, Französisch, Spanisch und Chinesisch. Die Sprache wird automatisch aus Ihren Systemeinstellungen erkannt.

**Français:** Cette application prend en charge plusieurs langues, notamment l'anglais, l'allemand, le français, l'espagnol et le chinois. La langue est automatiquement détectée à partir de vos paramètres système.

**Español:** Esta aplicación admite varios idiomas, incluidos inglés, alemán, francés, español y chino. El idioma se detecta automáticamente desde la configuración del sistema.

**中文:** 此应用程序支持多种语言，包括英语、德语、法语、西班牙语和中文。语言会自动从您的系统设置中检测。

---

## 👥 Contributors

- Original JavaScript version: [cho45](https://github.com/cho45)

## 🙏 Acknowledgments

- FNIRSI for developing the DPS-150 power supply
- cho45 for the original JavaScript implementation and protocol reverse engineering

## 🔗 Links

- FNIRSI DPS-150: https://www.fnirsi.com/products/dps-150
- Original Repository: https://github.com/cho45/fnirsi-dps-150
