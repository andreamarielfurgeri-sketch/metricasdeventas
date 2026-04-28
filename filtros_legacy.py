"""
Funciones legacy de filtros que se mantienen para compatibilidad
Estas funciones no usan session_state directamente y son seguras
"""

import pandas as pd
from datetime import datetime, timedelta


def aplicar_filtros(df_total, vendedores_seleccionados, fechas_periodo):
    """Aplica filtros de vendedores y fechas al DataFrame unificado"""
    if df_total is None:
        return None
    
    df_filtrado = df_total.copy()
    
    # Filtrar por vendedores
    if vendedores_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['vendedor'].isin(vendedores_seleccionados)]
    
    # Filtrar por fechas
    if fechas_periodo and 'Fecha' in df_filtrado.columns:
        fecha_desde, fecha_hasta = fechas_periodo
        
        # Convertir fechas del filtro a datetime si no lo son
        if not isinstance(fecha_desde, pd.Timestamp):
            fecha_desde = pd.to_datetime(fecha_desde)
        if not isinstance(fecha_hasta, pd.Timestamp):
            fecha_hasta = pd.to_datetime(fecha_hasta)
        
        # Asegurar que la columna Fecha esté en datetime
        if not pd.api.types.is_datetime64_any_dtype(df_filtrado['Fecha']):
            df_filtrado['Fecha'] = pd.to_datetime(df_filtrado['Fecha'])
        
        # Aplicar filtro de rango de fechas (inclusive)
        df_filtrado = df_filtrado[
            (df_filtrado['Fecha'] >= fecha_desde) &
            (df_filtrado['Fecha'] <= fecha_hasta)
        ]
    
    return df_filtrado


def separar_datos_filtrados(df_filtrado):
    """Separa el DataFrame unificado en facturación y cotizaciones"""
    df_fac_filtrado = None
    df_cot_filtrado = None
    
    if df_filtrado is not None and not df_filtrado.empty:
        # Separar facturas
        df_fac_filtrado = df_filtrado[df_filtrado['tipo'] == 'factura'].copy()
        
        # Renombrar columnas al formato original
        df_fac_filtrado = df_fac_filtrado.rename(columns={
            'Fecha': 'Fecha de emisión',
            'vendedor': 'Nombre Vendedor',
            'monto_sin_imp': 'Total sin Impuestos',
            'monto_con_imp': 'Total'
        })
        
        # Separar cotizaciones
        df_cot_filtrado = df_filtrado[df_filtrado['tipo'] == 'cotizacion'].copy()
        
        # Renombrar columnas al formato original
        df_cot_filtrado = df_cot_filtrado.rename(columns={
            'Fecha': 'Fecha emisión',
            'vendedor': 'Nombre Vendedor',
            'monto_sin_imp': 'Total sin Impuestos (CTE)',
            'monto_con_imp': 'Total (CTE)'
        })
    
    return df_fac_filtrado, df_cot_filtrado


def normalizar_datos(df_fac, df_cot):
    """Normaliza y unifica los datos de facturación y cotizaciones"""
    df_total = None
    
    # Normalizar facturación
    if df_fac is not None and not df_fac.empty:
        df_fac_norm = df_fac.copy()
        df_fac_norm['Nombre Vendedor'] = df_fac_norm['Nombre Vendedor'].astype(str)
        df_fac_norm['Fecha de emisión'] = pd.to_datetime(df_fac_norm['Fecha de emisión'])
        
        # Asegurar que los montos sean float
        for col in ['Total sin Impuestos', 'Total de Impuestos', 'Total']:
            if col in df_fac_norm.columns:
                df_fac_norm[col] = pd.to_numeric(df_fac_norm[col], errors='coerce')
        
        df_fac_norm['tipo'] = 'factura'
        
        # Renombrar columnas para unificación
        df_fac_norm = df_fac_norm.rename(columns={
            'Fecha de emisión': 'Fecha',
            'Nombre Vendedor': 'vendedor',
            'Total sin Impuestos': 'monto_sin_imp',
            'Total': 'monto_con_imp'
        })
        
        df_total = df_fac_norm
    
    # Normalizar cotizaciones
    if df_cot is not None and not df_cot.empty:
        df_cot_norm = df_cot.copy()
        df_cot_norm['Nombre Vendedor'] = df_cot_norm['Nombre Vendedor'].astype(str)
        df_cot_norm['Fecha emisión'] = pd.to_datetime(df_cot_norm['Fecha emisión'])
        
        # Asegurar que los montos sean float
        for col in ['Total sin Impuestos (CTE)', 'Total (CTE)']:
            if col in df_cot_norm.columns:
                df_cot_norm[col] = pd.to_numeric(df_cot_norm[col], errors='coerce')
        
        df_cot_norm['tipo'] = 'cotizacion'
        
        # Renombrar columnas para unificación
        df_cot_norm = df_cot_norm.rename(columns={
            'Fecha emisión': 'Fecha',
            'Nombre Vendedor': 'vendedor',
            'Total sin Impuestos (CTE)': 'monto_sin_imp',
            'Total (CTE)': 'monto_con_imp'
        })
        
        if df_total is not None:
            df_total = pd.concat([df_total, df_cot_norm], ignore_index=True)
        else:
            df_total = df_cot_norm
    
    return df_total


def obtener_fechas_default():
    """Obtiene fechas por defecto para el período actual y anterior"""
    hoy = datetime.now()
    
    # Período actual (mes actual)
    primer_dia_mes_actual = hoy.replace(day=1)
    
    # Período anterior (mes anterior)
    if hoy.month == 1:
        mes_anterior = 12
        anio_anterior = hoy.year - 1
    else:
        mes_anterior = hoy.month - 1
        anio_anterior = hoy.year
    
    primer_dia_mes_anterior = datetime(anio_anterior, mes_anterior, 1).date()
    
    if mes_anterior == 12:
        ultimo_dia_mes_anterior = datetime(anio_anterior, 12, 31).date()
    else:
        primer_dia_mes_actual_anterior = datetime(anio_anterior, mes_anterior + 1, 1).date()
        ultimo_dia_mes_anterior = primer_dia_mes_actual_anterior - timedelta(days=1)
    
    return {
        'periodo_actual': (primer_dia_mes_actual.date(), hoy.date()),
        'periodo_anterior': (primer_dia_mes_anterior, ultimo_dia_mes_anterior)
    }


def obtener_vendedores(df_fac, df_cot):
    """Obtiene la lista completa de vendedores de ambos dataframes"""
    todos_vendedores = []
    
    if df_fac is not None and not df_fac.empty:
        vendedores_fac = df_fac['Nombre Vendedor'].unique().tolist()
        todos_vendedores.extend(vendedores_fac)
    
    if df_cot is not None and not df_cot.empty:
        vendedores_cot = df_cot['Nombre Vendedor'].unique().tolist()
        todos_vendedores.extend(vendedores_cot)
    
    # Eliminar duplicados y ordenar
    return sorted(list(set(todos_vendedores)))


def objetivos_vendedores_sidebar():
    """Panel de objetivos mensuales en sidebar"""
    import streamlit as st
    
    st.sidebar.markdown("### Objetivos Mensuales")
    
    # Objetivos individuales
    objetivos = {}
    vendedores_objetivo = ['Betty', 'Juan G', 'Cesar', 'Francisco', 'Ferrari Alan', 'Leandro', 'CORP Alejandro']
    
    for vendedor in vendedores_objetivo:
        objetivos[vendedor] = st.sidebar.number_input(
            f"Objetivo {vendedor} (ARS S/Imp)",
            min_value=0,
            value=100000000,
            step=1000000,
            format="%d",
            key=f"objetivo_{vendedor}"
        )
    
    # Objetivos grupales
    st.sidebar.markdown("**Objetivos Grupales**")
    objetivo_minimo = st.sidebar.number_input(
        "Objetivo Mínimo Grupal (ARS S/Imp)",
        min_value=0,
        value=700000000,
        step=10000000,
        format="%d",
        key="objetivo_minimo_grupal"
    )
    
    objetivo_ideal = st.sidebar.number_input(
        "Objetivo Ideal Grupal (ARS S/Imp)",
        min_value=0,
        value=1000000000,
        step=10000000,
        format="%d",
        key="objetivo_ideal_grupal"
    )
    
    return objetivos, objetivo_minimo, objetivo_ideal
