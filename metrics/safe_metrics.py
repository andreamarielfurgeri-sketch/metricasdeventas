"""
Capa de Seguridad para Métricas de Ventas
Protección contra errores en producción con valores seguros y validaciones robustas
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional, Any, Union
import logging

# Importar funciones originales de ventas
from .ventas import (
    ventas_totales,
    ventas_por_periodo,
    ventas_mmaa,
    crecimiento_yoy,
    crecimiento_mom,
    ranking_vendedores,
    ticket_promedio,
    resumen_mensual,
    metricas_completas
)

# Configurar logging para debugging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def safe_number(value: Any) -> float:
    """
    Convierte cualquier valor a un número seguro.
    
    Args:
        value: Valor a convertir (puede ser None, NaN, string, etc.)
        
    Returns:
        float: Valor seguro (nunca None, siempre numérico)
    """
    try:
        if value is None:
            return 0.0
        
        if isinstance(value, str):
            value = value.strip()
            if not value or value.lower() in ['nan', 'none', 'null', '']:
                return 0.0
            return float(value)
        
        if pd.isna(value):
            return 0.0
        
        if isinstance(value, (int, float)):
            return float(value)
        
        # Intentar conversión para otros tipos
        return float(value)
        
    except (ValueError, TypeError, OverflowError) as e:
        logger.warning(f"Error convirtiendo valor {value} a número: {e}")
        return 0.0


def safe_div(numerator: Any, denominator: Any) -> float:
    """
    División segura que maneja divisiones por cero y valores inválidos.
    
    Args:
        numerator: Numerador (puede ser None, NaN, etc.)
        denominator: Denominador (puede ser None, NaN, cero)
        
    Returns:
        float: Resultado seguro de la división (nunca error)
    """
    try:
        num = safe_number(numerator)
        den = safe_number(denominator)
        
        if den == 0.0:
            return 0.0
        
        return num / den
        
    except Exception as e:
        logger.warning(f"Error en división segura {numerator}/{denominator}: {e}")
        return 0.0


def safe_df(df: Any) -> pd.DataFrame:
    """
    Asegura que siempre se devuelva un DataFrame válido.
    
    Args:
        df: DataFrame a validar (puede ser None, vacío, etc.)
        
    Returns:
        pd.DataFrame: DataFrame seguro (nunca None)
    """
    try:
        if df is None:
            return pd.DataFrame()
        
        if not isinstance(df, pd.DataFrame):
            logger.warning(f"safe_df recibió tipo {type(df)}, esperaba DataFrame")
            return pd.DataFrame()
        
        if df.empty:
            return pd.DataFrame()
        
        # Devolver copia para evitar modificaciones inesperadas
        return df.copy()
        
    except Exception as e:
        logger.warning(f"Error validando DataFrame: {e}")
        return pd.DataFrame()


def safe_date(value: Any) -> date:
    """
    Convierte cualquier valor a una fecha segura.
    
    Args:
        value: Valor a convertir (puede ser None, string, datetime, etc.)
        
    Returns:
        date: Fecha segura (nunca None)
    """
    try:
        if value is None:
            return datetime.now().date()
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, date):
            return value
        
        if isinstance(value, str):
            value = value.strip()
            if not value or value.lower() in ['nan', 'none', 'null', '']:
                return datetime.now().date()
            
            # Intentar parsear string
            return pd.to_datetime(value).date()
        
        # Intentar conversión para otros tipos
        return pd.to_datetime(value).date()
        
    except Exception as e:
        logger.warning(f"Error convirtiendo valor {value} a fecha: {e}")
        return datetime.now().date()


def safe_ventas_totales(df: Any) -> Dict[str, Union[float, int]]:
    """
    Versión segura de ventas_totales que nunca devuelve None.
    
    Args:
        df: DataFrame con datos de ventas
        
    Returns:
        Dict: Métricas seguras con valores numéricos
    """
    try:
        df_safe = safe_df(df)
        
        if df_safe.empty:
            return {
                'total_ventas': 0.0,
                'total_operaciones': 0,
                'venta_promedio': 0.0
            }
        
        # Usar función original con datos seguros
        metricas = ventas_totales(df_safe)
        
        # Asegurar que todos los valores sean seguros
        return {
            'total_ventas': safe_number(metricas.get('total_ventas', 0)),
            'total_operaciones': int(safe_number(metricas.get('total_operaciones', 0))),
            'venta_promedio': safe_number(metricas.get('venta_promedio', 0))
        }
        
    except Exception as e:
        logger.warning(f"Error en safe_ventas_totales: {e}")
        return {
            'total_ventas': 0.0,
            'total_operaciones': 0,
            'venta_promedio': 0.0
        }


def safe_ventas_por_periodo(df: Any, fecha_desde: Any, fecha_hasta: Any) -> Dict[str, Any]:
    """
    Versión segura de ventas_por_periodo.
    
    Args:
        df: DataFrame con datos de ventas
        fecha_desde: Fecha de inicio
        fecha_hasta: Fecha de fin
        
    Returns:
        Dict: Métricas seguras del período
    """
    try:
        df_safe = safe_df(df)
        desde = safe_date(fecha_desde)
        hasta = safe_date(fecha_hasta)
        
        if df_safe.empty:
            return {
                'total_ventas': 0.0,
                'total_operaciones': 0,
                'venta_promedio': 0.0,
                'dias_periodo': 0,
                'venta_promedio_diaria': 0.0
            }
        
        metricas = ventas_por_periodo(df_safe, desde, hasta)
        
        return {
            'total_ventas': safe_number(metricas.get('total_ventas', 0)),
            'total_operaciones': int(safe_number(metricas.get('total_operaciones', 0))),
            'venta_promedio': safe_number(metricas.get('venta_promedio', 0)),
            'dias_periodo': int(safe_number(metricas.get('dias_periodo', 0))),
            'venta_promedio_diaria': safe_number(metricas.get('venta_promedio_diaria', 0))
        }
        
    except Exception as e:
        logger.warning(f"Error en safe_ventas_por_periodo: {e}")
        return {
            'total_ventas': 0.0,
            'total_operaciones': 0,
            'venta_promedio': 0.0,
            'dias_periodo': 0,
            'venta_promedio_diaria': 0.0
        }


def safe_ventas_mmaa(df: Any, fecha_desde: Any, fecha_hasta: Any) -> Dict[str, Any]:
    """
    Versión segura de ventas_mmaa.
    
    Args:
        df: DataFrame con datos de ventas
        fecha_desde: Fecha de inicio
        fecha_hasta: Fecha de fin
        
    Returns:
        Dict: Métricas MMAA seguras
    """
    try:
        df_safe = safe_df(df)
        desde = safe_date(fecha_desde)
        hasta = safe_date(fecha_hasta)
        
        if df_safe.empty:
            return {
                'ventas_mmaa': 0.0,
                'operaciones_mmaa': 0,
                'venta_promedio_mmaa': 0.0,
                'crecimiento_mmaa': 0.0
            }
        
        metricas = ventas_mmaa(df_safe, desde, hasta)
        
        crecimiento = metricas.get('crecimiento_mmaa')
        if crecimiento is None:
            crecimiento = 0.0
        
        return {
            'ventas_mmaa': safe_number(metricas.get('ventas_mmaa', 0)),
            'operaciones_mmaa': int(safe_number(metricas.get('operaciones_mmaa', 0))),
            'venta_promedio_mmaa': safe_number(metricas.get('venta_promedio_mmaa', 0)),
            'crecimiento_mmaa': safe_number(crecimiento)
        }
        
    except Exception as e:
        logger.warning(f"Error en safe_ventas_mmaa: {e}")
        return {
            'ventas_mmaa': 0.0,
            'operaciones_mmaa': 0,
            'venta_promedio_mmaa': 0.0,
            'crecimiento_mmaa': 0.0
        }


def safe_crecimiento_yoy(df: Any, fecha_desde: Any, fecha_hasta: Any) -> Dict[str, Any]:
    """
    Versión segura de crecimiento_yoy.
    
    Args:
        df: DataFrame con datos de ventas
        fecha_desde: Fecha de inicio
        fecha_hasta: Fecha de fin
        
    Returns:
        Dict: Métricas YoY seguras
    """
    try:
        df_safe = safe_df(df)
        desde = safe_date(fecha_desde)
        hasta = safe_date(fecha_hasta)
        
        if df_safe.empty:
            return {
                'ventas_actual': 0.0,
                'ventas_anterior': 0.0,
                'crecimiento_yoy': 0.0,
                'variacion_absoluta': 0.0
            }
        
        metricas = crecimiento_yoy(df_safe, desde, hasta)
        
        crecimiento = metricas.get('crecimiento_yoy')
        if crecimiento is None:
            crecimiento = 0.0
        
        return {
            'ventas_actual': safe_number(metricas.get('ventas_actual', 0)),
            'ventas_anterior': safe_number(metricas.get('ventas_anterior', 0)),
            'crecimiento_yoy': safe_number(crecimiento),
            'variacion_absoluta': safe_number(metricas.get('variacion_absoluta', 0))
        }
        
    except Exception as e:
        logger.warning(f"Error en safe_crecimiento_yoy: {e}")
        return {
            'ventas_actual': 0.0,
            'ventas_anterior': 0.0,
            'crecimiento_yoy': 0.0,
            'variacion_absoluta': 0.0
        }


def safe_crecimiento_mom(df: Any) -> Dict[str, Any]:
    """
    Versión segura de crecimiento_mom.
    
    Args:
        df: DataFrame con datos de ventas
        
    Returns:
        Dict: Métricas MoM seguras
    """
    try:
        df_safe = safe_df(df)
        
        if df_safe.empty:
            return {
                'ventas_mes_actual': 0.0,
                'ventas_mes_anterior': 0.0,
                'crecimiento_mom': 0.0,
                'variacion_absoluta': 0.0
            }
        
        metricas = crecimiento_mom(df_safe)
        
        crecimiento = metricas.get('crecimiento_mom')
        if crecimiento is None:
            crecimiento = 0.0
        
        return {
            'ventas_mes_actual': safe_number(metricas.get('ventas_mes_actual', 0)),
            'ventas_mes_anterior': safe_number(metricas.get('ventas_mes_anterior', 0)),
            'crecimiento_mom': safe_number(crecimiento),
            'variacion_absoluta': safe_number(metricas.get('variacion_absoluta', 0))
        }
        
    except Exception as e:
        logger.warning(f"Error en safe_crecimiento_mom: {e}")
        return {
            'ventas_mes_actual': 0.0,
            'ventas_mes_anterior': 0.0,
            'crecimiento_mom': 0.0,
            'variacion_absoluta': 0.0
        }


def safe_ranking_vendedores(df: Any, top_n: int = 10) -> pd.DataFrame:
    """
    Versión segura de ranking_vendedores.
    
    Args:
        df: DataFrame con datos de ventas
        top_n: Número de vendedores a incluir
        
    Returns:
        pd.DataFrame: Ranking seguro (nunca None)
    """
    try:
        df_safe = safe_df(df)
        
        if df_safe.empty:
            return pd.DataFrame(columns=['vendedor', 'ventas', 'operaciones', 'venta_promedio', 'ranking'])
        
        ranking = ranking_vendedores(df_safe, top_n)
        
        if ranking is None or ranking.empty:
            return pd.DataFrame(columns=['vendedor', 'ventas', 'operaciones', 'venta_promedio', 'ranking'])
        
        # Asegurar que todas las columnas existan y sean seguras
        if 'ventas' in ranking.columns:
            ranking['ventas'] = ranking['ventas'].apply(safe_number)
        
        if 'venta_promedio' in ranking.columns:
            ranking['venta_promedio'] = ranking['venta_promedio'].apply(safe_number)
        
        return ranking
        
    except Exception as e:
        logger.warning(f"Error en safe_ranking_vendedores: {e}")
        return pd.DataFrame(columns=['vendedor', 'ventas', 'operaciones', 'venta_promedio', 'ranking'])


def safe_ticket_promedio(df: Any, por_vendedor: bool = False) -> Union[float, pd.DataFrame]:
    """
    Versión segura de ticket_promedio.
    
    Args:
        df: DataFrame con datos de ventas
        por_vendedor: Si calcular por vendedor
        
    Returns:
        Union[float, pd.DataFrame]: Ticket promedio seguro
    """
    try:
        df_safe = safe_df(df)
        
        if df_safe.empty:
            return 0.0 if not por_vendedor else pd.DataFrame()
        
        ticket = ticket_promedio(df_safe, por_vendedor)
        
        if ticket is None:
            return 0.0 if not por_vendedor else pd.DataFrame()
        
        if por_vendedor and isinstance(ticket, pd.DataFrame):
            if not ticket.empty and 'ticket_promedio' in ticket.columns:
                ticket['ticket_promedio'] = ticket['ticket_promedio'].apply(safe_number)
            return ticket
        else:
            return safe_number(ticket)
        
    except Exception as e:
        logger.warning(f"Error en safe_ticket_promedio: {e}")
        return 0.0 if not por_vendedor else pd.DataFrame()


def safe_resumen_kpis(df: Any, fecha_desde: Any, fecha_hasta: Any) -> Dict[str, Any]:
    """
    KPI consolidado seguro que nunca devuelve None ni valores inválidos.
    
    Args:
        df: DataFrame con datos de ventas
        fecha_desde: Fecha de inicio del período
        fecha_hasta: Fecha de fin del período
        
    Returns:
        Dict: Todos los KPIs seguros para uso en dashboard
    """
    try:
        df_safe = safe_df(df)
        desde = safe_date(fecha_desde)
        hasta = safe_date(fecha_hasta)
        
        if df_safe.empty:
            return {
                'ventas': 0.0,
                'operaciones': 0,
                'ticket_promedio': 0.0,
                'ventas_mmaa': 0.0,
                'crecimiento_mmaa': 0.0,
                'yoy': {
                    'ventas_actual': 0.0,
                    'ventas_anterior': 0.0,
                    'crecimiento': 0.0,
                    'variacion_absoluta': 0.0
                },
                'mom': {
                    'ventas_mes_actual': 0.0,
                    'ventas_mes_anterior': 0.0,
                    'crecimiento': 0.0,
                    'variacion_absoluta': 0.0
                },
                'ranking': pd.DataFrame(),
                'periodo': {
                    'dias': 0,
                    'venta_promedio_diaria': 0.0
                }
            }
        
        # Calcular todas las métricas seguras
        ventas_periodo = safe_ventas_por_periodo(df_safe, desde, hasta)
        ventas_mmaa_data = safe_ventas_mmaa(df_safe, desde, hasta)
        yoy_data = safe_crecimiento_yoy(df_safe, desde, hasta)
        mom_data = safe_crecimiento_mom(df_safe)
        ranking_data = safe_ranking_vendedores(df_safe, top_n=10)
        
        return {
            'ventas': ventas_periodo['total_ventas'],
            'operaciones': ventas_periodo['total_operaciones'],
            'ticket_promedio': ventas_periodo['venta_promedio'],
            'ventas_mmaa': ventas_mmaa_data['ventas_mmaa'],
            'crecimiento_mmaa': ventas_mmaa_data['crecimiento_mmaa'],
            'yoy': {
                'ventas_actual': yoy_data['ventas_actual'],
                'ventas_anterior': yoy_data['ventas_anterior'],
                'crecimiento': yoy_data['crecimiento_yoy'],
                'variacion_absoluta': yoy_data['variacion_absoluta']
            },
            'mom': {
                'ventas_mes_actual': mom_data['ventas_mes_actual'],
                'ventas_mes_anterior': mom_data['ventas_mes_anterior'],
                'crecimiento': mom_data['crecimiento_mom'],
                'variacion_absoluta': mom_data['variacion_absoluta']
            },
            'ranking': ranking_data,
            'periodo': {
                'dias': ventas_periodo['dias_periodo'],
                'venta_promedio_diaria': ventas_periodo['venta_promedio_diaria']
            }
        }
        
    except Exception as e:
        logger.error(f"Error crítico en safe_resumen_kpis: {e}")
        # Retornar valores seguros incluso en caso de error crítico
        return {
            'ventas': 0.0,
            'operaciones': 0,
            'ticket_promedio': 0.0,
            'ventas_mmaa': 0.0,
            'crecimiento_mmaa': 0.0,
            'yoy': {
                'ventas_actual': 0.0,
                'ventas_anterior': 0.0,
                'crecimiento': 0.0,
                'variacion_absoluta': 0.0
            },
            'mom': {
                'ventas_mes_actual': 0.0,
                'ventas_mes_anterior': 0.0,
                'crecimiento': 0.0,
                'variacion_absoluta': 0.0
            },
            'ranking': pd.DataFrame(),
            'periodo': {
                'dias': 0,
                'venta_promedio_diaria': 0.0
            }
        }


# Funciones de utilidad para validación específica
def safe_crecimiento_color(crecimiento: Any) -> str:
    """
    Determina color seguro para indicadores de crecimiento.
    
    Args:
        crecimiento: Valor de crecimiento (puede ser None, etc.)
        
    Returns:
        str: Color seguro ('green', 'red', 'orange')
    """
    try:
        valor = safe_number(crecimiento)
        
        if valor > 0:
            return 'green'
        elif valor < 0:
            return 'red'
        else:
            return 'orange'
            
    except Exception:
        return 'orange'


def safe_format_crecimiento(crecimiento: Any) -> str:
    """
    Formatea crecimiento de manera segura.
    
    Args:
        crecimiento: Valor de crecimiento
        
    Returns:
        str: Texto formateado seguro
    """
    try:
        valor = safe_number(crecimiento)
        return f"{valor:.1f}%"
    except Exception:
        return "0.0%"


def safe_validate_dataframe(df: Any, required_columns: List[str]) -> bool:
    """
    Valida que un DataFrame tenga las columnas requeridas.
    
    Args:
        df: DataFrame a validar
        required_columns: Lista de columnas requeridas
        
    Returns:
        bool: True si es válido, False si no
    """
    try:
        df_safe = safe_df(df)
        
        if df_safe.empty:
            return False
        
        missing_columns = [col for col in required_columns if col not in df_safe.columns]
        
        if missing_columns:
            logger.warning(f"Columnas faltantes: {missing_columns}")
            return False
        
        return True
        
    except Exception as e:
        logger.warning(f"Error validando DataFrame: {e}")
        return False
