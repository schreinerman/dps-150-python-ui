"""
Internationalization (i18n) support for DPS-150 Control
Provides translations for common languages
"""

TRANSLATIONS = {
    'en': {
        # Connection
        'connection': 'Connection',
        'port': 'Port:',
        'refresh': 'Refresh',
        'connect': 'Connect',
        'disconnect': 'Disconnect',
        'not_connected': 'Not connected',
        'connecting': 'Connecting...',
        'connected_to': 'Connected to {port}',
        'connection_failed': 'Connection failed',
        'connection_error': 'Connection Error',
        'select_port': 'Please select a port',
        
        # Output control
        'output': 'Output',
        'output_on': 'Output ON',
        'output_off': 'Output OFF',
        'enable_output': 'Enable Output',
        'disable_output': 'Disable Output',
        
        # Display & Control
        'display_control': 'Display & Control',
        'graph': 'Graph',
        
        # Settings
        'set_voltage': 'Set Voltage',
        'set_current': 'Set Current',
        'voltage': 'Voltage (V):',
        'current': 'Current (A):',
        'set': 'Set: {value} {unit}',
        
        # Protection
        'protection': 'Protection Functions',
        'ovp': 'OVP (V):',
        'ocp': 'OCP (A):',
        'opp': 'OPP (W):',
        'protection_active': '⚠️ Protection active: {state}',
        
        # Display
        'display': 'Display',
        'brightness': 'Brightness:',
        
        # Graph
        'reset_history': 'Reset History',
        'time_s': 'Time (s)',
        'value': 'Value',
        'voltage_v': 'Voltage (V)',
        'current_a': 'Current (A)',
        'power_w': 'Power (W)',
        
        # Errors
        'error': 'Error',
        'could_not_enable_output': 'Could not enable output: {error}',
        'could_not_disable_output': 'Could not disable output: {error}',
    },
    'de': {
        # Connection
        'connection': 'Verbindung',
        'port': 'Port:',
        'refresh': 'Aktualisieren',
        'connect': 'Verbinden',
        'disconnect': 'Trennen',
        'not_connected': 'Nicht verbunden',
        'connecting': 'Verbinde...',
        'connected_to': 'Verbunden mit {port}',
        'connection_failed': 'Verbindung fehlgeschlagen',
        'connection_error': 'Verbindungsfehler',
        'select_port': 'Bitte wählen Sie einen Port aus',
        
        # Output control
        'output': 'Output',
        'output_on': 'Output EIN',
        'output_off': 'Output AUS',
        'enable_output': 'Output aktivieren',
        'disable_output': 'Output deaktivieren',
        
        # Display & Control
        'display_control': 'Anzeige & Steuerung',
        'graph': 'Graph',
        
        # Settings
        'set_voltage': 'Spannung einstellen',
        'set_current': 'Strom einstellen',
        'voltage': 'Spannung (V):',
        'current': 'Strom (A):',
        'set': 'Set: {value} {unit}',
        
        # Protection
        'protection': 'Schutzfunktionen',
        'ovp': 'OVP (V):',
        'ocp': 'OCP (A):',
        'opp': 'OPP (W):',
        'protection_active': '⚠️ Schutz aktiv: {state}',
        
        # Display
        'display': 'Display',
        'brightness': 'Helligkeit:',
        
        # Graph
        'reset_history': 'Historie zurücksetzen',
        'time_s': 'Zeit (s)',
        'value': 'Wert',
        'voltage_v': 'Spannung (V)',
        'current_a': 'Strom (A)',
        'power_w': 'Leistung (W)',
        
        # Errors
        'error': 'Fehler',
        'could_not_enable_output': 'Konnte Output nicht aktivieren: {error}',
        'could_not_disable_output': 'Konnte Output nicht deaktivieren: {error}',
    },
    'fr': {
        # Connection
        'connection': 'Connexion',
        'port': 'Port:',
        'refresh': 'Actualiser',
        'connect': 'Connecter',
        'disconnect': 'Déconnecter',
        'not_connected': 'Non connecté',
        'connecting': 'Connexion...',
        'connected_to': 'Connecté à {port}',
        'connection_failed': 'Échec de la connexion',
        'connection_error': 'Erreur de connexion',
        'select_port': 'Veuillez sélectionner un port',
        
        # Output control
        'output': 'Sortie',
        'output_on': 'Sortie ACTIVÉE',
        'output_off': 'Sortie DÉSACTIVÉE',
        'enable_output': 'Activer la sortie',
        'disable_output': 'Désactiver la sortie',
        
        # Display & Control
        'display_control': 'Affichage et Contrôle',
        'graph': 'Graphique',
        
        # Settings
        'set_voltage': 'Régler la tension',
        'set_current': 'Régler le courant',
        'voltage': 'Tension (V):',
        'current': 'Courant (A):',
        'set': 'Réglage: {value} {unit}',
        
        # Protection
        'protection': 'Fonctions de protection',
        'ovp': 'OVP (V):',
        'ocp': 'OCP (A):',
        'opp': 'OPP (W):',
        'protection_active': '⚠️ Protection active: {state}',
        
        # Display
        'display': 'Affichage',
        'brightness': 'Luminosité:',
        
        # Graph
        'reset_history': 'Réinitialiser l\'historique',
        'time_s': 'Temps (s)',
        'value': 'Valeur',
        'voltage_v': 'Tension (V)',
        'current_a': 'Courant (A)',
        'power_w': 'Puissance (W)',
        
        # Errors
        'error': 'Erreur',
        'could_not_enable_output': 'Impossible d\'activer la sortie: {error}',
        'could_not_disable_output': 'Impossible de désactiver la sortie: {error}',
    },
    'es': {
        # Connection
        'connection': 'Conexión',
        'port': 'Puerto:',
        'refresh': 'Actualizar',
        'connect': 'Conectar',
        'disconnect': 'Desconectar',
        'not_connected': 'No conectado',
        'connecting': 'Conectando...',
        'connected_to': 'Conectado a {port}',
        'connection_failed': 'Conexión fallida',
        'connection_error': 'Error de conexión',
        'select_port': 'Por favor seleccione un puerto',
        
        # Output control
        'output': 'Salida',
        'output_on': 'Salida ENCENDIDA',
        'output_off': 'Salida APAGADA',
        'enable_output': 'Activar salida',
        'disable_output': 'Desactivar salida',
        
        # Display & Control
        'display_control': 'Pantalla y Control',
        'graph': 'Gráfico',
        
        # Settings
        'set_voltage': 'Ajustar voltaje',
        'set_current': 'Ajustar corriente',
        'voltage': 'Voltaje (V):',
        'current': 'Corriente (A):',
        'set': 'Ajuste: {value} {unit}',
        
        # Protection
        'protection': 'Funciones de protección',
        'ovp': 'OVP (V):',
        'ocp': 'OCP (A):',
        'opp': 'OPP (W):',
        'protection_active': '⚠️ Protección activa: {state}',
        
        # Display
        'display': 'Pantalla',
        'brightness': 'Brillo:',
        
        # Graph
        'reset_history': 'Resetear historial',
        'time_s': 'Tiempo (s)',
        'value': 'Valor',
        'voltage_v': 'Voltaje (V)',
        'current_a': 'Corriente (A)',
        'power_w': 'Potencia (W)',
        
        # Errors
        'error': 'Error',
        'could_not_enable_output': 'No se pudo activar la salida: {error}',
        'could_not_disable_output': 'No se pudo desactivar la salida: {error}',
    },
    'zh': {
        # Connection
        'connection': '连接',
        'port': '端口:',
        'refresh': '刷新',
        'connect': '连接',
        'disconnect': '断开',
        'not_connected': '未连接',
        'connecting': '正在连接...',
        'connected_to': '已连接到 {port}',
        'connection_failed': '连接失败',
        'connection_error': '连接错误',
        'select_port': '请选择端口',
        
        # Output control
        'output': '输出',
        'output_on': '输出开启',
        'output_off': '输出关闭',
        'enable_output': '启用输出',
        'disable_output': '禁用输出',
        
        # Display & Control
        'display_control': '显示与控制',
        'graph': '图表',
        
        # Settings
        'set_voltage': '设置电压',
        'set_current': '设置电流',
        'voltage': '电压 (V):',
        'current': '电流 (A):',
        'set': '设置: {value} {unit}',
        
        # Protection
        'protection': '保护功能',
        'ovp': 'OVP (V):',
        'ocp': 'OCP (A):',
        'opp': 'OPP (W):',
        'protection_active': '⚠️ 保护激活: {state}',
        
        # Display
        'display': '显示',
        'brightness': '亮度:',
        
        # Graph
        'reset_history': '重置历史',
        'time_s': '时间 (s)',
        'value': '值',
        'voltage_v': '电压 (V)',
        'current_a': '电流 (A)',
        'power_w': '功率 (W)',
        
        # Errors
        'error': '错误',
        'could_not_enable_output': '无法启用输出: {error}',
        'could_not_disable_output': '无法禁用输出: {error}',
    },
}


class Translator:
    """Simple translator class"""
    
    def __init__(self, language='en'):
        self.language = language
        
    def set_language(self, language):
        """Set the current language"""
        if language in TRANSLATIONS:
            self.language = language
        else:
            print(f"Warning: Language '{language}' not found, using English")
            self.language = 'en'
            
    def translate(self, key, **kwargs):
        """Translate a key with optional formatting arguments"""
        if self.language in TRANSLATIONS and key in TRANSLATIONS[self.language]:
            text = TRANSLATIONS[self.language][key]
        elif key in TRANSLATIONS['en']:
            text = TRANSLATIONS['en'][key]
        else:
            return key
            
        # Format with kwargs if provided
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text
    
    def __call__(self, key, **kwargs):
        """Allow translator to be called directly"""
        return self.translate(key, **kwargs)


# Global translator instance
_translator = Translator('en')


def get_translator():
    """Get the global translator instance"""
    return _translator


def set_language(language):
    """Set the global language"""
    _translator.set_language(language)


def tr(key, **kwargs):
    """Shortcut for translation"""
    return _translator.translate(key, **kwargs)


# Detect system language
def get_system_language():
    """Detect system language"""
    import locale
    try:
        lang = locale.getdefaultlocale()[0]
        if lang:
            # Extract language code (e.g., 'de_DE' -> 'de')
            lang_code = lang.split('_')[0].lower()
            if lang_code in TRANSLATIONS:
                return lang_code
    except:
        pass
    return 'en'
