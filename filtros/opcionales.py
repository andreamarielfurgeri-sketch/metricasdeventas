"""
Panel de filtros opcionales para Streamlit
Manejo seguro de filtros opcionales como comparativos sin errores de session_state
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd

from .state import (
    get_filtros_state, 
    update_filtros_state, 
    is_comparativo_activo,
    get_rango_fechas_comparativo
)


def panel_filtros_opcionales(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Panel de filtros opcionales con manejo seguro de estado.
    
    Args:
        data: Diccionario con datos necesarios
              - mostrar_comparativo: Boolean para mostrar sección de comparativo
              - expandir_por_defecto: Boolean para expandir panel por defecto
    
    Returns:
        Diccionario con los filtros opcionales seleccionados
    """
    estado = get_filtros_state()
    mostrar_comparativo = data.get('mostrar_comparativo', True)
    expandir_por_defecto = data.get('expandir_por_defecto', False)
    
    with st.expander("Filtros Opcionales", expanded=expandir_por_defecto):
        
        # Sección de comparativo
        if mostrar_comparativo:
            st.markdown("**Período Comparativo**")
            
            # Obtener estado actual del comparativo
            comparativo_activo_actual = estado['comparativo']['activo']
            
            # Widget checkbox seguro
            comparar_periodo = st.checkbox(
                "Comparar con otro período",
                value=comparativo_activo_actual,
                key="comparar_periodo_opcional",
                help="Activa para comparar con un período anterior"
            )
            
            # Actualizar estado solo si hay cambios
            if comparar_periodo != comparativo_activo_actual:
                update_filtros_state('comparativo', 'activo', comparar_periodo)
            
            # Mostrar fechas comparativas solo si está activo
            if comparar_periodo:
                _panel_fechas_comparativas()
            else:
                st.info("Comparativo inactivo")
    
    # Returnar filtros actuales
    return _get_filtros_opcionales_actuales()


def _panel_fechas_comparativas() -> None:
    """
    Panel interno para selección de fechas comparativas.
    """
    estado = get_filtros_state()
    fecha_desde_comp_actual, fecha_hasta_comp_actual = estado['comparativo']['desde'], estado['comparativo']['hasta']
    
    st.markdown("**Rango Comparativo**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha_desde_comp = st.date_input(
            "Desde (comparativo)",
            value=fecha_desde_comp_actual,
            key="fecha_desde_comparativo",
            help="Fecha de inicio del período comparativo"
        )
    
    with col2:
        fecha_hasta_comp = st.date_input(
            "Hasta (comparativo)",
            value=fecha_hasta_comp_actual,
            key="fecha_hasta_comparativo",
            help="Fecha de fin del período comparativo"
        )
    
    # Validación de fechas comparativas
    if fecha_desde_comp > fecha_hasta_comp:
        st.error("La fecha 'Desde' comparativa debe ser menor o igual a la fecha 'Hasta' comparativa")
        return
    
    # Validación que no se solape con el período principal
    fecha_desde_principal, fecha_hasta_principal = estado['fechas']['desde'], estado['fechas']['hasta']
    
    if fecha_desde_comp >= fecha_desde_principal and fecha_hasta_comp <= fecha_hasta_principal:
        st.warning("El período comparativo se solapa con el período principal")
    
    # Actualizar estado solo si hay cambios
    if (fecha_desde_comp != fecha_desde_comp_actual or 
        fecha_hasta_comp != fecha_hasta_comp_actual):
        update_filtros_state('comparativo', 'desde', fecha_desde_comp)
        update_filtros_state('comparativo', 'hasta', fecha_hasta_comp)
    
    # Sugerencias de períodos comunes
    _sugerencias_periodo_comparativo()


def _sugerencias_periodo_comparativo() -> None:
    """
    Muestra botones de sugerencias para períodos comparativos comunes.
    """
    st.markdown("**Sugerencias:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Mes Anterior", key="btn_mes_anterior_comp", help="Comparar con el mes anterior"):
            _set_periodo_comparativo_mes_anterior()
    
    with col2:
        if st.button("Mismo Mes Año Anterior", key="btn_mismo_mes_anio_anterior_comp", help="Comparar con el mismo mes del año anterior"):
            _set_periodo_comparativo_mismo_mes_anio_anterior()
    
    with col3:
        if st.button("Trimestre Anterior", key="btn_trimestre_anterior_comp", help="Comparar con el trimestre anterior"):
            _set_periodo_comparativo_trimestre_anterior()


def _set_periodo_comparativo_mes_anterior() -> None:
    """
    Establece el período comparativo al mes anterior.
    """
    estado = get_filtros_state()
    fecha_desde_principal = estado['fechas']['desde']
    
    # Calcular mes anterior
    if fecha_desde_principal.month == 1:
        mes_anterior = 12
        anio_anterior = fecha_desde_principal.year - 1
    else:
        mes_anterior = fecha_desde_principal.month - 1
        anio_anterior = fecha_desde_principal.year
    
    primer_dia_mes_anterior = datetime(anio_anterior, mes_anterior, 1).date()
    
    # Último día del mes anterior
    if mes_anterior == 12:
        primer_dia_mes_actual = datetime(anio_anterior + 1, 1, 1).date()
    else:
        primer_dia_mes_actual = datetime(anio_anterior, mes_anterior + 1, 1).date()
    
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
    
    update_filtros_state('comparativo', 'desde', primer_dia_mes_anterior)
    update_filtros_state('comparativo', 'hasta', ultimo_dia_mes_anterior)


def _set_periodo_comparativo_mismo_mes_anio_anterior() -> None:
    """
    Establece el período comparativo al mismo mes del año anterior.
    """
    estado = get_filtros_state()
    fecha_desde_principal = estado['fechas']['desde']
    
    # Mismo mes del año anterior
    primer_dia_mes_anio_anterior = datetime(
        fecha_desde_principal.year - 1, 
        fecha_desde_principal.month, 
        1
    ).date()
    
    # Último día del mismo mes del año anterior
    if fecha_desde_principal.month == 12:
        ultimo_dia_mes_anio_anterior = datetime(
            fecha_desde_principal.year - 1, 
            12, 
            31
        ).date()
    else:
        primer_dia_siguiente_mes = datetime(
            fecha_desde_principal.year - 1, 
            fecha_desde_principal.month + 1, 
            1
        ).date()
        ultimo_dia_mes_anio_anterior = primer_dia_siguiente_mes - timedelta(days=1)
    
    update_filtros_state('comparativo', 'desde', primer_dia_mes_anio_anterior)
    update_filtros_state('comparativo', 'hasta', ultimo_dia_mes_anio_anterior)


def _set_periodo_comparativo_trimestre_anterior() -> None:
    """
    Establece el período comparativo al trimestre anterior.
    """
    estado = get_filtros_state()
    fecha_desde_principal = estado['fechas']['desde']
    
    # Calcular trimestre actual
    trimestre_actual = (fecha_desde_principal.month - 1) // 3 + 1
    
    if trimestre_actual == 1:
        # Trimestre 4 del año anterior
        trimestre_anterior = 4
        anio_anterior = fecha_desde_principal.year - 1
    else:
        trimestre_anterior = trimestre_actual - 1
        anio_anterior = fecha_desde_principal.year
    
    # Primer día del trimestre anterior
    primer_mes_trimestre = (trimestre_anterior - 1) * 3 + 1
    primer_dia_trimestre_anterior = datetime(anio_anterior, primer_mes_trimestre, 1).date()
    
    # Último día del trimestre anterior
    if trimestre_anterior == 4:
        ultimo_dia_trimestre_anterior = datetime(anio_anterior, 12, 31).date()
    else:
        primer_mes_siguiente_trimestre = trimestre_anterior * 3 + 1
        if primer_mes_siguiente_trimestre > 12:
            primer_mes_siguiente_trimestre = 1
            anio_siguiente = anio_anterior + 1
        else:
            anio_siguiente = anio_anterior
        
        primer_dia_siguiente_trimestre = datetime(anio_siguiente, primer_mes_siguiente_trimestre, 1).date()
        ultimo_dia_trimestre_anterior = primer_dia_siguiente_trimestre - timedelta(days=1)
    
    update_filtros_state('comparativo', 'desde', primer_dia_trimestre_anterior)
    update_filtros_state('comparativo', 'hasta', ultimo_dia_trimestre_anterior)


def _get_filtros_opcionales_actuales() -> Dict[str, Any]:
    """
    Función interna para obtener los filtros opcionales actuales.
    
    Returns:
        Diccionario con los filtros opcionales actualmente aplicados
    """
    return {
        'vendedores_seleccionados': None,  # Se maneja en globales.py
        'fechas_periodo': None,             # Se maneja en globales.py
        'fechas_comparativo': get_rango_fechas_comparativo(),
        'comparar_periodo': is_comparativo_activo()
    }


def panel_filtros_opcionales_compacto(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Versión compacta del panel de filtros opcionales.
    
    Args:
        data: Diccionario con datos necesarios
    
    Returns:
        Diccionario con los filtros opcionales seleccionados
    """
    data['expandir_por_defecto'] = False
    return panel_filtros_opcionales(data)


def resumen_comparativo() -> None:
    """
    Muestra un resumen del estado del comparativo.
    """
    try:
        if is_comparativo_activo():
            fecha_desde_comp, fecha_hasta_comp = get_rango_fechas_comparativo()
            dias_comparativo = (fecha_hasta_comp - fecha_desde_comp).days + 1
            
            st.markdown(f"**Comparativo Activo:**")
            st.markdown(f"- Período: {fecha_desde_comp.strftime('%d/%m/%Y')} - {fecha_hasta_comp.strftime('%d/%m/%Y')}")
            st.markdown(f"- Duración: {dias_comparativo} días")
        else:
            st.markdown("**Comparativo:** Inactivo")
            
    except RuntimeError:
        st.info("No hay estado de comparativo disponible")
