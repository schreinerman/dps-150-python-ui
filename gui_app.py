"""
Native desktop application for FNIRSI DPS-150 control
Uses PyQt6 for cross-platform GUI with multi-language support
"""

import sys
import asyncio
from collections import deque
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QDoubleSpinBox, QSlider,
    QGroupBox, QGridLayout, QMessageBox, QSplitter, QCheckBox, QTabWidget, QMenu
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QAction
from threading import Thread
import traceback

try:
    import pyqtgraph as pg
    PYQTGRAPH_AVAILABLE = True
except ImportError:
    PYQTGRAPH_AVAILABLE = False
    print("PyQtGraph not installed - graph will be disabled")

from dps150 import (
    DPS150, list_serial_ports,
    VOLTAGE_SET, CURRENT_SET, BRIGHTNESS, VOLUME,
    OVP, OCP, OPP, OTP, LVP,
    OUTPUT_ENABLE, METERING_ENABLE,
    GROUP1_VOLTAGE_SET, GROUP1_CURRENT_SET,
    GROUP2_VOLTAGE_SET, GROUP2_CURRENT_SET,
    GROUP3_VOLTAGE_SET, GROUP3_CURRENT_SET,
    GROUP4_VOLTAGE_SET, GROUP4_CURRENT_SET,
    GROUP5_VOLTAGE_SET, GROUP5_CURRENT_SET,
    GROUP6_VOLTAGE_SET, GROUP6_CURRENT_SET,
)

from translations import get_translator, set_language, get_system_language


class DeviceSignals(QObject):
    """Signals for device updates (thread-safe)"""
    data_received = pyqtSignal(dict)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.dps_device = None
        self.event_loop = None
        self.loop_thread = None
        self.signals = DeviceSignals()
        self.signals.data_received.connect(self.on_device_data)
        
        # Data history (maximum 500 data points)
        self.max_points = 500
        self.time_data = deque(maxlen=self.max_points)
        self.voltage_history = deque(maxlen=self.max_points)
        self.current_history = deque(maxlen=self.max_points)
        self.power_history = deque(maxlen=self.max_points)
        self.start_time = None
        
        # Initialize graph variables (if PyQtGraph available)
        self.graph_widget = None
        self.voltage_curve = None
        self.current_curve = None
        self.power_curve = None
        
        # Get translator
        self.tr = get_translator()
        
        # Detect and set system language
        system_lang = get_system_language()
        set_language(system_lang)
        
        self.init_ui()
        self.refresh_ports()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("FNIRSI DPS-150 - Native App")
        self.setMinimumSize(900, 700)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Connection area
        connection_group = self.create_connection_group()
        main_layout.addWidget(connection_group)
        
        # Tab widget for display and graph
        self.tab_widget = QTabWidget()
        
        # Tab 1: Display and Control
        display_control_widget = QWidget()
        display_control_layout = QHBoxLayout(display_control_widget)
        
        # Splitter for main and side area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Main display area (left)
        display_widget = self.create_display_area()
        splitter.addWidget(display_widget)
        
        # Control area (right)
        control_widget = self.create_control_area()
        splitter.addWidget(control_widget)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        display_control_layout.addWidget(splitter)
        self.tab_widget.addTab(display_control_widget, self.tr('display_control'))
        
        # Tab 2: Graph (if PyQtGraph available)
        if PYQTGRAPH_AVAILABLE:
            graph_widget = self.create_graph_area()
            self.tab_widget.addTab(graph_widget, self.tr('graph'))
        
        main_layout.addWidget(self.tab_widget)
    
    def create_menu_bar(self):
        """Create menu bar with language selection"""
        menubar = self.menuBar()
        
        # Language menu
        lang_menu = menubar.addMenu('Language / Sprache / 语言')
        
        # Language actions
        languages = [
            ('English', 'en'),
            ('Deutsch', 'de'),
            ('Français', 'fr'),
            ('Español', 'es'),
            ('中文', 'zh'),
        ]
        
        for lang_name, lang_code in languages:
            action = QAction(lang_name, self)
            action.triggered.connect(lambda checked, lc=lang_code: self.change_language(lc))
            lang_menu.addAction(action)
    
    def change_language(self, language_code):
        """Change application language"""
        set_language(language_code)
        
        # Show restart message
        QMessageBox.information(
            self,
            "Language Changed",
            "Please restart the application for the language change to take full effect.\n\n"
            "Bitte starten Sie die Anwendung neu, damit die Sprachänderung vollständig wirksam wird.\n\n"
            "请重启应用程序以使语言更改完全生效。"
        )
        
    def create_connection_group(self):
        """Create connection area"""
        group = QGroupBox(self.tr('connection'))
        layout = QHBoxLayout()
        
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        self.port_label = QLabel(self.tr('port'))
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton(self.tr('refresh'))
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        self.connect_btn = QPushButton(self.tr('connect'))
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)
        
        self.status_label = QLabel(self.tr('not_connected'))
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
        
    def create_display_area(self):
        """Create main display area"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Voltage display
        voltage_layout = QHBoxLayout()
        self.voltage_label = QLabel("0.00")
        self.voltage_label.setStyleSheet("color: #4CAF50; font-size: 72px; font-weight: bold;")
        voltage_layout.addWidget(self.voltage_label)
        voltage_layout.addWidget(QLabel("V", styleSheet="font-size: 36px; color: #4CAF50;"))
        voltage_layout.addStretch()
        layout.addLayout(voltage_layout)
        
        self.voltage_set_label = QLabel("Set: 0.00 V")
        self.voltage_set_label.setStyleSheet("font-size: 24px; color: #888;")
        layout.addWidget(self.voltage_set_label)
        
        # Current display
        current_layout = QHBoxLayout()
        self.current_label = QLabel("0.000")
        self.current_label.setStyleSheet("color: #FF9800; font-size: 72px; font-weight: bold;")
        current_layout.addWidget(self.current_label)
        current_layout.addWidget(QLabel("A", styleSheet="font-size: 36px; color: #FF9800;"))
        current_layout.addStretch()
        layout.addLayout(current_layout)
        
        self.current_set_label = QLabel("Set: 0.000 A")
        self.current_set_label.setStyleSheet("font-size: 24px; color: #888;")
        layout.addWidget(self.current_set_label)
        
        # Power display
        power_layout = QHBoxLayout()
        self.power_label = QLabel("0.00")
        self.power_label.setStyleSheet("color: #666; font-size: 48px; font-weight: bold;")
        power_layout.addWidget(self.power_label)
        power_layout.addWidget(QLabel("W", styleSheet="font-size: 24px; color: #666;"))
        power_layout.addStretch()
        layout.addLayout(power_layout)
        
        # Status
        self.output_status_label = QLabel("Output: OFF")
        self.output_status_label.setStyleSheet("font-size: 18px; padding: 10px;")
        layout.addWidget(self.output_status_label)
        
        self.protection_label = QLabel("")
        self.protection_label.setStyleSheet("font-size: 16px; color: red; padding: 10px;")
        layout.addWidget(self.protection_label)
        
        layout.addStretch()
        return widget
        
    def create_control_area(self):
        """Create control area"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Output control
        output_group = QGroupBox(self.tr('output'))
        output_layout = QHBoxLayout()
        
        self.output_on_btn = QPushButton(self.tr('output_on'))
        self.output_on_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.output_on_btn.clicked.connect(self.enable_output)
        self.output_on_btn.setEnabled(False)
        output_layout.addWidget(self.output_on_btn)
        
        self.output_off_btn = QPushButton(self.tr('output_off'))
        self.output_off_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 10px;")
        self.output_off_btn.clicked.connect(self.disable_output)
        self.output_off_btn.setEnabled(False)
        output_layout.addWidget(self.output_off_btn)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Voltage control
        voltage_group = QGroupBox(self.tr('set_voltage'))
        voltage_layout = QGridLayout()
        
        voltage_layout.addWidget(QLabel(self.tr('voltage')), 0, 0)
        self.voltage_spinbox = QDoubleSpinBox()
        self.voltage_spinbox.setRange(0, 150)
        self.voltage_spinbox.setDecimals(2)
        self.voltage_spinbox.setSingleStep(0.1)
        self.voltage_spinbox.valueChanged.connect(self.set_voltage)
        self.voltage_spinbox.setEnabled(False)  # Disabled until connection
        voltage_layout.addWidget(self.voltage_spinbox, 0, 1)
        
        voltage_group.setLayout(voltage_layout)
        layout.addWidget(voltage_group)
        
        # Current control
        current_group = QGroupBox(self.tr('set_current'))
        current_layout = QGridLayout()
        
        current_layout.addWidget(QLabel(self.tr('current')), 0, 0)
        self.current_spinbox = QDoubleSpinBox()
        self.current_spinbox.setRange(0, 15)
        self.current_spinbox.setDecimals(3)
        self.current_spinbox.setSingleStep(0.01)
        self.current_spinbox.valueChanged.connect(self.set_current)
        self.current_spinbox.setEnabled(False)  # Disabled until connection
        current_layout.addWidget(self.current_spinbox, 0, 1)
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        # Protection functions
        protection_group = QGroupBox(self.tr('protection'))
        protection_layout = QGridLayout()
        
        protection_layout.addWidget(QLabel(self.tr('ovp')), 0, 0)
        self.ovp_spinbox = QDoubleSpinBox()
        self.ovp_spinbox.setRange(0, 160)
        self.ovp_spinbox.setDecimals(2)
        self.ovp_spinbox.valueChanged.connect(lambda v: self.set_protection(OVP, v))
        protection_layout.addWidget(self.ovp_spinbox, 0, 1)
        
        protection_layout.addWidget(QLabel(self.tr('ocp')), 1, 0)
        self.ocp_spinbox = QDoubleSpinBox()
        self.ocp_spinbox.setRange(0, 16)
        self.ocp_spinbox.setDecimals(2)
        self.ocp_spinbox.valueChanged.connect(lambda v: self.set_protection(OCP, v))
        protection_layout.addWidget(self.ocp_spinbox, 1, 1)
        
        protection_layout.addWidget(QLabel(self.tr('opp')), 2, 0)
        self.opp_spinbox = QDoubleSpinBox()
        self.opp_spinbox.setRange(0, 300)
        self.opp_spinbox.setDecimals(2)
        self.opp_spinbox.valueChanged.connect(lambda v: self.set_protection(OPP, v))
        protection_layout.addWidget(self.opp_spinbox, 2, 1)
        
        protection_group.setLayout(protection_layout)
        layout.addWidget(protection_group)
        
        # Brightness control
        brightness_group = QGroupBox(self.tr('display'))
        brightness_layout = QVBoxLayout()
        
        brightness_layout.addWidget(QLabel(self.tr('brightness')))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 5)
        self.brightness_slider.setValue(5)
        self.brightness_slider.valueChanged.connect(self.set_brightness)
        brightness_layout.addWidget(self.brightness_slider)
        
        brightness_group.setLayout(brightness_layout)
        layout.addWidget(brightness_group)
        
        layout.addStretch()
        return widget
    
    def create_graph_area(self):
        """Create graph area"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configure PyQtGraph
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        
        # Create graph widget
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setLabel('left', self.tr('value'))
        self.graph_widget.setLabel('bottom', self.tr('time_s'))
        self.graph_widget.addLegend()
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Create plots
        self.voltage_curve = self.graph_widget.plot(
            pen=pg.mkPen(color=(76, 175, 80), width=2),
            name=self.tr('voltage_v')
        )
        self.current_curve = self.graph_widget.plot(
            pen=pg.mkPen(color=(255, 152, 0), width=2),
            name=self.tr('current_a')
        )
        self.power_curve = self.graph_widget.plot(
            pen=pg.mkPen(color=(102, 102, 102), width=2),
            name=self.tr('power_w')
        )
        
        layout.addWidget(self.graph_widget)
        
        # Button to reset history
        reset_btn = QPushButton(self.tr('reset_history'))
        reset_btn.clicked.connect(self.reset_history)
        layout.addWidget(reset_btn)
        
        return widget
    
    def reset_history(self):
        """Reset data history"""
        self.time_data.clear()
        self.voltage_history.clear()
        self.current_history.clear()
        self.power_history.clear()
        self.start_time = None
        if PYQTGRAPH_AVAILABLE:
            self.update_graph()
        
    def update_graph(self):
        """Update the graph"""
        if not PYQTGRAPH_AVAILABLE or self.voltage_curve is None:
            return
            
        if len(self.time_data) > 0:
            import numpy as np
            time_array = np.array(list(self.time_data))
            voltage_array = np.array(list(self.voltage_history))
            current_array = np.array(list(self.current_history))
            power_array = np.array(list(self.power_history))
            
            self.voltage_curve.setData(time_array, voltage_array)
            self.current_curve.setData(time_array, current_array)
            self.power_curve.setData(time_array, power_array)
        
    def refresh_ports(self):
        """Update the list of available ports"""
        self.port_combo.clear()
        ports = list_serial_ports()
        at32_index = -1
        for i, port in enumerate(ports):
            self.port_combo.addItem(f"{port['device']} - {port['description']}", port['device'])
            # Remember index if "AT32" is in description
            if 'AT32' in port['description'].upper():
                at32_index = i
        
        # Automatically select AT32 port if found
        if at32_index >= 0:
            self.port_combo.setCurrentIndex(at32_index)
            
    def toggle_connection(self):
        """Connect/disconnect the device"""
        if self.dps_device:
            self.disconnect_device()
        else:
            self.connect_device()
            
    def connect_device(self):
        """Connect to the device"""
        port = self.port_combo.currentData()
        if not port:
            QMessageBox.warning(self, self.tr('error'), self.tr('select_port'))
            return
            
        try:
            self.status_label.setText(self.tr('connecting'))
            self.connect_btn.setEnabled(False)
            
            # Create event loop
            self.event_loop = asyncio.new_event_loop()
            self.loop_thread = Thread(
                target=self.run_event_loop,
                args=(self.event_loop,),
                daemon=True
            )
            self.loop_thread.start()
            
            # Create and connect device
            self.dps_device = DPS150(port, callback=self.device_callback)
            
            future = asyncio.run_coroutine_threadsafe(
                self.dps_device.start(),
                self.event_loop
            )
            future.result(timeout=5)
            
            self.status_label.setText(self.tr('connected_to', port=port))
            self.connect_btn.setText(self.tr('disconnect'))
            self.connect_btn.setEnabled(True)
            self.port_combo.setEnabled(False)
            self.refresh_btn.setEnabled(False)
            
            # Enable control fields
            self.voltage_spinbox.setEnabled(True)
            self.current_spinbox.setEnabled(True)
            self.output_on_btn.setEnabled(True)
            self.output_off_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, self.tr('connection_error'), f"{self.tr('error')}: {str(e)}\n{traceback.format_exc()}")
            self.status_label.setText(self.tr('connection_failed'))
            self.connect_btn.setEnabled(True)
            
    def disconnect_device(self):
        """Disconnect the connection"""
        if self.dps_device:
            try:
                future = asyncio.run_coroutine_threadsafe(
                    self.dps_device.stop(),
                    self.event_loop
                )
                future.result(timeout=5)
            except:
                pass
                
            self.dps_device = None
            
        if self.event_loop:
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)
            self.event_loop = None
            
        self.status_label.setText(self.tr('not_connected'))
        self.connect_btn.setText(self.tr('connect'))
        self.port_combo.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        
        # Disable control fields
        self.voltage_spinbox.setEnabled(False)
        self.current_spinbox.setEnabled(False)
        self.output_on_btn.setEnabled(False)
        self.output_off_btn.setEnabled(False)
        
    def run_event_loop(self, loop):
        """Runs in a separate thread for asyncio"""
        asyncio.set_event_loop(loop)
        loop.run_forever()
        
    def device_callback(self, data):
        """Callback for device data (called in another thread)"""
        # Emit signal for thread-safe update
        self.signals.data_received.emit(data)
        
    def on_device_data(self, data):
        """Update UI with device data (runs in Main Thread)"""
        # Timestamp for graph
        if self.start_time is None:
            self.start_time = datetime.now()
        
        current_time = (datetime.now() - self.start_time).total_seconds()
        
        # Voltage display (outputVoltage instead of voltage)
        if 'outputVoltage' in data:
            voltage = data['outputVoltage']
            self.voltage_label.setText(f"{voltage:.2f}")
            self.voltage_history.append(voltage)
            
        if 'setVoltage' in data:
            set_voltage = data['setVoltage']
            self.voltage_set_label.setText(f"Set: {set_voltage:.2f} V")
            # Only update spinbox if value differs (prevents endless loop)
            if abs(self.voltage_spinbox.value() - set_voltage) > 0.01:
                self.voltage_spinbox.blockSignals(True)
                self.voltage_spinbox.setValue(set_voltage)
                self.voltage_spinbox.blockSignals(False)
            
        # Current display (outputCurrent instead of current)
        if 'outputCurrent' in data:
            current = data['outputCurrent']
            self.current_label.setText(f"{current:.3f}")
            self.current_history.append(current)
            
        if 'setCurrent' in data:
            set_current = data['setCurrent']
            self.current_set_label.setText(f"Set: {set_current:.3f} A")
            # Only update spinbox if value differs
            if abs(self.current_spinbox.value() - set_current) > 0.001:
                self.current_spinbox.blockSignals(True)
                self.current_spinbox.setValue(set_current)
                self.current_spinbox.blockSignals(False)
            
        # Power (outputPower instead of power)
        if 'outputPower' in data:
            power = data['outputPower']
            self.power_label.setText(f"{power:.2f}")
            self.power_history.append(power)
        
        # Add time for graph
        if 'outputVoltage' in data and 'outputCurrent' in data and 'outputPower' in data:
            self.time_data.append(current_time)
            # Update graph
            if PYQTGRAPH_AVAILABLE:
                self.update_graph()
            
        # Output status
        if 'outputClosed' in data:
            output_on = data['outputClosed']
            status_text = self.tr('output_on') if output_on else self.tr('output_off')
            self.output_status_label.setText(f"Output: {status_text}")
            self.output_status_label.setStyleSheet(
                f"font-size: 18px; padding: 10px; color: {'green' if output_on else 'red'}; font-weight: bold;"
            )
            
        # Protection status (protectionState instead of protection_state)
        if 'protectionState' in data:
            state = data['protectionState']
            if state and state != '':
                self.protection_label.setText(self.tr('protection_active', state=state))
            else:
                self.protection_label.setText("")
                
    def set_voltage(self, value):
        """Set voltage"""
        if self.dps_device:
            asyncio.run_coroutine_threadsafe(
                self.dps_device.set_float_value(VOLTAGE_SET, value),
                self.event_loop
            )
            
    def set_current(self, value):
        """Set current"""
        if self.dps_device:
            asyncio.run_coroutine_threadsafe(
                self.dps_device.set_float_value(CURRENT_SET, value),
                self.event_loop
            )
            
    def enable_output(self):
        """Enable output"""
        if not self.dps_device:
            return
            
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.dps_device.enable(),
                self.event_loop
            )
            future.result(timeout=2)
        except Exception as e:
            print(f"Error enabling output: {e}")
            QMessageBox.critical(self, self.tr('error'), self.tr('could_not_enable_output', error=str(e)))
    
    def disable_output(self):
        """Disable output"""
        if not self.dps_device:
            return
            
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.dps_device.disable(),
                self.event_loop
            )
            future.result(timeout=2)
        except Exception as e:
            print(f"Error disabling output: {e}")
            QMessageBox.critical(self, self.tr('error'), self.tr('could_not_disable_output', error=str(e)))
            
    def set_protection(self, param, value):
        """Set protection parameter"""
        if self.dps_device:
            asyncio.run_coroutine_threadsafe(
                self.dps_device.set_float_value(param, value),
                self.event_loop
            )
            
    def set_brightness(self, value):
        """Set display brightness"""
        if self.dps_device:
            asyncio.run_coroutine_threadsafe(
                self.dps_device.set_byte_value(BRIGHTNESS, value),
                self.event_loop
            )
            
    def closeEvent(self, event):
        """Called when the window is closed"""
        self.disconnect_device()
        event.accept()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
