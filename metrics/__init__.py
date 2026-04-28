"""
Módulo de métricas para análisis de datos de ventas
Funciones robustas tipo Power BI para cálculos de ventas y crecimiento
"""

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

from .safe_metrics import (
    safe_number,
    safe_div,
    safe_df,
    safe_date,
    safe_ventas_totales,
    safe_ventas_por_periodo,
    safe_ventas_mmaa,
    safe_crecimiento_yoy,
    safe_crecimiento_mom,
    safe_ranking_vendedores,
    safe_ticket_promedio,
    safe_resumen_kpis,
    safe_crecimiento_color,
    safe_format_crecimiento,
    safe_validate_dataframe
)

__all__ = [
    # Funciones originales
    'ventas_totales',
    'ventas_por_periodo',
    'ventas_mmaa',
    'crecimiento_yoy',
    'crecimiento_mom',
    'ranking_vendedores',
    'ticket_promedio',
    'resumen_mensual',
    'metricas_completas',
    
    # Funciones seguras
    'safe_number',
    'safe_div',
    'safe_df',
    'safe_date',
    'safe_ventas_totales',
    'safe_ventas_por_periodo',
    'safe_ventas_mmaa',
    'safe_crecimiento_yoy',
    'safe_crecimiento_mom',
    'safe_ranking_vendedores',
    'safe_ticket_promedio',
    'safe_resumen_kpis',
    'safe_crecimiento_color',
    'safe_format_crecimiento',
    'safe_validate_dataframe'
]
