"""
TradeTracker - Lógica de procesamiento de operaciones

Extrae y procesa operaciones de MT5, filtrando cierres finales,
agrupando por position_id y calculando datos formateados.
"""

from datetime import datetime


class TradeTracker:
    """Procesa operaciones de MT5 y las formatea para la aplicación"""
    
    def __init__(self):
        """Inicializa el tracker de operaciones"""
        self.log_messages = []
    
    def process_trades(self, raw_trades):
        """
        Procesa operaciones crudas de MT5 y las formatea
        
        Args:
            raw_trades: Lista de operaciones crudas de MT5
            
        Returns:
            Lista de operaciones formateadas
        """
        if not raw_trades:
            self.log("❌ No hay operaciones para procesar")
            return []
        
        try:
            self.log("🔍 Procesando operaciones de MT5...")
            
            # Constantes para deal.entry
            DEAL_ENTRY_IN = 0    # Apertura
            DEAL_ENTRY_OUT = 1   # Cierre
            
            # Filtrar SOLO operaciones CERRADAS (trades completos)
            closed_trades = []
            for trade in raw_trades:
                # Solo operaciones de trading (tipos 0 y 1) con símbolo
                if trade.type in [0, 1] and trade.symbol:
                    # Verificar si es una operación de CIERRE (trade completo)
                    if hasattr(trade, 'entry'):
                        if trade.entry == DEAL_ENTRY_OUT:
                            # Obtener comentario para verificar si es cierre parcial
                            comment = trade.comment if hasattr(trade, 'comment') else ''
                            
                            # EXCLUIR SOLO cierres parciales basándose en comentarios
                            if any(partial_indicator in comment.lower() for partial_indicator in [
                                'cierre parcial', 'partial close', 'partial', 'parcial'
                            ]):
                                self.log(f"❌ CIERRE PARCIAL excluido: Ticket {trade.ticket}, {trade.symbol} - Comment: '{comment}'")
                                continue
                            
                            closed_trades.append(trade)
                            self.log(f"✅ CIERRE FINAL incluido: Tipo {trade.type}, Símbolo {trade.symbol}, Ticket {trade.ticket}, Entry: {trade.entry}")
                        else:
                            self.log(f"❌ APERTURA excluida: Tipo {trade.type}, Símbolo {trade.symbol}, Ticket {trade.ticket}, Entry: {trade.entry}")
                    else:
                        # Si no tiene atributo entry, usar lógica alternativa
                        if trade.volume > 0:
                            closed_trades.append(trade)
                            self.log(f"✅ CIERRE incluido (sin entry): Tipo {trade.type}, Símbolo {trade.symbol}, Ticket {trade.ticket}")
                        else:
                            self.log(f"❌ CIERRE excluido (sin entry): Tipo {trade.type}, Símbolo {trade.symbol}, Ticket {trade.ticket}, Vol {trade.volume}")
            
            self.log(f"📊 Operaciones de CIERRE filtradas: {len(closed_trades)}")
            
            # Agrupar operaciones por POSITION_ID (no por ticket)
            positions = self._group_trades_by_position(raw_trades)
            
            self.log(f"📊 Posiciones encontradas: {len(positions)}")
            
            # Procesar solo posiciones CERRADAS (que tengan tanto apertura como cierre)
            formatted_trades = self._format_closed_positions(positions)
            
            # Ordenar por fecha de entrada (cronológicamente)
            formatted_trades = self._sort_trades_chronologically(formatted_trades)
            
            self.log(f"✅ Procesadas {len(formatted_trades)} posiciones cerradas únicas por POSITION_ID")
            return formatted_trades
            
        except Exception as e:
            self.log(f"❌ Error al procesar operaciones: {e}")
            return []
    
    def _group_trades_by_position(self, raw_trades):
        """Agrupa operaciones por position_id"""
        positions = {}
        DEAL_ENTRY_IN = 0
        DEAL_ENTRY_OUT = 1
        
        for trade in raw_trades:
            # Solo operaciones de trading (tipos 0 y 1) con símbolo
            if trade.type in [0, 1] and trade.symbol:
                # Obtener position_id
                position_id = getattr(trade, 'position_id', None)
                if position_id is None:
                    self.log(f"⚠️ Operación sin position_id: Ticket {trade.ticket}")
                    continue
                
                # Inicializar posición si no existe
                if position_id not in positions:
                    positions[position_id] = {
                        'trades': [],
                        'symbol': trade.symbol,
                        'opening_time': None,
                        'closing_time': None,
                        'total_profit': 0.0,
                        'opening_trade': None,
                        'closing_trade': None
                    }
                
                # Agregar trade a la posición
                positions[position_id]['trades'].append(trade)
                positions[position_id]['total_profit'] += trade.profit
                
                # Determinar si es apertura o cierre
                if hasattr(trade, 'entry'):
                    if trade.entry == DEAL_ENTRY_IN:
                        positions[position_id]['opening_trade'] = trade
                        if positions[position_id]['opening_time'] is None or trade.time < positions[position_id]['opening_time']:
                            positions[position_id]['opening_time'] = trade.time
                    elif trade.entry == DEAL_ENTRY_OUT:
                        positions[position_id]['closing_trade'] = trade
                        if positions[position_id]['closing_time'] is None or trade.time > positions[position_id]['closing_time']:
                            positions[position_id]['closing_time'] = trade.time
        
        return positions
    
    def _format_closed_positions(self, positions):
        """Formatea posiciones cerradas (con apertura y cierre)"""
        formatted_trades = []
        
        for position_id, position_data in positions.items():
            # Solo procesar si tiene apertura y cierre
            if position_data['opening_trade'] and position_data['closing_trade']:
                opening_trade = position_data['opening_trade']
                closing_trade = position_data['closing_trade']
                
                self.log(f"✅ Procesando posición cerrada: ID {position_id}, {position_data['symbol']} - {'COMPRA' if opening_trade.type == 0 else 'VENTA'}")
                
                # Determinar tipo de operación basado en la apertura
                if opening_trade.type == 0:  # Buy en MT5 = COMPRA en nuestro registro
                    trade_type = "COMPRA"
                elif opening_trade.type == 1:  # Sell en MT5 = VENTA en nuestro registro
                    trade_type = "VENTA"
                else:
                    trade_type = f"TIPO_{opening_trade.type}"
                
                # Formatear fechas
                opening_time_str = self._format_timestamp(position_data['opening_time'])
                closing_time_str = self._format_timestamp(position_data['closing_time'])
                
                self.log(f"📅 Fecha de apertura (UTC): {opening_time_str}")
                self.log(f"📅 Fecha de cierre (UTC): {closing_time_str}")
                
                # Usar el beneficio total acumulado
                profit = position_data['total_profit']
                
                formatted_trade = {
                    'ticket': position_id,  # Position ID (Ticket de MT5)
                    'symbol': position_data['symbol'],
                    'type': trade_type,
                    'volume': opening_trade.volume,
                    'price': opening_trade.price,
                    'profit': profit,
                    'time': opening_time_str,
                    'comment': opening_trade.comment or "",
                    'position_id': position_id,  # ID único de la posición
                    'opening_ticket': opening_trade.ticket,  # Ticket de apertura (deal)
                    'closing_ticket': closing_trade.ticket,  # Ticket de cierre (deal)
                    'opening_time': opening_time_str,  # Fecha de apertura
                    'closing_time': closing_time_str  # Fecha de cierre
                }
                formatted_trades.append(formatted_trade)
            else:
                self.log(f"⚠️ Posición incompleta ignorada: ID {position_id} (sin apertura o cierre)")
        
        return formatted_trades
    
    def _format_timestamp(self, timestamp):
        """Formatea un timestamp a string legible"""
        if hasattr(timestamp, 'strftime'):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            try:
                # Convertir a UTC (como en MT5)
                time_utc = datetime.utcfromtimestamp(timestamp)
                return time_utc.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return "Fecha desconocida"
    
    def _sort_trades_chronologically(self, trades):
        """Ordena operaciones cronológicamente por fecha de apertura"""
        # Convertir tiempo a datetime para ordenamiento correcto
        for trade in trades:
            if isinstance(trade['time'], str):
                try:
                    # Convertir string de tiempo a datetime para ordenamiento
                    trade['_sort_time'] = datetime.strptime(trade['time'], '%Y-%m-%d %H:%M:%S')
                except:
                    # Si no se puede convertir, usar tiempo original
                    trade['_sort_time'] = trade['time']
            else:
                trade['_sort_time'] = trade['time']
        
        # Ordenar cronológicamente (más antigua primero, como en el historial real)
        trades.sort(key=lambda x: x['_sort_time'])
        
        # Limpiar campo temporal de ordenamiento
        for trade in trades:
            trade.pop('_sort_time', None)
        
        self.log("✅ Operaciones ordenadas cronológicamente por fecha de APERTURA (como en el historial real)")
        return trades
    
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
