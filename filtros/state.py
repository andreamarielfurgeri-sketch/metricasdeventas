"""
Sistema centralizado de estado de filtros para Streamlit
Manejo seguro y persistente del estado de filtros sin errores de session_state
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import numpy as np


def init_filtros_state(data: Dict[str, Any]) -> None:
    """
    Inicializa el estado de filtros UNA SOLA VEZ de forma segura.
    
    Args:
        data: Diccionario con datos necesarios para inicialización
              - df_fac: DataFrame de facturación
              - df_cot: DataFrame de cotizaciones
              - fechas_default: Diccionario con fechas por defecto
    """
    # Verificar si ya está inicializado para evitar múltiples inicializaciones
    if 'filtros_inicializados' in st.session_state:
        return
    
    # Extraer datos necesarios
    df_fac = data.get('df_fac')
    df_cot = data.get('df_cot')
    fechas_default = data.get('fechas_default')
    
    # Obtener lista completa de vendedores
    todos_vendedores = []
    
    def extraer_vendedores_validos(df, nombre_columna):
        """Extrae y limpia nombres de vendedores de un DataFrame"""
        if df is None or df.empty or nombre_columna not in df.columns:
            return []
        
        vendedores = df[nombre_columna].dropna().unique()
        # Filtrar valores válidos: no nulos, no vacíos, no numéricos
        vendedores_validos = []
        for vendedor in vendedores:
            if pd.notna(vendedor):
                vendedor_str = str(vendedor).strip()
                # Excluir valores vacíos, numéricos o genéricos
                if (vendedor_str and 
                    vendedor_str.lower() not in ['nan', 'none', ''] and
                    not vendedor_str.replace('.', '').replace('-', '').isdigit()):
                    vendedores_validos.append(vendedor_str)
        
        return vendedores_validos
    
    # Extraer de facturación
    if df_fac is not None and not df_fac.empty:
        vendedores_fac = extraer_vendedores_validos(df_fac, 'Nombre Vendedor')
        todos_vendedores.extend(vendedores_fac)
    
    # Extraer de cotizaciones
    if df_cot is not None and not df_cot.empty:
        vendedores_cot = extraer_vendedores_validos(df_cot, 'Nombre Vendedor')
        todos_vendedores.extend(vendedores_cot)
    
    # Eliminar duplicados y ordenar (solo strings válidos)
    if todos_vendedores:
        todos_vendedores = sorted(list(set(todos_vendedores)))
    else:
        todos_vendedores = []
    
    # Inicializar estado de filtros de forma segura
    st.session_state.filtros = {
        'vendedores': {
            'todos': todos_vendedores,
            'seleccionados': todos_vendedores.copy()
        },
        'fechas': {
            'desde': fechas_default['periodo_actual'][0] if fechas_default else datetime.now().date(),
            'hasta': fechas_default['periodo_actual'][1] if fechas_default else datetime.now().date()
        },
        'comparativo': {
            'activo': False,
            'desde': fechas_default['periodo_anterior'][0] if fechas_default else (datetime.now() - timedelta(days=30)).date(),
            'hasta': fechas_default['periodo_anterior'][1] if fechas_default else datetime.now().date()
        }
    }
    
    # Marcar como inicializado
    st.session_state.filtros_inicializados = True


def get_filtros_state() -> Dict[str, Any]:
    """
    Obtiene el estado actual de filtros de forma segura.
    
    Returns:
        Diccionario con el estado actual de filtros
    """
    if 'filtros' not in st.session_state:
        raise RuntimeError("Estado de filtros no inicializado. Llamar a init_filtros_state() primero.")
    
    return st.session_state.filtros


def update_filtros_state(seccion: str, clave: str, valor: Any) -> None:
    """
    Actualiza una sección específica del estado de filtros de forma segura.
    
    Args:
        seccion: Sección a actualizar ('vendedores', 'fechas', 'comparativo')
        clave: Clave dentro de la sección
        valor: Nuevo valor a asignar
    """
    if 'filtros' not in st.session_state:
        raise RuntimeError("Estado de filtros no inicializado. Llamar a init_filtros_state() primero.")
    
    st.session_state.filtros[seccion][clave] = valor


def get_vendedores_seleccionados() -> List[str]:
    """
    Obtiene la lista de vendedores seleccionados.
    
    Returns:
        Lista de nombres de vendedores seleccionados
    """
    estado = get_filtros_state()
    return estado['vendedores']['seleccionados']


def get_rango_fechas_principal() -> Tuple[datetime.date, datetime.date]:
    """
    Obtiene el rango de fechas principal.
    
    Returns:
        Tupla con (fecha_desde, fecha_hasta)
    """
    estado = get_filtros_state()
    return estado['fechas']['desde'], estado['fechas']['hasta']


def get_rango_fechas_comparativo() -> Optional[Tuple[datetime.date, datetime.date]]:
    """
    Obtiene el rango de fechas comparativo si está activo.
    
    Returns:
        Tupla con (fecha_desde, fecha_hasta) o None si no está activo
    """
    estado = get_filtros_state()
    if estado['comparativo']['activo']:
        return estado['comparativo']['desde'], estado['comparativo']['hasta']
    return None


def is_comparativo_activo() -> bool:
    """
    Verifica si el comparativo está activo.
    
    Returns:
        True si el comparativo está activo, False en caso contrario
    """
    estado = get_filtros_state()
    return estado['comparativo']['activo']


def reset_filtros_state() -> None:
    """
    Resetea el estado de filtros a los valores por defecto.
    """
    if 'filtros' not in st.session_state:
        return
    
    estado = st.session_state.filtros
    
    # Resetear vendedores a todos
    estado['vendedores']['seleccionados'] = estado['vendedores']['todos'].copy()
    
    # Resetear fechas a valores por defecto
    hoy = datetime.now().date()
    primer_dia_mes = hoy.replace(day=1)
    
    estado['fechas']['desde'] = primer_dia_mes
    estado['fechas']['hasta'] = hoy
    
    # Resetear comparativo
    mes_anterior = (primer_dia_mes - timedelta(days=1)).replace(day=1)
    ultimo_dia_mes_anterior = primer_dia_mes - timedelta(days=1)
    
    estado['comparativo']['activo'] = True
    estado['comparativo']['desde'] = mes_anterior
    estado['comparativo']['hasta'] = ultimo_dia_mes_anterior


def set_mes_actual() -> None:
    """
    Establece el rango de fechas al mes actual.
    """
    hoy = datetime.now().date()
    primer_dia_mes = hoy.replace(day=1)
    
    # Actualizar session_state para que los date_input lo lean
    st.session_state['filtro_fecha_desde'] = primer_dia_mes
    st.session_state['filtro_fecha_hasta'] = hoy
    
    # Actualizar estado de filtros
    update_filtros_state('fechas', 'desde', primer_dia_mes)
    update_filtros_state('fechas', 'hasta', hoy)


def set_mes_anterior() -> None:
    """
    Establece el rango de fechas al mes anterior.
    """
    hoy = datetime.now().date()
    primer_dia_mes_actual = hoy.replace(day=1)
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
    primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
    
    # Actualizar session_state para que los date_input lo lean
    st.session_state['filtro_fecha_desde'] = primer_dia_mes_anterior
    st.session_state['filtro_fecha_hasta'] = ultimo_dia_mes_anterior
    
    # Actualizar estado de filtros
    update_filtros_state('fechas', 'desde', primer_dia_mes_anterior)
    update_filtros_state('fechas', 'hasta', ultimo_dia_mes_anterior)


def set_anio_completo() -> None:
    """
    Establece el rango de fechas al año completo.
    """
    hoy = datetime.now().date()
    primer_dia_anio = hoy.replace(month=1, day=1)
    
    # Actualizar session_state para que los date_input lo lean
    st.session_state['filtro_fecha_desde'] = primer_dia_anio
    st.session_state['filtro_fecha_hasta'] = hoy
    
    # Actualizar estado de filtros
    update_filtros_state('fechas', 'desde', primer_dia_anio)
    update_filtros_state('fechas', 'hasta', hoy)


def get_filtros_aplicados() -> Dict[str, Any]:
    """
    Obtiene un diccionario con los filtros actualmente aplicados.
    
    Returns:
        Diccionario con los filtros listos para aplicar a los datos
    """
    estado = get_filtros_state()
    
    return {
        'vendedores_seleccionados': estado['vendedores']['seleccionados'],
        'fechas_periodo': (estado['fechas']['desde'], estado['fechas']['hasta']),
        'fechas_comparativo': (estado['comparativo']['desde'], estado['comparativo']['hasta']) if estado['comparativo']['activo'] else None,
        'comparar_periodo': estado['comparativo']['activo']
    }
