"""
Módulo de Métricas de Ventas tipo Power BI
Cálculos robustos y confiables para análisis de datos de ventas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union


def ventas_totales(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcula métricas totales de ventas
    
    Args:
        df: DataFrame con columnas 'ventas' y 'fecha'
        
    Returns:
        Diccionario con métricas totales
    """
    if df is None or df.empty or 'ventas' not in df.columns:
        return {
            'total_ventas': 0.0,
            'total_operaciones': 0,
            'venta_promedio': 0.0
        }
    
    # Filtrar solo ventas válidas
    df_valido = df.dropna(subset=['ventas'])
    
    if df_valido.empty:
        return {
            'total_ventas': 0.0,
            'total_operaciones': 0,
            'venta_promedio': 0.0
        }
    
    total_ventas = df_valido['ventas'].sum()
    total_operaciones = len(df_valido)
    venta_promedio = total_ventas / total_operaciones if total_operaciones > 0 else 0.0
    
    return {
        'total_ventas': float(total_ventas),
        'total_operaciones': int(total_operaciones),
        'venta_promedio': float(venta_promedio)
    }


def ventas_por_periodo(df: pd.DataFrame, fecha_desde: datetime.date, fecha_hasta: datetime.date) -> Dict[str, Any]:
    """
    Calcula métricas de ventas para un período específico
    
    Args:
        df: DataFrame con columnas 'fecha' y 'ventas'
        fecha_desde: Fecha de inicio del período
        fecha_hasta: Fecha de fin del período
        
    Returns:
        Diccionario con métricas del período
    """
    if df is None or df.empty:
        return {
            'total_ventas': 0.0,
            'total_operaciones': 0,
            'venta_promedio': 0.0,
            'dias_periodo': 0,
            'venta_promedio_diaria': 0.0
        }
    
    # Filtrar por período
    df_filtrado = df.copy()
    
    # Asegurar que la columna fecha esté en datetime
    if not pd.api.types.is_datetime64_any_dtype(df_filtrado['fecha']):
        df_filtrado['fecha'] = pd.to_datetime(df_filtrado['fecha'])
    
    # Filtrar por rango de fechas
    mask = (df_filtrado['fecha'].dt.date >= fecha_desde) & (df_filtrado['fecha'].dt.date <= fecha_hasta)
    df_periodo = df_filtrado[mask]
    
    if df_periodo.empty:
        return {
            'total_ventas': 0.0,
            'total_operaciones': 0,
            'venta_promedio': 0.0,
            'dias_periodo': 0,
            'venta_promedio_diaria': 0.0
        }
    
    # Calcular métricas básicas
    metricas_basicas = ventas_totales(df_periodo)
    
    # Calcular días del período
    dias_periodo = (fecha_hasta - fecha_desde).days + 1
    venta_promedio_diaria = metricas_basicas['total_ventas'] / dias_periodo if dias_periodo > 0 else 0.0
    
    return {
        **metricas_basicas,
        'dias_periodo': dias_periodo,
        'venta_promedio_diaria': float(venta_promedio_diaria)
    }


def ventas_mmaa(df: pd.DataFrame, fecha_desde: datetime.date, fecha_hasta: datetime.date) -> Dict[str, float]:
    """
    Calcula métricas de Mes Mismo Año Anterior (MMAA)
    
    Args:
        df: DataFrame con columnas 'fecha' y 'ventas'
        fecha_desde: Fecha de inicio del período actual
        fecha_hasta: Fecha de fin del período actual
        
    Returns:
        Diccionario con métricas MMAA
    """
    if df is None or df.empty:
        return {
            'ventas_mmaa': 0.0,
            'operaciones_mmaa': 0,
            'venta_promedio_mmaa': 0.0,
            'crecimiento_mmaa': None
        }
    
    # Calcular fechas del mismo período del año anterior
    fecha_desde_mmaa = fecha_desde.replace(year=fecha_desde.year - 1)
    fecha_hasta_mmaa = fecha_hasta.replace(year=fecha_hasta.year - 1)
    
    # Obtener métricas del período actual
    metricas_actuales = ventas_por_periodo(df, fecha_desde, fecha_hasta)
    
    # Obtener métricas del período MMAA
    metricas_mmaa = ventas_por_periodo(df, fecha_desde_mmaa, fecha_hasta_mmaa)
    
    # Calcular crecimiento
    ventas_actuales = metricas_actuales['total_ventas']
    ventas_mmaa = metricas_mmaa['total_ventas']
    
    crecimiento_mmaa = None
    if ventas_mmaa != 0:
        crecimiento_mmaa = ((ventas_actuales - ventas_mmaa) / ventas_mmaa) * 100
    
    return {
        'ventas_mmaa': float(ventas_mmaa),
        'operaciones_mmaa': metricas_mmaa['total_operaciones'],
        'venta_promedio_mmaa': float(metricas_mmaa['venta_promedio']),
        'crecimiento_mmaa': float(crecimiento_mmaa) if crecimiento_mmaa is not None else None
    }


def crecimiento_yoy(df: pd.DataFrame, fecha_desde: datetime.date, fecha_hasta: datetime.date) -> Dict[str, Any]:
    """
    Calcula crecimiento Year-over-Year (YoY)
    
    Args:
        df: DataFrame con columnas 'fecha' y 'ventas'
        fecha_desde: Fecha de inicio del período
        fecha_hasta: Fecha de fin del período
        
    Returns:
        Diccionario con métricas de crecimiento YoY
    """
    if df is None or df.empty:
        return {
            'ventas_actual': 0.0,
            'ventas_anterior': 0.0,
            'crecimiento_yoy': None,
            'variacion_absoluta': 0.0
        }
    
    # Obtener métricas del período actual
    metricas_actuales = ventas_por_periodo(df, fecha_desde, fecha_hasta)
    
    # Calcular fechas del año anterior (mismo período)
    fecha_desde_anterior = fecha_desde.replace(year=fecha_desde.year - 1)
    fecha_hasta_anterior = fecha_hasta.replace(year=fecha_hasta.year - 1)
    
    # Obtener métricas del período anterior
    metricas_anterior = ventas_por_periodo(df, fecha_desde_anterior, fecha_hasta_anterior)
    
    ventas_actual = metricas_actuales['total_ventas']
    ventas_anterior = metricas_anterior['total_ventas']
    
    # Calcular crecimiento YoY
    crecimiento_yoy = None
    if ventas_anterior != 0:
        crecimiento_yoy = ((ventas_actual - ventas_anterior) / ventas_anterior) * 100
    
    variacion_absoluta = ventas_actual - ventas_anterior
    
    return {
        'ventas_actual': float(ventas_actual),
        'ventas_anterior': float(ventas_anterior),
        'crecimiento_yoy': float(crecimiento_yoy) if crecimiento_yoy is not None else None,
        'variacion_absoluta': float(variacion_absoluta)
    }


def crecimiento_mom(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula crecimiento Month-over-Month (MoM)
    
    Args:
        df: DataFrame con columnas 'fecha' y 'ventas'
        
    Returns:
        Diccionario con métricas de crecimiento MoM
    """
    if df is None or df.empty:
        return {
            'ventas_mes_actual': 0.0,
            'ventas_mes_anterior': 0.0,
            'crecimiento_mom': None,
            'variacion_absoluta': 0.0
        }
    
    # Asegurar que la columna fecha esté en datetime
    df_copy = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_copy['fecha']):
        df_copy['fecha'] = pd.to_datetime(df_copy['fecha'])
    
    # Obtener el mes más reciente con datos
    fecha_max = df_copy['fecha'].max()
    mes_actual = fecha_max.replace(day=1)
    
    # Calcular mes anterior
    if mes_actual.month == 1:
        mes_anterior = mes_actual.replace(year=mes_actual.year - 1, month=12)
    else:
        mes_anterior = mes_actual.replace(month=mes_actual.month - 1)
    
    # Obtener último día de cada mes
    if mes_actual.month == 12:
        ultimo_dia_actual = datetime(mes_actual.year, 12, 31).date()
    else:
        ultimo_dia_actual = (datetime(mes_actual.year, mes_actual.month + 1, 1) - timedelta(days=1)).date()
    
    if mes_anterior.month == 12:
        ultimo_dia_anterior = datetime(mes_anterior.year, 12, 31).date()
    else:
        ultimo_dia_anterior = (datetime(mes_anterior.year, mes_anterior.month + 1, 1) - timedelta(days=1)).date()
    
    # Calcular métricas de cada mes
    metricas_mes_actual = ventas_por_periodo(df, mes_actual.date(), ultimo_dia_actual)
    metricas_mes_anterior = ventas_por_periodo(df, mes_anterior.date(), ultimo_dia_anterior)
    
    ventas_mes_actual = metricas_mes_actual['total_ventas']
    ventas_mes_anterior = metricas_mes_anterior['total_ventas']
    
    # Calcular crecimiento MoM
    crecimiento_mom = None
    if ventas_mes_anterior != 0:
        crecimiento_mom = ((ventas_mes_actual - ventas_mes_anterior) / ventas_mes_anterior) * 100
    
    variacion_absoluta = ventas_mes_actual - ventas_mes_anterior
    
    return {
        'ventas_mes_actual': float(ventas_mes_actual),
        'ventas_mes_anterior': float(ventas_mes_anterior),
        'crecimiento_mom': float(crecimiento_mom) if crecimiento_mom is not None else None,
        'variacion_absoluta': float(variacion_absoluta)
    }


def ranking_vendedores(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Genera ranking de vendedores por ventas
    
    Args:
        df: DataFrame con columnas 'vendedor' y 'ventas'
        top_n: Número de vendedores a incluir en el ranking
        
    Returns:
        DataFrame con ranking de vendedores
    """
    if df is None or df.empty or 'vendedor' not in df.columns or 'ventas' not in df.columns:
        return pd.DataFrame(columns=['vendedor', 'ventas', 'operaciones', 'venta_promedio', 'ranking'])
    
    # Agrupar por vendedor
    ranking = df.groupby('vendedor').agg({
        'ventas': ['sum', 'count', 'mean']
    }).round(2)
    
    # Aplanar columnas multi-nivel
    ranking.columns = ['ventas', 'operaciones', 'venta_promedio']
    ranking = ranking.reset_index()
    
    # Ordenar por ventas descendente
    ranking = ranking.sort_values('ventas', ascending=False)
    
    # Agregar ranking
    ranking['ranking'] = range(1, len(ranking) + 1)
    
    # Limitar a top_n vendedores
    if len(ranking) > top_n:
        ranking = ranking.head(top_n)
    
    # Convertir tipos de datos
    ranking['ventas'] = ranking['ventas'].astype(float)
    ranking['operaciones'] = ranking['operaciones'].astype(int)
    ranking['venta_promedio'] = ranking['venta_promedio'].astype(float)
    
    return ranking


def ticket_promedio(df: pd.DataFrame, por_vendedor: bool = False) -> Union[float, pd.DataFrame]:
    """
    Calcula ticket promedio de ventas
    
    Args:
        df: DataFrame con columnas 'ventas'
        por_vendedor: Si True, calcula ticket promedio por vendedor
        
    Returns:
        Ticket promedio general o DataFrame con ticket promedio por vendedor
    """
    if df is None or df.empty or 'ventas' not in df.columns:
        return 0.0 if not por_vendedor else pd.DataFrame()
    
    # Filtrar ventas válidas
    df_valido = df.dropna(subset=['ventas'])
    
    if df_valido.empty:
        return 0.0 if not por_vendedor else pd.DataFrame()
    
    if not por_vendedor:
        # Ticket promedio general
        return float(df_valido['ventas'].mean())
    
    else:
        # Ticket promedio por vendedor
        if 'vendedor' not in df_valido.columns:
            return pd.DataFrame()
        
        ticket_vendedor = df_valido.groupby('vendedor')['ventas'].mean().round(2)
        ticket_vendedor = ticket_vendedor.reset_index()
        ticket_vendedor.columns = ['vendedor', 'ticket_promedio']
        ticket_vendedor = ticket_vendedor.sort_values('ticket_promedio', ascending=False)
        
        return ticket_vendedor


def resumen_mensual(df: pd.DataFrame, meses: int = 12) -> pd.DataFrame:
    """
    Genera resumen mensual de ventas
    
    Args:
        df: DataFrame con columnas 'fecha' y 'ventas'
        meses: Número de meses a incluir en el resumen
        
    Returns:
        DataFrame con resumen mensual
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=['mes', 'año', 'ventas', 'operaciones', 'ticket_promedio'])
    
    # Asegurar que la columna fecha esté en datetime
    df_copy = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_copy['fecha']):
        df_copy['fecha'] = pd.to_datetime(df_copy['fecha'])
    
    # Extraer año y mes
    df_copy['año'] = df_copy['fecha'].dt.year
    df_copy['mes'] = df_copy['fecha'].dt.month
    
    # Agrupar por mes y año
    resumen = df_copy.groupby(['año', 'mes']).agg({
        'ventas': ['sum', 'count', 'mean']
    }).round(2)
    
    # Aplanar columnas
    resumen.columns = ['ventas', 'operaciones', 'ticket_promedio']
    resumen = resumen.reset_index()
    
    # Crear columna de período formateado
    resumen['periodo'] = resumen['mes'].astype(str).str.zfill(2) + '/' + resumen['año'].astype(str)
    
    # Ordenar cronológicamente
    resumen = resumen.sort_values(['año', 'mes'])
    
    # Limitar a los últimos N meses
    if len(resumen) > meses:
        resumen = resumen.tail(meses)
    
    # Reordenar columnas
    resumen = resumen[['periodo', 'año', 'mes', 'ventas', 'operaciones', 'ticket_promedio']]
    
    return resumen


def metricas_completas(df: pd.DataFrame, fecha_desde: datetime.date, fecha_hasta: datetime.date) -> Dict[str, Any]:
    """
    Calcula todas las métricas importantes para un período
    
    Args:
        df: DataFrame con columnas 'fecha', 'vendedor', 'ventas'
        fecha_desde: Fecha de inicio del período
        fecha_hasta: Fecha de fin del período
        
    Returns:
        Diccionario con todas las métricas calculadas
    """
    if df is None or df.empty:
        return {
            'periodo': {'ventas': 0.0, 'operaciones': 0, 'ticket_promedio': 0.0},
            'yoy': {'crecimiento': None, 'variacion_absoluta': 0.0},
            'mmaa': {'crecimiento': None, 'variacion_absoluta': 0.0},
            'mom': {'crecimiento': None, 'variacion_absoluta': 0.0},
            'ranking': pd.DataFrame(),
            'resumen_mensual': pd.DataFrame()
        }
    
    # Métricas del período
    metricas_periodo = ventas_por_periodo(df, fecha_desde, fecha_hasta)
    
    # Crecimiento YoY
    metricas_yoy = crecimiento_yoy(df, fecha_desde, fecha_hasta)
    
    # Crecimiento MMAA
    metricas_mmaa = ventas_mmaa(df, fecha_desde, fecha_hasta)
    
    # Crecimiento MoM
    metricas_mom = crecimiento_mom(df)
    
    # Ranking de vendedores
    ranking_vended = ranking_vendedores(df, top_n=10)
    
    # Resumen mensual
    resumen_mensual_data = resumen_mensual(df, meses=12)
    
    return {
        'periodo': metricas_periodo,
        'yoy': {
            'crecimiento': metricas_yoy['crecimiento_yoy'],
            'variacion_absoluta': metricas_yoy['variacion_absoluta']
        },
        'mmaa': {
            'crecimiento': metricas_mmaa['crecimiento_mmaa'],
            'variacion_absoluta': metricas_mmaa['ventas_mmaa'] - metricas_periodo['total_ventas']
        },
        'mom': {
            'crecimiento': metricas_mom['crecimiento_mom'],
            'variacion_absoluta': metricas_mom['variacion_absoluta']
        },
        'ranking': ranking_vended,
        'resumen_mensual': resumen_mensual_data
    }
