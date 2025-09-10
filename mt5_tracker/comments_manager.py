"""
CommentsManager - Manejo de persistencia de comentarios

Maneja el guardado y carga de comentarios editados por el usuario,
manteniéndolos incluso cuando se recargan las operaciones desde MT5.
"""

import os
import json
from datetime import datetime


class CommentsManager:
    """Maneja la persistencia de comentarios editados por el usuario"""
    
    def __init__(self, output_dir="output"):
        """Inicializa el CommentsManager con el directorio de salida"""
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def get_comments_file_path(self, account_id):
        """Obtiene la ruta del archivo de comentarios para una cuenta"""
        return os.path.join(self.output_dir, f"comments_Account_{account_id}.json")
    
    def load_comments(self, account_id):
        """Carga los comentarios guardados para una cuenta"""
        comments_file = self.get_comments_file_path(account_id)
        
        if not os.path.exists(comments_file):
            return {}
        
        try:
            with open(comments_file, 'r', encoding='utf-8') as file:
                comments_data = json.load(file)
                return comments_data.get('comments', {})
        except Exception as e:
            print(f"⚠️ Error al cargar comentarios: {e}")
            return {}
    
    def save_comment(self, account_id, position_id, comment):
        """Guarda un comentario específico para una posición"""
        comments_file = self.get_comments_file_path(account_id)
        
        # Cargar comentarios existentes
        comments_data = self._load_comments_data(comments_file)
        
        # Actualizar comentario
        comments_data['comments'][str(position_id)] = comment
        comments_data['last_updated'] = datetime.now().isoformat()
        
        # Guardar archivo
        try:
            with open(comments_file, 'w', encoding='utf-8') as file:
                json.dump(comments_data, file, indent=2, ensure_ascii=False)
            print(f"✅ Comentario guardado para Position ID {position_id}")
        except Exception as e:
            print(f"❌ Error al guardar comentario: {e}")
    
    def apply_comments_to_trades(self, trades_data, account_id):
        """Aplica los comentarios guardados a las operaciones cargadas"""
        saved_comments = self.load_comments(account_id)
        
        if not saved_comments:
            return trades_data
        
        # Aplicar comentarios guardados a las operaciones
        for trade in trades_data:
            position_id = str(trade.get('position_id', ''))
            if position_id in saved_comments:
                trade['comment'] = saved_comments[position_id]
                print(f"📝 Comentario aplicado a Position ID {position_id}: '{saved_comments[position_id]}'")
        
        print(f"✅ Aplicados {len(saved_comments)} comentarios guardados a las operaciones")
        return trades_data
    
    def _load_comments_data(self, comments_file):
        """Carga los datos completos del archivo de comentarios"""
        if not os.path.exists(comments_file):
            return {
                'account_id': '',
                'comments': {},
                'last_updated': '',
                'total_comments': 0
            }
        
        try:
            with open(comments_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"⚠️ Error al cargar datos de comentarios: {e}")
            return {
                'account_id': '',
                'comments': {},
                'last_updated': '',
                'total_comments': 0
            }
    
