"""
MT5Connector - Conexión con MetaTrader 5

Responsable de conectar y desconectar de MetaTrader 5,
login/logout y obtener operaciones crudas (history_deals_get).
"""

import MetaTrader5 as mt5
from datetime import datetime


class MT5Connector:
    """Conecta con MetaTrader 5 y obtiene operaciones crudas"""
    
    def __init__(self):
        """Inicializa el conector MT5"""
        self.connected = False
        self.log_messages = []
        self.current_login = None
        self.current_password = None
        self.current_server = None
    
    def connect(self, login=None, password=None, server=None):
        """Conecta con MetaTrader 5 usando credenciales específicas"""
        try:
            # Si ya está conectado, desconectar primero
            if self.connected:
                self.disconnect()
            
            # Guardar credenciales
            if login and password and server:
                self.current_login = login
                self.current_password = password
                self.current_server = server
                self.log(f"🔐 Intentando conectar con cuenta: {login} en servidor: {server}")
            else:
                self.log("⚠️ No se proporcionaron credenciales, usando conexión por defecto")
            
            # Inicializar MT5
            if not mt5.initialize():
                self.log("❌ Error: No se pudo inicializar MetaTrader 5")
                return False
        
            # Si tenemos credenciales, intentar login
            if self.current_login and self.current_password and self.current_server:
                # Intentar login con credenciales específicas
                login_result = mt5.login(
                    login=int(self.current_login),
                    password=self.current_password,
                    server=self.current_server
                )
                
                if not login_result:
                    error = mt5.last_error()
                    self.log(f"❌ Error de login: {error}")
                    mt5.shutdown()
                    return False
                
                self.log(f"✅ Login exitoso en cuenta: {self.current_login}")
            
            # Verificar que estamos conectados a la cuenta correcta
            account_info = mt5.account_info()
            if account_info:
                self.log(f"📊 Conectado a cuenta: {account_info.login}")
                self.log(f"📊 Servidor: {account_info.server}")
                self.log(f"📊 Balance: {account_info.balance}")
                
                # Verificar que es la cuenta correcta si se especificaron credenciales
                if self.current_login and str(account_info.login) != str(self.current_login):
                    self.log(f"⚠️ ADVERTENCIA: Conectado a cuenta {account_info.login} en lugar de {self.current_login}")
                    self.log("💡 Esto puede indicar que MT5 está usando credenciales guardadas")
            else:
                self.log("⚠️ No se pudo obtener información de la cuenta")
            
            self.connected = True
            self.log("✅ Conectado a MetaTrader 5")
            return True
            
        except Exception as e:
            self.log(f"❌ Error durante la conexión: {e}")
            if self.connected:
                mt5.shutdown()
                self.connected = False
            return False
    
    def disconnect(self):
        """Desconecta de MetaTrader 5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.log("🔚 Desconectado de MetaTrader 5")
    
    def get_raw_trades(self, from_date=None, to_date=None):
        """Obtiene operaciones crudas de MT5 sin procesar"""
        if not self.connected:
            self.log("❌ No hay conexión con MT5")
            return []
        
        try:
            # Calcular rango de fechas por defecto: últimos 5 años
            if to_date is None:
                to_date = datetime.now()
            if from_date is None:
                from_date = to_date.replace(year=to_date.year - 5)
            
            self.log(f"🔍 Obteniendo operaciones crudas desde {from_date.strftime('%Y-%m-%d')} hasta {to_date.strftime('%Y-%m-%d')}")
            
            # Obtener todas las operaciones del rango
            all_trades = mt5.history_deals_get(from_date, to_date)
            
            if all_trades is None:
                self.log("❌ No se encontraron operaciones en el rango especificado")
                return []
            
            self.log(f"📊 Se encontraron {len(all_trades)} operaciones crudas en MT5")
            return all_trades
            
        except Exception as e:
            self.log(f"❌ Error al obtener operaciones crudas: {e}")
            return []
    
    def get_account_info(self):
        """Obtiene información de la cuenta conectada"""
        if not self.connected:
            return None
        
        try:
            return mt5.account_info()
        except Exception as e:
            self.log(f"❌ Error al obtener información de cuenta: {e}")
            return None
    
    def log(self, message):
        """Registra un mensaje"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_messages.append(log_message)
        print(log_message)
    
    def get_logs(self):
        """Obtiene todos los mensajes de log"""
        return self.log_messages.copy()
    
    def clear_logs(self):
        """Limpia los mensajes de log"""
        self.log_messages.clear()
