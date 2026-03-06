"""
Database Module - Sistema de Cobranzas (Streamlit)
Maneja la persistencia de datos usando SQLite
"""

import sqlite3
import uuid
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import pandas as pd
import streamlit as st

# ==================== DATA CLASSES ====================

@dataclass
class Cliente:
    id: str
    nombre: str
    telefono: str
    direccion: str
    email: str
    fecha_inicio: str
    total_deuda: float
    total_pagado: float
    saldo_pendiente: float
    estado: str
    producto: str
    notas: str
    created_at: str
    updated_at: str

@dataclass
class Pago:
    id: str
    cliente_id: str
    cliente_nombre: str = ""  # Para joins
    fecha: str
    monto: float
    tipo: str
    metodo: str
    notas: str
    created_at: str

@dataclass
class Recordatorio:
    id: str
    cliente_id: str
    cliente_nombre: str = ""  # Para joins
    tipo: str
    fecha_programada: str
    mensaje: str
    estado: str
    fecha_envio: Optional[str] = None
    created_at: str = ""

# ==================== DATABASE CLASS ====================

class Database:
    def __init__(self, db_path: str = "sistema_cobranzas.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de Clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL,
                direccion TEXT NOT NULL,
                email TEXT,
                fecha_inicio TEXT NOT NULL,
                total_deuda REAL DEFAULT 0,
                total_pagado REAL DEFAULT 0,
                saldo_pendiente REAL DEFAULT 0,
                estado TEXT DEFAULT 'pendiente',
                producto TEXT NOT NULL,
                notas TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Tabla de Pagos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id TEXT PRIMARY KEY,
                cliente_id TEXT NOT NULL,
                fecha TEXT NOT NULL,
                monto REAL NOT NULL,
                tipo TEXT NOT NULL,
                metodo TEXT NOT NULL,
                notas TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            )
        ''')
        
        # Tabla de Recordatorios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recordatorios (
                id TEXT PRIMARY KEY,
                cliente_id TEXT NOT NULL,
                tipo TEXT NOT NULL,
                fecha_programada TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                fecha_envio TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
            )
        ''')
        
        # Crear índices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pagos_cliente ON pagos(cliente_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pagos_fecha ON pagos(fecha)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recordatorios_cliente ON recordatorios(cliente_id)')
        
        conn.commit()
        conn.close()
    
    # ==================== CLIENTES CRUD ====================
    
    def crear_cliente(self, nombre: str, telefono: str, direccion: str, 
                      email: str, total_deuda: float, producto: str, 
                      notas: str = "") -> str:
        """Crea un nuevo cliente y retorna su ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cliente_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO clientes (id, nombre, telefono, direccion, email, 
                                 fecha_inicio, total_deuda, total_pagado, 
                                 saldo_pendiente, estado, producto, notas, 
                                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cliente_id, nombre, telefono, direccion, email, now,
              total_deuda, 0, total_deuda, 
              'pendiente' if total_deuda > 0 else 'al_dia',
              producto, notas, now, now))
        
        conn.commit()
        conn.close()
        return cliente_id
    
    def get_clientes(self) -> pd.DataFrame:
        """Obtiene todos los clientes como DataFrame"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT * FROM clientes 
            ORDER BY nombre ASC
        ''', conn)
        conn.close()
        return df
    
    def get_cliente_by_id(self, cliente_id: str) -> Optional[Dict]:
        """Obtiene un cliente por su ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    def actualizar_cliente(self, cliente_id: str, **kwargs) -> bool:
        """Actualiza los datos de un cliente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Campos permitidos
        campos_permitidos = ['nombre', 'telefono', 'direccion', 'email', 
                            'producto', 'notas']
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in campos_permitidos:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(cliente_id)
        
        query = f"UPDATE clientes SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        return True
    
    def eliminar_cliente(self, cliente_id: str) -> bool:
        """Elimina un cliente y todos sus pagos/recordatorios"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
        
        conn.commit()
        conn.close()
        return True
    
    # ==================== PAGOS CRUD ====================
    
    def registrar_pago(self, cliente_id: str, monto: float, tipo: str, 
                       metodo: str, notas: str = "") -> str:
        """
        Registra un nuevo pago y actualiza el saldo del cliente.
        Retorna el ID del pago creado.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener cliente actual
        cursor.execute('''
            SELECT total_deuda, total_pagado, saldo_pendiente 
            FROM clientes WHERE id = ?
        ''', (cliente_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError("Cliente no encontrado")
        
        total_deuda, total_pagado, saldo_pendiente = row
        
        # Calcular nuevos valores
        nuevo_total_pagado = total_pagado + monto
        nuevo_saldo = total_deuda - nuevo_total_pagado
        
        # Determinar nuevo estado
        if nuevo_saldo <= 0:
            nuevo_estado = 'al_dia'
        elif nuevo_saldo < saldo_pendiente:
            nuevo_estado = 'pendiente'
        else:
            nuevo_estado = 'atrasado'
        
        # Crear pago
        pago_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO pagos (id, cliente_id, fecha, monto, tipo, metodo, notas, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pago_id, cliente_id, now, monto, tipo, metodo, notas, now))
        
        # Actualizar cliente
        cursor.execute('''
            UPDATE clientes 
            SET total_pagado = ?, saldo_pendiente = ?, estado = ?, updated_at = ?
            WHERE id = ?
        ''', (nuevo_total_pagado, max(0, nuevo_saldo), nuevo_estado, now, cliente_id))
        
        conn.commit()
        conn.close()
        
        return pago_id
    
    def get_pagos(self, cliente_id: str = None) -> pd.DataFrame:
        """Obtiene los pagos, opcionalmente filtrados por cliente"""
        conn = self.get_connection()
        
        if cliente_id:
            query = '''
                SELECT p.*, c.nombre as cliente_nombre
                FROM pagos p
                JOIN clientes c ON p.cliente_id = c.id
                WHERE p.cliente_id = ?
                ORDER BY p.fecha DESC
            '''
            df = pd.read_sql_query(query, conn, params=(cliente_id,))
        else:
            query = '''
                SELECT p.*, c.nombre as cliente_nombre
                FROM pagos p
                JOIN clientes c ON p.cliente_id = c.id
                ORDER BY p.fecha DESC
            '''
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def eliminar_pago(self, pago_id: str) -> bool:
        """Elimina un pago y recalcula el saldo del cliente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener información del pago
        cursor.execute('SELECT cliente_id, monto FROM pagos WHERE id = ?', (pago_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        cliente_id, monto = row
        
        # Obtener datos del cliente
        cursor.execute('''
            SELECT total_pagado, saldo_pendiente, total_deuda
            FROM clientes WHERE id = ?
        ''', (cliente_id,))
        
        cliente_row = cursor.fetchone()
        total_pagado, saldo_pendiente, total_deuda = cliente_row
        
        # Recalcular
        nuevo_total_pagado = max(0, total_pagado - monto)
        nuevo_saldo = total_deuda - nuevo_total_pagado
        
        if nuevo_saldo <= 0:
            nuevo_estado = 'al_dia'
        elif nuevo_saldo < total_deuda:
            nuevo_estado = 'pendiente'
        else:
            nuevo_estado = 'atrasado'
        
        # Eliminar pago
        cursor.execute('DELETE FROM pagos WHERE id = ?', (pago_id,))
        
        # Actualizar cliente
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE clientes 
            SET total_pagado = ?, saldo_pendiente = ?, estado = ?, updated_at = ?
            WHERE id = ?
        ''', (nuevo_total_pagado, nuevo_saldo, nuevo_estado, now, cliente_id))
        
        conn.commit()
        conn.close()
        return True
    
    # ==================== RECORDATORIOS CRUD ====================
    
    def crear_recordatorio(self, cliente_id: str, tipo: str, 
                          fecha_programada: str, mensaje: str) -> str:
        """Crea un nuevo recordatorio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        recordatorio_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO recordatorios (id, cliente_id, tipo, fecha_programada, 
                                      mensaje, estado, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (recordatorio_id, cliente_id, tipo, fecha_programada, 
              mensaje, 'pendiente', now))
        
        conn.commit()
        conn.close()
        return recordatorio_id
    
    def get_recordatorios(self, cliente_id: str = None) -> pd.DataFrame:
        """Obtiene los recordatorios"""
        conn = self.get_connection()
        
        if cliente_id:
            query = '''
                SELECT r.*, c.nombre as cliente_nombre
                FROM recordatorios r
                JOIN clientes c ON r.cliente_id = c.id
                WHERE r.cliente_id = ?
                ORDER BY r.fecha_programada ASC
            '''
            df = pd.read_sql_query(query, conn, params=(cliente_id,))
        else:
            query = '''
                SELECT r.*, c.nombre as cliente_nombre
                FROM recordatorios r
                JOIN clientes c ON r.cliente_id = c.id
                ORDER BY r.fecha_programada ASC
            '''
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def marcar_recordatorio_enviado(self, recordatorio_id: str) -> bool:
        """Marca un recordatorio como enviado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            UPDATE recordatorios 
            SET estado = ?, fecha_envio = ?
            WHERE id = ?
        ''', ('enviado', now, recordatorio_id))
        
        conn.commit()
        conn.close()
        return True
    
    def eliminar_recordatorio(self, recordatorio_id: str) -> bool:
        """Elimina un recordatorio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM recordatorios WHERE id = ?', (recordatorio_id,))
        
        conn.commit()
        conn.close()
        return True
    
    # ==================== REPORTES Y ESTADÍSTICAS ====================
    
    def get_resumen_cartera(self) -> Dict[str, Any]:
        """Obtiene el resumen de la cartera"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Totales
        cursor.execute('''
            SELECT 
                COUNT(*) as total_clientes,
                SUM(CASE WHEN estado = 'al_dia' THEN 1 ELSE 0 END) as clientes_al_dia,
                SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as clientes_pendientes,
                SUM(CASE WHEN estado = 'atrasado' THEN 1 ELSE 0 END) as clientes_atrasados,
                SUM(total_deuda) as total_deuda,
                SUM(total_pagado) as total_pagado,
                SUM(saldo_pendiente) as total_por_cobrar
            FROM clientes
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'total_clientes': row[0] or 0,
                'clientes_al_dia': row[1] or 0,
                'clientes_pendientes': row[2] or 0,
                'clientes_atrasados': row[3] or 0,
                'total_deuda': row[4] or 0,
                'total_pagado': row[5] or 0,
                'total_por_cobrar': row[6] or 0
            }
        return {}
    
    def get_clientes_atrasados(self) -> pd.DataFrame:
        """Obtiene los clientes con pagos atrasados"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT * FROM clientes 
            WHERE estado = 'atrasado'
            ORDER BY saldo_pendiente DESC
        ''', conn)
        conn.close()
        return df
    
    def exportar_datos(self) -> Dict:
        """Exporta todos los datos para backup"""
        return {
            'clientes': self.get_clientes().to_dict('records'),
            'pagos': self.get_pagos().to_dict('records'),
            'recordatorios': self.get_recordatorios().to_dict('records'),
            'fecha_exportacion': datetime.now().isoformat()
        }

# ==================== SINGLETON INSTANCE ====================

@st.cache_resource
def get_database():
    """Retorna una instancia singleton de la base de datos"""
    return Database()
