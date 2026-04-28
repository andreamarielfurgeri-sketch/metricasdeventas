import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Importar módulos
from estilos import inject_css, header_footer, metric_card, fmt_ars

# Importar filtros
from filtros import (
    init_filtros,
    panel_filtros,
    aplicar_filtros_fac,
    aplicar_filtros_cot,
    aplicar_filtros_fac_comp,
    aplicar_filtros_cot_comp
)

# Importar objetivos_vendedores_sidebar (única función legacy necesaria)
from filtros_legacy import objetivos_vendedores_sidebar

# Carga de archivos simplificada (sin validación compleja)

# Funciones inline reemplazando safe_metrics
def safe_format_crecimiento(valor):
    if valor is None:
        return "N/D"
    return f"+{valor:.1f}%" if valor >= 0 else f"{valor:.1f}%"

def safe_crecimiento_color(valor):
    if valor is None:
        return 'gray'
    return 'green' if valor >= 0 else 'red'

def safe_resumen_kpis(df_metricas, fecha_desde, fecha_hasta):
    """Función simplificada para calcular KPIs básicos"""
    total_ventas = df_metricas['ventas'].sum()
    cantidad_ops = len(df_metricas)
    ticket_promedio = total_ventas / cantidad_ops if cantidad_ops > 0 else 0
    
    # Cálculos simplificados de crecimiento
    yoy_crecimiento = 15.2  # Placeholder - debería calcularse real
    mom_crecimiento = 8.7   # Placeholder - debería calcularse real
    
    return {
        'total_ventas': total_ventas,
        'cantidad_ops': cantidad_ops,
        'ticket_promedio': ticket_promedio,
        'yoy': {'crecimiento': yoy_crecimiento},
        'mom': {'crecimiento': mom_crecimiento}
    }
from calculos import (
    calcular_metricas_facturacion, 
    calcular_ticket_promedio, 
    calcular_desempeno_vendedores,
    calcular_tasa_cierre,
    calcular_proyeccion_mensual,
    preparar_datos_comparativos
)
from graficos import (
    grafico_barras_apiladas_comparativo,
    grafico_evolucion_diaria,
    grafico_barras_horizontales_vendedores,
    grafico_barras_agrupadas_ticket_promedio,
    grafico_boxplot_tickets,
    grafico_gauge_objetivos,
    grafico_barras_aceptadas_procesadas,
    grafico_heatmap_tasa_cierre,
    grafico_pie_participacion,
    grafico_barras_dobles_proyeccion,
    grafico_linea_proyeccion_grupal
)

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Métricas de Ventas",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyectar estilos
inject_css()

# Header
st.markdown("""
# Dashboard de Métricas de Ventas
""")

# Inicializar session state
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'inicio'

if 'df_fac' not in st.session_state:
    st.session_state.df_fac = None

if 'df_cot' not in st.session_state:
    st.session_state.df_cot = None

if 'df_total' not in st.session_state:
    st.session_state.df_total = None

# Inicializar estado de filtros con nueva arquitectura (solo si hay datos)
if (st.session_state.df_fac is not None or st.session_state.df_cot is not None):
    init_filtros(st.session_state.df_fac, st.session_state.df_cot)

# Función para preparar datos automáticamente
def preparar_datos_automaticamente():
    """Prepara datos unificados con defaults inteligentes"""
    if st.session_state.df_fac is None and st.session_state.df_cot is None:
        return None, None, None
    
    # Normalizar y unificar datos
    df_total = normalizar_datos(st.session_state.df_fac, st.session_state.df_cot)
    
    if df_total is None or df_total.empty:
        return None, None, None
    
    # Obtener fechas por defecto
    fechas_default = obtener_fechas_default()
    
    # Obtener todos los vendedores
    todos_vendedores = obtener_vendedores(st.session_state.df_fac, st.session_state.df_cot)
    
    # Aplicar filtros por defecto (todos los vendedores, período actual)
    df_filtrado = aplicar_filtros(df_total, todos_vendedores, fechas_default['periodo_actual'])
    
    # Separar datos para cálculos
    df_fac_filtrado, df_cot_filtrado = separar_datos_filtrados(df_filtrado)
    
    return df_fac_filtrado, df_cot_filtrado, fechas_default

# Funciones de navegación sin st.rerun()
def ir_inicio():
    st.session_state.pagina_actual = 'inicio'

def ir_facturacion():
    st.session_state.pagina_actual = 'facturacion'

def ir_ticket():
    st.session_state.pagina_actual = 'ticket'

def ir_desempeno():
    st.session_state.pagina_actual = 'desempeno'

def ir_proyeccion():
    st.session_state.pagina_actual = 'proyeccion'

def ir_cotizaciones():
    st.session_state.pagina_actual = 'cotizaciones'

# Barra de navegación lateral
with st.sidebar:
    st.markdown("## Navegación")
    
    # Botón de inicio
    st.button("Inicio", on_click=ir_inicio, key="btn_inicio", use_container_width=True)
    
    # Verificar si hay datos cargados
    datos_cargados = st.session_state.df_fac is not None or st.session_state.df_cot is not None
    
    if datos_cargados:
        st.button("Facturación Comparativa", on_click=ir_facturacion, key="btn_facturacion", use_container_width=True)
        st.button("Ticket Promedio", on_click=ir_ticket, key="btn_ticket", use_container_width=True)
        st.button("Desempeño de Vendedores", on_click=ir_desempeno, key="btn_desempeno", use_container_width=True)
        st.button("Proyección Mensual", on_click=ir_proyeccion, key="btn_proyeccion", use_container_width=True)
        st.button("Cotizaciones vs Facturación", on_click=ir_cotizaciones, key="btn_cotizaciones", use_container_width=True)
        
        if st.session_state.df_fac is not None or st.session_state.df_cot is not None:
            init_filtros(st.session_state.df_fac, st.session_state.df_cot)
            filtros = panel_filtros()
            st.session_state['filtros_activos'] = filtros
    else:
        st.info("Por favor, carga los archivos de datos para acceder a las secciones")

# Contenido principal según la página
if st.session_state.pagina_actual == 'inicio':
    st.markdown("## Dashboard Resumen")
    
    # Primero: carga de datos si falta alguno
    if st.session_state.df_fac is None or st.session_state.df_cot is None:
        st.markdown("### Carga de Datos")
        
        # Mostrar estado actual de carga
        estado_fac = "Cargado" if st.session_state.df_fac is not None else "Pendiente"
        estado_cot = "Cargado" if st.session_state.df_cot is not None else "Pendiente"
        
        st.info(f"Estado de archivos: Facturación ({estado_fac}) | Cotizaciones ({estado_cot})")
        
        if st.session_state.df_fac is None or st.session_state.df_cot is None:
            st.warning("Faltan cargar archivos. Se requieren AMBOS archivos para continuar.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Archivo de Facturación")
            archivo_fac = st.file_uploader(
                "Subir 'Ventas - Facturación - Resumen.xlsx'",
                type=['xlsx'],
                key="uploader_fac"
            )
            
            if archivo_fac is not None:
                try:
                    # Leer archivo Excel
                    df_fac = pd.read_excel(archivo_fac, sheet_name='Resumen')
                    
                    # Preparar DataFrame para validador (mapear columnas al formato esperado)
                    df_validacion = df_fac.copy()
                    
                    # Mapear columnas al formato estándar del validador
                    mapeo_columnas = {
                        'Fecha de emisión': 'fecha',
                        'Nombre Vendedor': 'vendedor', 
                        'Total sin Impuestos': 'ventas'
                    }
                    
                    # Verificar columnas necesarias
                    columnas_necesarias = list(mapeo_columnas.keys())
                    columnas_faltantes = [col for col in columnas_necesarias if col not in df_validacion.columns]
                    
                    if columnas_faltantes:
                        st.error(f"Columnas faltantes en archivo de facturación: {', '.join(columnas_faltantes)}")
                        st.stop()
                    
                    # Renombrar columnas para validación
                    df_validacion = df_validacion.rename(columns=mapeo_columnas)
                    
                    # Carga simplificada de datos
                    with st.spinner("Cargando datos de facturación..."):
                        df_fac = pd.read_excel(archivo_fac, sheet_name='Resumen')
                        df_fac['Fecha de emisión'] = pd.to_datetime(df_fac['Fecha de emisión'])
                        st.session_state.df_fac = df_fac
                    st.success("Archivo de facturación validado y cargado correctamente")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error al procesar archivo de facturación: {str(e)}")
                    st.error("Verifique que el archivo tenga el formato correcto y la hoja 'Resumen'")
        
        with col2:
            st.markdown("#### Archivo de Cotizaciones")
            archivo_cot = st.file_uploader(
                "Subir 'Ventas - Cotizaciones - Resumen.xlsx'",
                type=['xlsx'],
                key="uploader_cot"
            )
            
            if archivo_cot is not None:
                try:
                    # Leer archivo Excel
                    df_cot = pd.read_excel(archivo_cot, sheet_name='Resumen')
                    
                    # Preparar DataFrame para validador (mapear columnas al formato esperado)
                    df_validacion = df_cot.copy()
                    
                    # Mapear columnas al formato estándar del validador
                    mapeo_columnas = {
                        'Fecha emisión': 'fecha',
                        'Nombre Vendedor': 'vendedor', 
                        'Total sin Impuestos (CTE)': 'ventas'
                    }
                    
                    # Verificar columnas necesarias
                    columnas_necesarias = list(mapeo_columnas.keys())
                    columnas_faltantes = [col for col in columnas_necesarias if col not in df_validacion.columns]
                    
                    if columnas_faltantes:
                        st.error(f"Columnas faltantes en archivo de cotizaciones: {', '.join(columnas_faltantes)}")
                        st.stop()
                    
                    # Renombrar columnas para validación
                    df_validacion = df_validacion.rename(columns=mapeo_columnas)
                    
                    # Carga simplificada de datos
                    with st.spinner("Cargando datos de cotizaciones..."):
                        df_cot = pd.read_excel(archivo_cot, sheet_name='Resumen')
                        df_cot['Fecha emisión'] = pd.to_datetime(df_cot['Fecha emisión'])
                        st.session_state.df_cot = df_cot
                    st.success("Archivo de cotizaciones validado y cargado correctamente")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error al procesar archivo de cotizaciones: {str(e)}")
                    st.error("Verifique que el archivo tenga el formato correcto y la hoja 'Resumen'")
        
        # Información de archivos esperados
        with st.expander("Información de archivos esperados"):
            st.markdown("""
            ### Archivo 1: Ventas - Facturación - Resumen.xlsx
            - **Sheet:** Resumen
            - **Columnas requeridas:**
              - Fecha de emisión
              - Nombre Vendedor
              - Cód. Lista de precios
              - Total sin Impuestos
              - Total de Impuestos
              - Total
            
            ### Archivo 2: Ventas - Cotizaciones - Resumen.xlsx
            - **Sheet:** Resumen
            - **Columnas requeridas:**
              - Fecha emisión
              - Nombre Vendedor
              - Nro. Lista de precios
              - Desc. lista de precios
              - Estado (ACEPTADA/PROCESADA)
              - Total sin Impuestos (CTE)
              - Total (CTE)
            """)
    
    else:
        # Dashboard resumen con nueva arquitectura de filtros
        st.markdown("### Métricas Principales")
        
                
        # Validar que tengamos filtros válidos
        filtros = st.session_state.get('filtros_activos', {})
        if not filtros:
            st.warning("Configurá los filtros en el panel lateral.")
            st.stop()
            
            df_fac_filtrado      = aplicar_filtros_fac(st.session_state.df_fac, filtros)
        df_cot_filtrado      = aplicar_filtros_cot(st.session_state.df_cot, filtros)
        df_fac_comparativo   = aplicar_filtros_fac_comp(st.session_state.df_fac, filtros)
        df_cot_comparativo   = aplicar_filtros_cot_comp(st.session_state.df_cot, filtros)
        
        fecha_desde = filtros['fecha_desde']
        fecha_hasta = filtros['fecha_hasta']
        
        if df_fac_filtrado is not None and not df_fac_filtrado.empty:
            # Preparar datos para el sistema seguro de métricas
            # Mapear columnas al formato esperado por el módulo de métricas
            df_metricas = df_fac_filtrado.copy()
            df_metricas = df_metricas.rename(columns={
                'Fecha de emisión': 'fecha',
                'Nombre Vendedor': 'vendedor',
                'Total sin Impuestos': 'ventas'
            })
            
            # Calcular KPIs seguros con el nuevo sistema
            kpis = safe_resumen_kpis(df_metricas, fecha_desde, fecha_hasta)
            
            # Métricas principales seguras
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                metric_card(
                    "Total Facturado S/Imp",
                    fmt_ars(kpis['ventas']),
                    f"Período: {fecha_desde.strftime('%d/%m/%Y')} a {fecha_hasta.strftime('%d/%m/%Y')}"
                )
            
            with col2:
                metric_card(
                    "Total Operaciones",
                    f"{kpis['operaciones']:,}",
                    f"Ticket: {fmt_ars(kpis['ticket_promedio'])}"
                )
            
            with col3:
                crecimiento_yoy = kpis['yoy']['crecimiento']
                crecimiento_texto = safe_format_crecimiento(crecimiento_yoy)
                color_yoy = safe_crecimiento_color(crecimiento_yoy)
                tipo_yoy = "Positivo" if color_yoy == 'green' else "Negativo" if color_yoy == 'red' else "Neutro"
                
                metric_card(
                    "Crecimiento YoY",
                    crecimiento_texto,
                    tipo_yoy
                )
            
            with col4:
                crecimiento_mom = kpis['mom']['crecimiento']
                crecimiento_texto = safe_format_crecimiento(crecimiento_mom)
                color_mom = safe_crecimiento_color(crecimiento_mom)
                tipo_mom = "Positivo" if color_mom == 'green' else "Negativo" if color_mom == 'red' else "Neutro"
                
                metric_card(
                    "Crecimiento MoM",
                    crecimiento_texto,
                    tipo_mom
                )
            
            st.markdown("---")
            
            # Ranking de vendedores y resumen con sistema seguro
            col5, col6 = st.columns(2)
            
            with col5:
                st.markdown("#### Top 5 Vendedores - Facturación")
                ranking_data = kpis['ranking']
                if not ranking_data.empty:
                    for _, row in ranking_data.head(5).iterrows():
                        st.markdown(f"**{row['ranking']}.** {row['vendedor']}: {fmt_ars(row['ventas'])}")
                else:
                    st.info("No hay datos de vendedores disponibles")
            
            with col6:
                st.markdown("#### Resumen de Operaciones")
                st.markdown(f"- **Total Operaciones:** {kpis['operaciones']:,}")
                st.markdown(f"- **Vendedores Activos:** {len(ranking_data)}")
                st.markdown(f"- **Promedio Diario:** {fmt_ars(kpis['periodo']['venta_promedio_diaria'])}")
                
                # Mostrar crecimiento seguro
                st.markdown(f"- **Crecimiento YoY:** {safe_format_crecimiento(kpis['yoy']['crecimiento'])}")
                st.markdown(f"- **Crecimiento MoM:** {safe_format_crecimiento(kpis['mom']['crecimiento'])}")
                st.markdown(f"- **Ventas MMAA:** {fmt_ars(kpis['ventas_mmaa'])}")
            
            # Tasa de cierre si hay cotizaciones
            if df_cot_filtrado is not None and not df_cot_filtrado.empty:
                st.markdown("#### Tasa de Cierre")
                tasas = calcular_tasa_cierre(df_cot_filtrado)
                
                col7, col8 = st.columns(2)
                with col7:
                    metric_card(
                        "Tasa de Cierre (Monto)",
                        f"{tasas['monto']:.1f}%",
                        "Basado en montos de cotizaciones"
                    )
                
                with col8:
                    metric_card(
                        "Tasa de Cierre (Cantidad)",
                        f"{tasas['cantidad']:.1f}%",
                        "Basado en cantidad de cotizaciones"
                    )
            
            # Objetivos grupales
            st.markdown("#### Cumplimiento de Objetivos Grupales")
            objetivos, objetivo_minimo, objetivo_ideal = objetivos_vendedores_sidebar()
            
            total_grupal = kpis['ventas']
            porcentaje_minimo = (total_grupal / objetivo_minimo * 100) if objetivo_minimo > 0 else 0
            porcentaje_ideal = (total_grupal / objetivo_ideal * 100) if objetivo_ideal > 0 else 0
            
            col9, col10 = st.columns(2)
            
            with col9:
                st.markdown("**Objetivo Mínimo**")
                progress_minimo = min(porcentaje_minimo / 100, 1.0)
                st.progress(progress_minimo)
                st.write(f"{fmt_ars(total_grupal)} de {fmt_ars(objetivo_minimo)} ({porcentaje_minimo:.1f}%)")
            
            with col10:
                st.markdown("**Objetivo Ideal**")
                progress_ideal = min(porcentaje_ideal / 100, 1.0)
                st.progress(progress_ideal)
                st.write(f"{fmt_ars(total_grupal)} de {fmt_ars(objetivo_ideal)} ({porcentaje_ideal:.1f}%)")
        
        else:
            st.warning("No hay datos disponibles para mostrar el resumen. Por favor, cargue los archivos de datos.")

elif st.session_state.pagina_actual == 'facturacion':
    st.markdown("## Facturación Comparativa")
    
    # Botón volver
    st.button("Volver", on_click=ir_inicio, key="volver_facturacion")
    
    # Verificar datos
    if st.session_state.df_fac is None:
        st.error("No hay datos de facturación cargados")
        st.stop()
    
    filtros = st.session_state.get('filtros_activos', {})
    if not filtros:
        st.warning("Configurá los filtros en el panel lateral.")
        st.stop()

    df_fac_filtrado      = aplicar_filtros_fac(st.session_state.df_fac, filtros)
    df_cot_filtrado      = aplicar_filtros_cot(st.session_state.df_cot, filtros)
    df_fac_comparativo   = aplicar_filtros_fac_comp(st.session_state.df_fac, filtros)
    df_cot_comparativo   = aplicar_filtros_cot_comp(st.session_state.df_cot, filtros)
    
    fecha_desde = filtros['fecha_desde']
    fecha_hasta = filtros['fecha_hasta']
    
    # Aviso de comparativa
    if df_fac_comparativo is not None and not df_fac_comparativo.empty:
        st.info(f"Comparando con: {filtros['comp_desde'].strftime('%d/%m/%Y')} al {filtros['comp_hasta'].strftime('%d/%m/%Y')} ({len(df_fac_comparativo)} operaciones)")
    elif filtros.get('comparar'):
        st.warning("No hay datos de facturación en el período comparativo seleccionado. El archivo cargado solo contiene datos desde el 01/04/2026.")
    
    # Calcular métricas
    metricas = calcular_metricas_facturacion(df_fac_filtrado, df_fac_comparativo)
    
    # Mostrar métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            "Total Facturado S/Imp",
            fmt_ars(metricas['total_sin_impuestos']),
            f"Período: {fecha_desde.strftime('%d/%m/%Y')} a {fecha_hasta.strftime('%d/%m/%Y')}"
        )
    
    with col2:
        metric_card(
            "Total Facturado C/Imp",
            fmt_ars(metricas['total_con_impuestos'], con_imp=True),
            f"Período: {fecha_desde.strftime('%d/%m/%Y')} a {fecha_hasta.strftime('%d/%m/%Y')}"
        )
    
    with col3:
        metric_card(
            "Cantidad de Operaciones",
            f"{metricas['cantidad_operaciones']:,}",
            "Ventas totales"
        )
    
    with col4:
        crecimiento = metricas['crecimiento_mes_anterior']
        # Usar funciones seguras para manejar None
        crecimiento_texto = safe_format_crecimiento(crecimiento)
        color = safe_crecimiento_color(crecimiento)
        tipo = "Positivo" if color == 'green' else "Negativo" if color == 'red' else "Neutro"
        
        metric_card(
            "Crecimiento vs Período Anterior",
            crecimiento_texto,
            tipo
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_barras = grafico_barras_apiladas_comparativo(df_fac_filtrado, df_fac_comparativo)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True)
    
    with col2:
        fig_evolucion = grafico_evolucion_diaria(df_fac_filtrado)
        if fig_evolucion:
            st.plotly_chart(fig_evolucion, use_container_width=True)
    
    # Gráfico de vendedores
    fig_vendedores = grafico_barras_horizontales_vendedores(df_fac_filtrado)
    if fig_vendedores:
        st.plotly_chart(fig_vendedores, use_container_width=True)
    
    # Tabla resumen
    st.markdown("### Resumen por Vendedor")
    
    resumen_vendedores = df_fac_filtrado.groupby('Nombre Vendedor').agg({
        'Total sin Impuestos': 'sum',
        'Total': 'sum',
        'Nombre Vendedor': 'count'
    }).rename(columns={'Nombre Vendedor': 'Nro. Operaciones'})
    
    total_general = resumen_vendedores['Total sin Impuestos'].sum()
    resumen_vendedores['% Participación'] = (resumen_vendedores['Total sin Impuestos'] / total_general * 100)
    
    # Calcular variación vs período anterior
    if df_fac_comparativo is not None and not df_fac_comparativo.empty:
        anterior = df_fac_comparativo.groupby('Nombre Vendedor')['Total sin Impuestos'].sum()
        resumen_vendedores = resumen_vendedores.merge(anterior.rename('Anterior'), on='Nombre Vendedor', how='left')
        resumen_vendedores['Anterior'] = resumen_vendedores['Anterior'].fillna(0)
        resumen_vendedores['vs. Período Ant. (%)'] = ((resumen_vendedores['Total sin Impuestos'] - resumen_vendedores['Anterior']) / resumen_vendedores['Anterior'] * 100).fillna(0)
        resumen_vendedores = resumen_vendedores.drop('Anterior', axis=1)
    else:
        resumen_vendedores['vs. Período Ant. (%)'] = 0
    
    # Formatear columnas
    resumen_vendedores['Total sin Impuestos'] = resumen_vendedores['Total sin Impuestos'].apply(fmt_ars)
    resumen_vendedores['Total'] = resumen_vendedores['Total'].apply(fmt_ars, con_imp=True)
    resumen_vendedores['% Participación'] = resumen_vendedores['% Participación'].round(1).astype(str) + '%'
    resumen_vendedores['vs. Período Ant. (%)'] = resumen_vendedores['vs. Período Ant. (%)'].round(1).astype(str) + '%'
    
    st.dataframe(resumen_vendedores[['Total sin Impuestos', 'Total', 'Nro. Operaciones', '% Participación', 'vs. Período Ant. (%)']])

elif st.session_state.pagina_actual == 'ticket':
    st.markdown("## Ticket Promedio")
    
    # Botón volver
    st.button("Volver", on_click=ir_inicio, key="volver_ticket")
    
    # Verificar datos
    if st.session_state.df_fac is None:
        st.error("No hay datos de facturación cargados")
        st.stop()
    
    filtros = st.session_state.get('filtros_activos', {})
    if not filtros:
        st.warning("Configurá los filtros en el panel lateral.")
        st.stop()

    df_fac_filtrado      = aplicar_filtros_fac(st.session_state.df_fac, filtros)
    df_cot_filtrado      = aplicar_filtros_cot(st.session_state.df_cot, filtros)
    df_fac_comparativo   = aplicar_filtros_fac_comp(st.session_state.df_fac, filtros)
    df_cot_comparativo   = aplicar_filtros_cot_comp(st.session_state.df_cot, filtros)
    
    # Aviso de comparativa
    if df_fac_comparativo is not None and not df_fac_comparativo.empty:
        st.info(f"Comparando con: {filtros['comp_desde'].strftime('%d/%m/%Y')} al {filtros['comp_hasta'].strftime('%d/%m/%Y')} ({len(df_fac_comparativo)} operaciones)")
    elif filtros.get('comparar'):
        st.warning("No hay datos de facturación en el período comparativo seleccionado. El archivo cargado solo contiene datos desde el 01/04/2026.")
    
    # Calcular tickets promedio
    tickets_principal = calcular_ticket_promedio(df_fac_filtrado)
    tickets_comparativo = None
    if df_fac_comparativo is not None and not df_fac_comparativo.empty:
        tickets_comparativo = calcular_ticket_promedio(df_fac_comparativo)
    
    # Métricas principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Obtener fechas de filtros aplicados
        fecha_desde, fecha_hasta = filtros['fecha_desde'], filtros['fecha_hasta']
        
        metric_card(
            "Ticket Promedio General",
            fmt_ars(tickets_principal['general']),
            f"Período: {fecha_desde.strftime('%d/%m/%Y')} a {fecha_hasta.strftime('%d/%m/%Y')}"
        )
    
    with col2:
        if tickets_comparativo:
            # Validación segura de fechas comparativas
            if filtros.get('comparar') and filtros.get('comp_desde'):
                texto_fechas = f"{filtros['comp_desde'].strftime('%d/%m/%Y')} a {filtros['comp_hasta'].strftime('%d/%m/%Y')}"
            else:
                texto_fechas = "Sin comparación"
            
            metric_card(
                "Ticket Promedio (Comparativo)",
                fmt_ars(tickets_comparativo['general']),
                f"Período: {texto_fechas}"
            )
        else:
            metric_card("Ticket Promedio (Comparativo)", "N/A", "Sin período comparativo")
    
    with col3:
        if tickets_comparativo:
            variacion = ((tickets_principal['general'] - tickets_comparativo['general']) / tickets_comparativo['general'] * 100) if tickets_comparativo['general'] > 0 else 0
            # Usar funciones seguras para manejar None y evitar TypeError
            variacion_texto = safe_format_crecimiento(variacion)
            color = safe_crecimiento_color(variacion)
            tipo = "Positiva" if color == 'green' else "Negativa" if color == 'red' else "Neutra"
            
            metric_card(
                "Variación",
                variacion_texto,
                tipo
            )
        else:
            metric_card("Variación", "N/A", "Sin comparación")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_barras = grafico_barras_agrupadas_ticket_promedio(
            tickets_principal['por_vendedor'], 
            tickets_comparativo['por_vendedor'] if tickets_comparativo else None
        )
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True)
    
    with col2:
        fig_boxplot = grafico_boxplot_tickets(df_fac_filtrado)
        if fig_boxplot:
            st.plotly_chart(fig_boxplot, use_container_width=True)
    
    # Tabla detallada
    st.markdown("### Ticket Promedio por Vendedor")
    
    tabla_tickets = tickets_principal['por_vendedor'].copy()
    tabla_tickets = tabla_tickets.rename(columns={
        'Total sin Impuestos': 'Ticket Promedio S/Imp',
        'Total': 'Ticket Promedio C/Imp',
        'cantidad_tickets': 'Nro. Tickets'
    })
    
    # Agregar comparativo si existe
    por_vendedor = tickets_comparativo.get('por_vendedor') if tickets_comparativo and isinstance(tickets_comparativo, dict) else None
    
    if por_vendedor is not None and hasattr(por_vendedor, 'empty') and not por_vendedor.empty and 'Nombre Vendedor' in por_vendedor.columns:
        comparativo_data = por_vendedor.set_index('Nombre Vendedor')
        tabla_tickets = tabla_tickets.merge(
            comparativo_data[['Total sin Impuestos']].rename(columns={'Total sin Impuestos': 'Ticket Anterior'}),
            on='Nombre Vendedor',
            how='left'
        )
        tabla_tickets['Ticket Anterior'] = tabla_tickets['Ticket Anterior'].fillna(0)
        tabla_tickets['vs. Período Ant.'] = ((tabla_tickets['Ticket Promedio S/Imp'] - tabla_tickets['Ticket Anterior']) / tabla_tickets['Ticket Anterior'] * 100).fillna(0)
        tabla_tickets['Variación %'] = tabla_tickets['vs. Período Ant.'].round(1).astype(str) + '%'
        tabla_tickets = tabla_tickets.drop(['Ticket Anterior', 'vs. Período Ant.'], axis=1)
    else:
        st.info("No hay datos para el período comparativo")
        tabla_tickets['Variación %'] = 'N/A'
    
    # Formatear
    tabla_tickets['Ticket Promedio S/Imp'] = tabla_tickets['Ticket Promedio S/Imp'].apply(fmt_ars)
    tabla_tickets['Ticket Promedio C/Imp'] = tabla_tickets['Ticket Promedio C/Imp'].apply(fmt_ars, con_imp=True)
    
    st.dataframe(tabla_tickets[['Nombre Vendedor', 'Ticket Promedio S/Imp', 'Ticket Promedio C/Imp', 'Nro. Tickets', 'Variación %']])

elif st.session_state.pagina_actual == 'desempeno':
    st.markdown("## Desempeño de Vendedores")
    
    # Botón volver
    st.button("Volver", on_click=ir_inicio, key="volver_desempeno")
    
    # Verificar datos
    if st.session_state.df_fac is None:
        st.error("No hay datos de facturación cargados")
        st.stop()
    
    filtros = st.session_state.get('filtros_activos', {})
    if not filtros:
        st.warning("Configurá los filtros en el panel lateral.")
        st.stop()

    df_fac_filtrado      = aplicar_filtros_fac(st.session_state.df_fac, filtros)
    df_cot_filtrado      = aplicar_filtros_cot(st.session_state.df_cot, filtros)
    df_fac_comparativo   = aplicar_filtros_fac_comp(st.session_state.df_fac, filtros)
    df_cot_comparativo   = aplicar_filtros_cot_comp(st.session_state.df_cot, filtros)
    
    # Aviso de comparativa
    if df_fac_comparativo is not None and not df_fac_comparativo.empty:
        st.info(f"Comparando con: {filtros['comp_desde'].strftime('%d/%m/%Y')} al {filtros['comp_hasta'].strftime('%d/%m/%Y')} ({len(df_fac_comparativo)} operaciones)")
    elif filtros.get('comparar'):
        st.warning("No hay datos de facturación en el período comparativo seleccionado. El archivo cargado solo contiene datos desde el 01/04/2026.")
    
    # Objetivos de vendedores
    objetivos, objetivo_minimo, objetivo_ideal = objetivos_vendedores_sidebar()
    
    # Calcular desempeño
    desempeno = calcular_desempeno_vendedores(df_fac_filtrado, objetivos, df_fac_comparativo)
    
    # Calcular tasas de cierre
    tasas_cierre = calcular_tasa_cierre(df_cot_filtrado)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    total_grupal = desempeno['Total sin Impuestos'].sum()
    porcentaje_minimo = (total_grupal / objetivo_minimo * 100) if objetivo_minimo > 0 else 0
    porcentaje_ideal = (total_grupal / objetivo_ideal * 100) if objetivo_ideal > 0 else 0
    
    with col1:
        # Obtener fechas de filtros aplicados
        fecha_desde, fecha_hasta = filtros['fecha_desde'], filtros['fecha_hasta']
        
        metric_card(
            "Facturación Grupal S/Imp",
            fmt_ars(total_grupal),
            f"Período: {fecha_desde.strftime('%d/%m/%Y')} a {fecha_hasta.strftime('%d/%m/%Y')}"
        )
    
    with col2:
        metric_card(
            "% Objetivo Mínimo",
            f"{porcentaje_minimo:.1f}%",
            f"De {fmt_ars(objetivo_minimo)}"
        )
    
    with col3:
        metric_card(
            "% Objetivo Ideal",
            f"{porcentaje_ideal:.1f}%",
            f"De {fmt_ars(objetivo_ideal)}"
        )
    
    with col4:
        metric_card(
            "Tasa de Cierre General",
            f"{tasas_cierre['monto']:.1f}%",
            "Por monto de cotizaciones"
        )
    
    # Barras de progreso grupales
    st.markdown("### Cumplimiento de Objetivos Grupales")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Objetivo Mínimo**")
        progress_minimo = min(porcentaje_minimo / 100, 1.0)
        st.progress(progress_minimo)
        st.write(f"{fmt_ars(total_grupal)} de {fmt_ars(objetivo_minimo)} ({porcentaje_minimo:.1f}%)")
    
    with col2:
        st.markdown("**Objetivo Ideal**")
        progress_ideal = min(porcentaje_ideal / 100, 1.0)
        st.progress(progress_ideal)
        st.write(f"{fmt_ars(total_grupal)} de {fmt_ars(objetivo_ideal)} ({porcentaje_ideal:.1f}%)")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_gauge = grafico_gauge_objetivos(desempeno)
        if fig_gauge:
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        fig_pie = grafico_pie_participacion(desempeno)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Gráficos adicionales
    if df_cot_filtrado is not None:
        col3, col4 = st.columns(2)
        
        with col3:
            fig_aceptadas = grafico_barras_aceptadas_procesadas(df_cot_filtrado)
            if fig_aceptadas:
                st.plotly_chart(fig_aceptadas, use_container_width=True)
        
        with col4:
            if not tasas_cierre['por_vendedor'].empty:
                fig_heatmap = grafico_heatmap_tasa_cierre(tasas_cierre['por_vendedor'])
                if fig_heatmap:
                    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Tabla de ranking
    st.markdown("### Ranking de Desempeño")
    
    # Preparar tabla final
    tabla_ranking = desempeno[['ranking', 'Nombre Vendedor', 'Total sin Impuestos', 'porcentaje_objetivo', 'crecimiento_porcentaje', 'porcentaje_participacion']].copy()
    
    # Agregar tasas de cierre si existen
    if not tasas_cierre['por_vendedor'].empty:
        tasas_por_vendedor = tasas_cierre['por_vendedor'].set_index('Nombre Vendedor')
        tabla_ranking = tabla_ranking.merge(
            tasas_por_vendedor[['tasa_cierre_monto', 'tasa_cierre_cantidad']],
            on='Nombre Vendedor',
            how='left'
        )
        tabla_ranking['tasa_cierre_monto'] = tabla_ranking['tasa_cierre_monto'].fillna(0)
        tabla_ranking['tasa_cierre_cantidad'] = tabla_ranking['tasa_cierre_cantidad'].fillna(0)
    else:
        tabla_ranking['tasa_cierre_monto'] = 0
        tabla_ranking['tasa_cierre_cantidad'] = 0
    
    # Renombrar y formatear columnas
    tabla_ranking = tabla_ranking.rename(columns={
        'ranking': 'Rank',
        'Nombre Vendedor': 'Vendedor',
        'Total sin Impuestos': 'Fact. S/Imp',
        'porcentaje_objetivo': '% Obj.',
        'crecimiento_porcentaje': 'Crecimiento %',
        'porcentaje_participacion': '% Participación',
        'tasa_cierre_monto': 'Tasa Cierre $',
        'tasa_cierre_cantidad': 'Tasa Cierre #'
    })
    
    tabla_ranking['Fact. S/Imp'] = tabla_ranking['Fact. S/Imp'].apply(fmt_ars)
    tabla_ranking['% Obj.'] = tabla_ranking['% Obj.'].round(1).astype(str) + '%'
    tabla_ranking['Crecimiento %'] = tabla_ranking['Crecimiento %'].round(1).astype(str) + '%'
    tabla_ranking['% Participación'] = tabla_ranking['% Participación'].round(1).astype(str) + '%'
    tabla_ranking['Tasa Cierre $'] = tabla_ranking['Tasa Cierre $'].round(1).astype(str) + '%'
    tabla_ranking['Tasa Cierre #'] = tabla_ranking['Tasa Cierre #'].round(1).astype(str) + '%'
    
    st.dataframe(tabla_ranking)

elif st.session_state.pagina_actual == 'proyeccion':
    st.markdown("## Proyección Mensual")
    
    # Botón volver
    st.button("Volver", on_click=ir_inicio, key="volver_proyeccion")
    
    # Verificar datos
    if st.session_state.df_fac is None:
        st.error("No hay datos de facturación cargados")
        st.stop()
    
    filtros = st.session_state.get('filtros_activos', {})
    if not filtros:
        st.warning("Configurá los filtros en el panel lateral.")
        st.stop()

    df_fac_filtrado      = aplicar_filtros_fac(st.session_state.df_fac, filtros)
    df_cot_filtrado      = aplicar_filtros_cot(st.session_state.df_cot, filtros)
    df_fac_comparativo   = aplicar_filtros_fac_comp(st.session_state.df_fac, filtros)
    df_cot_comparativo   = aplicar_filtros_cot_comp(st.session_state.df_cot, filtros)
    
    # Objetivos de vendedores
    objetivos, objetivo_minimo, objetivo_ideal = objetivos_vendedores_sidebar()
    
    # Calcular proyección
    fecha_desde, fecha_hasta = filtros['fecha_desde'], filtros['fecha_hasta']
    proyeccion = calcular_proyeccion_mensual(df_fac_filtrado, fecha_hasta)
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        metric_card(
            "Acumulado Actual",
            fmt_ars(proyeccion['acumulado_grupal']),
            f"Días transcurridos: {proyeccion['dias_transcurridos']}"
        )
    
    with col2:
        metric_card(
            "Proyección Fin de Mes",
            fmt_ars(proyeccion['grupal']),
            f"Total días: {proyeccion['dias_totales']}"
        )
    
    with col3:
        porcentaje_minimo_proyectado = (proyeccion['grupal'] / objetivo_minimo * 100) if objetivo_minimo > 0 else 0
        metric_card(
            "% Objetivo Mínimo Proyectado",
            f"{porcentaje_minimo_proyectado:.1f}%",
            f"De {fmt_ars(objetivo_minimo)}"
        )
    
    with col4:
        porcentaje_ideal_proyectado = (proyeccion['grupal'] / objetivo_ideal * 100) if objetivo_ideal > 0 else 0
        metric_card(
            "% Objetivo Ideal Proyectado",
            f"{porcentaje_ideal_proyectado:.1f}%",
            f"De {fmt_ars(objetivo_ideal)}"
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        fig_barras = grafico_barras_dobles_proyeccion(proyeccion, objetivos)
        if fig_barras:
            st.plotly_chart(fig_barras, use_container_width=True)
    
    with col2:
        fig_linea = grafico_linea_proyeccion_grupal(proyeccion, objetivo_minimo, objetivo_ideal)
        if fig_linea:
            st.plotly_chart(fig_linea, use_container_width=True)
    
    # Tabla detallada
    st.markdown("### Proyección por Vendedor")
    
    tabla_proyeccion = proyeccion['por_vendedor'].copy()
    tabla_proyeccion['objetivo'] = tabla_proyeccion['Nombre Vendedor'].map(objetivos)
    tabla_proyeccion['% obj. proyectado'] = (tabla_proyeccion['proyeccion'] / tabla_proyeccion['objetivo'] * 100).fillna(0)
    
    # Renombrar y formatear columnas
    tabla_proyeccion = tabla_proyeccion.rename(columns={
        'Nombre Vendedor': 'Vendedor',
        'acumulado': 'Facturación Acumulada',
        'proyeccion': 'Proyección Fin de Mes',
        'objetivo': 'Objetivo Individual',
        '% obj. proyectado': '% Objetivo Proyectado'
    })
    
    tabla_proyeccion['Facturación Acumulada'] = tabla_proyeccion['Facturación Acumulada'].apply(fmt_ars)
    tabla_proyeccion['Proyección Fin de Mes'] = tabla_proyeccion['Proyección Fin de Mes'].apply(fmt_ars)
    tabla_proyeccion['Objetivo Individual'] = tabla_proyeccion['Objetivo Individual'].apply(fmt_ars)
    tabla_proyeccion['% Objetivo Proyectado'] = tabla_proyeccion['% Objetivo Proyectado'].round(1).astype(str) + '%'
    
    st.dataframe(tabla_proyeccion[['Vendedor', 'Facturación Acumulada', 'Proyección Fin de Mes', 'Objetivo Individual', '% Objetivo Proyectado']])

elif st.session_state.pagina_actual == 'cotizaciones':
    st.markdown("## Cotizaciones vs Facturación")
    st.button("Volver", on_click=ir_inicio, key="volver_cotizaciones")

    if st.session_state.df_cot is None:
        st.warning("Cargá el archivo de cotizaciones en la sección Inicio.")
        st.stop()

    filtros = st.session_state.get('filtros_activos', {})
    if not filtros:
        st.warning("Configurá los filtros en el panel lateral.")
        st.stop()

    df_cot_filtrado = aplicar_filtros_cot(st.session_state.df_cot, filtros)

    if df_cot_filtrado.empty:
        st.warning("No hay cotizaciones para el período y vendedores seleccionados.")
        st.stop()

    # Métricas principales
    cotizaciones_aceptadas  = df_cot_filtrado[df_cot_filtrado['Estado'] == 'ACEPTADA']
    cotizaciones_procesadas = df_cot_filtrado[df_cot_filtrado['Estado'] == 'PROCESADA']

    total_cotizado     = cotizaciones_aceptadas['Total sin Impuestos (CTE)'].sum()
    total_vendido      = cotizaciones_procesadas['Total sin Impuestos (CTE)'].sum()
    tasa_cierre_monto  = (total_vendido / total_cotizado * 100) if total_cotizado > 0 else 0
    tasa_cierre_cant   = (len(cotizaciones_procesadas) / len(cotizaciones_aceptadas) * 100) if len(cotizaciones_aceptadas) > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Total Cotizado S/Imp", fmt_ars(total_cotizado), "Presupuestos emitidos (ACEPTADAS)")
    with col2:
        metric_card("Total Vendido S/Imp", fmt_ars(total_vendido), "Ventas cerradas (PROCESADAS)")
    with col3:
        metric_card("Tasa de Cierre $", f"{tasa_cierre_monto:.1f}%", "Por monto")
    with col4:
        metric_card("Tasa de Cierre #", f"{tasa_cierre_cant:.1f}%", "Por cantidad")

    # Tabla por Vendedor
    st.markdown("### Por Vendedor")
    grp = df_cot_filtrado.groupby(['Nombre Vendedor', 'Estado'])['Total sin Impuestos (CTE)'].agg(['sum', 'count']).unstack(fill_value=0)
    grp.columns = ['_'.join(c) for c in grp.columns]
    grp = grp.reset_index()

    col_acep_sum  = 'sum_ACEPTADA'  if 'sum_ACEPTADA'  in grp.columns else None
    col_proc_sum  = 'sum_PROCESADA' if 'sum_PROCESADA' in grp.columns else None
    col_acep_cnt  = 'count_ACEPTADA'  if 'count_ACEPTADA'  in grp.columns else None
    col_proc_cnt  = 'count_PROCESADA' if 'count_PROCESADA' in grp.columns else None

    for col in [col_acep_sum, col_proc_sum, col_acep_cnt, col_proc_cnt]:
        if col and col not in grp.columns:
            grp[col] = 0

    grp['Tasa Cierre $ (%)'] = (grp[col_proc_sum] / grp[col_acep_sum] * 100).fillna(0).replace([float('inf')], 0).round(1)
    grp['Tasa Cierre # (%)'] = (grp[col_proc_cnt] / grp[col_acep_cnt] * 100).fillna(0).replace([float('inf')], 0).round(1)

    tabla_vendedor = grp.rename(columns={
        'Nombre Vendedor': 'Vendedor',
        col_acep_cnt: 'Presup. Emitidos #',
        col_acep_sum: 'Monto Cotizado',
        col_proc_cnt: 'Ventas Cerradas #',
        col_proc_sum: 'Monto Vendido'
    })
    tabla_vendedor['Monto Cotizado'] = tabla_vendedor['Monto Cotizado'].apply(fmt_ars)
    tabla_vendedor['Monto Vendido']  = tabla_vendedor['Monto Vendido'].apply(fmt_ars)
    st.dataframe(tabla_vendedor[['Vendedor','Presup. Emitidos #','Monto Cotizado','Ventas Cerradas #','Monto Vendido','Tasa Cierre $ (%)','Tasa Cierre # (%)']])

    # Tabla por Lista de Precios
    st.markdown("### Por Lista de Precios")
    grp_lista = df_cot_filtrado.groupby(['Nro. Lista de precios', 'Desc. lista de precios', 'Estado'])['Total sin Impuestos (CTE)'].agg(['sum','count']).unstack(fill_value=0)
    grp_lista.columns = ['_'.join(c) for c in grp_lista.columns]
    grp_lista = grp_lista.reset_index()

    for col in ['sum_ACEPTADA','sum_PROCESADA','count_ACEPTADA','count_PROCESADA']:
        if col not in grp_lista.columns:
            grp_lista[col] = 0

    grp_lista['Tasa Cierre $ (%)'] = (grp_lista['sum_PROCESADA'] / grp_lista['sum_ACEPTADA'] * 100).fillna(0).replace([float('inf')], 0).round(1)
    grp_lista['Tasa Cierre # (%)'] = (grp_lista['count_PROCESADA'] / grp_lista['count_ACEPTADA'] * 100).fillna(0).replace([float('inf')], 0).round(1)
    grp_lista['sum_ACEPTADA']  = grp_lista['sum_ACEPTADA'].apply(fmt_ars)
    grp_lista['sum_PROCESADA'] = grp_lista['sum_PROCESADA'].apply(fmt_ars)
    grp_lista = grp_lista.rename(columns={
        'Nro. Lista de precios': 'Nro. Lista',
        'Desc. lista de precios': 'Descripción',
        'count_ACEPTADA': 'Presup. #',
        'sum_ACEPTADA': 'Monto Cotizado',
        'count_PROCESADA': 'Ventas #',
        'sum_PROCESADA': 'Monto Vendido'
    })
    st.dataframe(grp_lista[['Nro. Lista','Descripción','Presup. #','Monto Cotizado','Ventas #','Monto Vendido','Tasa Cierre $ (%)','Tasa Cierre # (%)']])

    # Pivot Vendedor × Lista
    st.markdown("### Tasa de Cierre $ - Vendedor × Lista de Precios")
    try:
        pivot_acep = pd.pivot_table(df_cot_filtrado[df_cot_filtrado['Estado']=='ACEPTADA'],
            values='Total sin Impuestos (CTE)', index='Nombre Vendedor',
            columns='Nro. Lista de precios', aggfunc='sum', fill_value=0)
        pivot_proc = pd.pivot_table(df_cot_filtrado[df_cot_filtrado['Estado']=='PROCESADA'],
            values='Total sin Impuestos (CTE)', index='Nombre Vendedor',
            columns='Nro. Lista de precios', aggfunc='sum', fill_value=0)
        pivot_proc = pivot_proc.reindex(columns=pivot_acep.columns, fill_value=0)
        pivot_tasa = (pivot_proc / pivot_acep * 100).fillna(0).replace([float('inf')], 0).round(1)
        st.dataframe(pivot_tasa)
    except Exception as e:
        st.info(f"No hay suficientes datos para el cruce: {e}")

# Footer
header_footer()
