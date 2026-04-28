"""
Panel de filtros globales para Streamlit
Manejo seguro de widgets globales sin errores de session_state
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import pandas as pd

from .state import (
    get_filtros_state, 
    update_filtros_state, 
    get_vendedores_seleccionados,
    get_rango_fechas_principal,
    set_mes_actual,
    set_mes_anterior,
    set_anio_completo,
    reset_filtros_state
)


def panel_filtros_globales(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Panel principal de filtros globales con manejo seguro de estado.
    
    Args:
        data: Diccionario con datos necesarios
              - df_fac: DataFrame de facturación
              - df_cot: DataFrame de cotizaciones
              - mostrar_botones_rapidos: Boolean para mostrar botones de acceso rápido
    
    Returns:
        Diccionario con los filtros seleccionados
    """
    estado = get_filtros_state()
    mostrar_botones_rapidos = data.get('mostrar_botones_rapidos', True)
    
    st.markdown("### Filtros Globales")
    
    # Sección de vendedores
    with st.container():
        st.markdown("**Vendedores**")
        
        # Obtener valores del estado para usar como default
        vendedores_seleccionados_actual = estado['vendedores']['seleccionados']
        todos_vendedores = estado['vendedores']['todos']
        
        # Widget multiselect seguro - usa el estado actual como default
        vendedores_seleccionados = st.multiselect(
            "Seleccionar vendedores",
            options=todos_vendedores,
            default=vendedores_seleccionados_actual,
            key="vendedores_globales_multiselect",
            help="Selecciona los vendedores a incluir en el análisis"
        )
        
        # Actualizar estado solo si hay cambios (evita modificaciones innecesarias)
        if vendedores_seleccionados != vendedores_seleccionados_actual:
            update_filtros_state('vendedores', 'seleccionados', vendedores_seleccionados)
        
        # Si no se selecciona ningún vendedor, mostrar todos
        if not vendedores_seleccionados:
            if vendedores_seleccionados_actual != todos_vendedores:
                update_filtros_state('vendedores', 'seleccionados', todos_vendedores)
            st.info("Mostrando todos los vendedores")
    
    # Sección de fechas
    with st.container():
        st.markdown("**Período Principal**")
        
        # Obtener valores actuales del estado
        fecha_desde_actual, fecha_hasta_actual = get_rango_fechas_principal()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Asegurar que las fechas estén en session_state para que los botones rápidos funcionen
            if 'filtro_fecha_desde' not in st.session_state:
                st.session_state['filtro_fecha_desde'] = fecha_desde_actual
            if 'filtro_fecha_hasta' not in st.session_state:
                st.session_state['filtro_fecha_hasta'] = fecha_hasta_actual
            
            fecha_desde = st.date_input(
                "Desde",
                value=st.session_state['filtro_fecha_desde'],
                key='filtro_fecha_desde',
                help="Fecha de inicio del período de análisis"
            )
        
        with col2:
            fecha_hasta = st.date_input(
                "Hasta",
                value=st.session_state['filtro_fecha_hasta'],
                key='filtro_fecha_hasta',
                help="Fecha de fin del período de análisis"
            )
        
        # Validación de fechas
        if fecha_desde > fecha_hasta:
            st.error("La fecha 'Desde' debe ser menor o igual a la fecha 'Hasta'")
            return _get_filtros_actuales()
        
        # Actualizar estado solo si hay cambios
        if fecha_desde != fecha_desde_actual or fecha_hasta != fecha_hasta_actual:
            update_filtros_state('fechas', 'desde', fecha_desde)
            update_filtros_state('fechas', 'hasta', fecha_hasta)
    
    # Botones de acceso rápido (opcionales)
    if mostrar_botones_rapidos:
        st.markdown("**Acceso Rápido**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Mes Actual", key="btn_mes_actual_global", help="Establecer período al mes actual"):
                set_mes_actual()
                st.rerun()
        
        with col2:
            if st.button("Mes Anterior", key="btn_mes_anterior_global", help="Establecer período al mes anterior"):
                set_mes_anterior()
                st.rerun()
        
        with col3:
            if st.button("Año Completo", key="btn_anio_completo_global", help="Establecer período al año completo"):
                set_anio_completo()
                st.rerun()
        
        with col4:
            if st.button("Resetear", key="btn_reset_global", help="Resetear todos los filtros a valores por defecto"):
                reset_filtros_state()
                st.rerun()
    
    # Returnar filtros actuales
    return _get_filtros_actuales()


def _get_filtros_actuales() -> Dict[str, Any]:
    """
    Función interna para obtener los filtros actuales del estado.
    
    Returns:
        Diccionario con los filtros actualmente aplicados
    """
    return {
        'vendedores_seleccionados': get_vendedores_seleccionados(),
        'fechas_periodo': get_rango_fechas_principal(),
        'fechas_comparativo': None,  # Se maneja en opcionales.py
        'comparar_periodo': False     # Se maneja en opcionales.py
    }


def panel_filtros_globales_compacto(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Versión compacta del panel de filtros globales para espacios reducidos.
    
    Args:
        data: Diccionario con datos necesarios
    
    Returns:
        Diccionario con los filtros seleccionados
    """
    estado = get_filtros_state()
    
    with st.expander("Filtros Globales", expanded=False):
        return panel_filtros_globales(data)


def resumen_filtros_aplicados() -> None:
    """
    Muestra un resumen visual de los filtros actualmente aplicados.
    """
    try:
        estado = get_filtros_state()
        
        st.markdown("**Filtros Aplicados:**")
        
        # Vendedores
        vendedores_sel = estado['vendedores']['seleccionados']
        total_vendedores = len(estado['vendedores']['todos'])
        
        if len(vendedores_sel) == total_vendedores:
            st.markdown(f"**Vendedores:** Todos ({total_vendedores})")
        else:
            st.markdown(f"**Vendedores:** {len(vendedores_sel)} de {total_vendedores}")
        
        # Fechas
        fecha_desde, fecha_hasta = get_rango_fechas_principal()
        st.markdown(f"**Período:** {fecha_desde.strftime('%d/%m/%Y')} - {fecha_hasta.strftime('%d/%m/%Y')}")
        
        # Comparativo
        if estado['comparativo']['activo']:
            fecha_desde_comp, fecha_hasta_comp = estado['comparativo']['desde'], estado['comparativo']['hasta']
            st.markdown(f"**Comparativo:** {fecha_desde_comp.strftime('%d/%m/%Y')} - {fecha_hasta_comp.strftime('%d/%m/%Y')}")
        else:
            st.markdown("**Comparativo:** Inactivo")
            
    except RuntimeError:
        st.info("No hay filtros aplicados")
