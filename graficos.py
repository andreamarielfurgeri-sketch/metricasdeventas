import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from estilos import plotly_template, color_sequence, fmt_ars, COLOR_PRIMARY, COLOR_DARK, COLOR_LIGHT

def grafico_barras_apiladas_comparativo(df_principal, df_comparativo=None):
    """Gráfico de barras apiladas por mes comparando períodos"""
    if df_principal is None or df_principal.empty:
        return None
    
    # Agrupar por mes para período principal
    df_principal['Fecha de emisión'] = pd.to_datetime(df_principal['Fecha de emisión'])
    df_principal['Mes'] = df_principal['Fecha de emisión'].dt.to_period('M')
    
    mensual_principal = df_principal.groupby('Mes').agg({
        'Total sin Impuestos': 'sum',
        'Total': 'sum'
    }).reset_index()
    
    mensual_principal['Impuestos'] = mensual_principal['Total'] - mensual_principal['Total sin Impuestos']
    
    fig = go.Figure()
    
    # Datos principales
    fig.add_trace(go.Bar(
        name='S/Imp (Principal)',
        x=mensual_principal['Mes'].astype(str),
        y=mensual_principal['Total sin Impuestos'],
        marker_color=COLOR_LIGHT,
        text=mensual_principal['Total sin Impuestos'].apply(fmt_ars),
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Impuestos (Principal)',
        x=mensual_principal['Mes'].astype(str),
        y=mensual_principal['Impuestos'],
        marker_color=COLOR_PRIMARY,
        text=mensual_principal['Impuestos'].apply(fmt_ars),
        textposition='auto'
    ))
    
    # Datos comparativos
    if df_comparativo is not None and not df_comparativo.empty:
        df_comparativo['Fecha de emisión'] = pd.to_datetime(df_comparativo['Fecha de emisión'])
        df_comparativo['Mes'] = df_comparativo['Fecha de emisión'].dt.to_period('M')
        
        mensual_comparativo = df_comparativo.groupby('Mes').agg({
            'Total sin Impuestos': 'sum',
            'Total': 'sum'
        }).reset_index()
        
        mensual_comparativo['Impuestos'] = mensual_comparativo['Total'] - mensual_comparativo['Total sin Impuestos']
        
        fig.add_trace(go.Bar(
            name='S/Imp (Comparativo)',
            x=mensual_comparativo['Mes'].astype(str),
            y=mensual_comparativo['Total sin Impuestos'],
            marker_color='rgba(224, 244, 251, 0.5)',
            text=mensual_comparativo['Total sin Impuestos'].apply(fmt_ars),
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Impuestos (Comparativo)',
            x=mensual_comparativo['Mes'].astype(str),
            y=mensual_comparativo['Impuestos'],
            marker_color='rgba(0, 153, 204, 0.5)',
            text=mensual_comparativo['Impuestos'].apply(fmt_ars),
            textposition='auto'
        ))
    
    fig.update_layout(
        title="Facturación Mensual Comparativa",
        xaxis_title="Mes",
        yaxis_title="Monto (ARS)",
        barmode='group',
        template=plotly_template,
        height=500
    )
    
    return fig

def grafico_evolucion_diaria(df_fac):
    """Gráfico de línea de evolución diaria de facturación"""
    if df_fac is None or df_fac.empty:
        return None
    
    df_fac['Fecha de emisión'] = pd.to_datetime(df_fac['Fecha de emisión'])
    
    diario = df_fac.groupby(df_fac['Fecha de emisión'].dt.date)['Total sin Impuestos'].sum().reset_index()
    diario.columns = ['Fecha', 'Monto']
    
    fig = px.line(
        diario, 
        x='Fecha', 
        y='Monto',
        title="Evolución Diaria de Facturación",
        labels={'Monto': 'Monto S/Imp (ARS)', 'Fecha': 'Fecha'},
        template=plotly_template,
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    
    fig.update_traces(mode='lines+markers')
    fig.update_layout(height=400)
    
    return fig

def grafico_barras_horizontales_vendedores(df_fac):
    """Gráfico de barras horizontales de facturación por vendedor"""
    if df_fac is None or df_fac.empty:
        return None
    
    vendedores = df_fac.groupby('Nombre Vendedor')['Total sin Impuestos'].sum().sort_values(ascending=True)
    
    fig = px.bar(
        x=vendedores.values,
        y=vendedores.index,
        orientation='h',
        title="Facturación por Vendedor",
        labels={'x': 'Monto S/Imp (ARS)', 'y': 'Vendedor'},
        template=plotly_template,
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    
    fig.update_layout(height=max(400, len(vendedores) * 40))
    
    return fig

def grafico_barras_agrupadas_ticket_promedio(tickets_principal, tickets_comparativo=None):
    """Gráfico de barras agrupadas de ticket promedio por vendedor"""
    if tickets_principal is None or tickets_principal.empty:
        return None
    
    fig = go.Figure()
    
    # Datos principales
    fig.add_trace(go.Bar(
        name='Ticket Promedio (Principal)',
        x=tickets_principal['Nombre Vendedor'],
        y=tickets_principal['Total sin Impuestos'],
        marker_color=COLOR_PRIMARY,
        text=tickets_principal['Total sin Impuestos'].apply(fmt_ars),
        textposition='auto'
    ))
    
    # Datos comparativos
    if tickets_comparativo is not None and not tickets_comparativo.empty:
        fig.add_trace(go.Bar(
            name='Ticket Promedio (Comparativo)',
            x=tickets_comparativo['Nombre Vendedor'],
            y=tickets_comparativo['Total sin Impuestos'],
            marker_color=COLOR_LIGHT,
            text=tickets_comparativo['Total sin Impuestos'].apply(fmt_ars),
            textposition='auto'
        ))
    
    fig.update_layout(
        title="Ticket Promedio por Vendedor",
        xaxis_title="Vendedor",
        yaxis_title="Ticket Promedio S/Imp (ARS)",
        barmode='group',
        template=plotly_template,
        height=500
    )
    
    return fig

def grafico_boxplot_tickets(df_fac):
    """Box plot de distribución de tickets por vendedor"""
    if df_fac is None or df_fac.empty:
        return None
    
    fig = px.box(
        df_fac, 
        x='Nombre Vendedor', 
        y='Total sin Impuestos',
        title="Distribución de Tickets por Vendedor",
        labels={'Total sin Impuestos': 'Monto S/Imp (ARS)', 'Nombre Vendedor': 'Vendedor'},
        template=plotly_template,
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    
    fig.update_layout(height=500)
    
    return fig

def grafico_gauge_objetivos(desempeno):
    """Gráfico gauge de % objetivo cumplido por vendedor"""
    if desempeno is None or desempeno.empty:
        return None
    
    # Crear subplots para múltiples gauges
    n_vendedores = len(desempeno)
    cols = 2
    rows = (n_vendedores + cols - 1) // cols
    
    fig = go.Figure()
    
    for i, (_, row) in enumerate(desempeno.iterrows()):
        vendedor = row['Nombre Vendedor']
        porcentaje = min(row['porcentaje_objetivo'], 200)  # Limitar a 200% para visualización
        
        # Determinar color
        if porcentaje < 50:
            color = "red"
        elif porcentaje < 80:
            color = "orange"
        else:
            color = "green"
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=porcentaje,
            domain={'row': i // cols, 'column': i % cols},
            title={'text': vendedor},
            gauge={
                'axis': {'range': [None, 200]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 200], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
    
    fig.update_layout(
        grid={'rows': rows, 'columns': cols},
        template=plotly_template,
        height=rows * 300,
        title_text="Cumplimiento de Objetivos por Vendedor"
    )
    
    return fig

def grafico_barras_aceptadas_procesadas(df_cot):
    """Gráfico de barras agrupadas de cotizaciones ACEPTADAS vs PROCESADAS"""
    if df_cot is None or df_cot.empty:
        return None
    
    # Agrupar por vendedor y estado
    por_vendedor = df_cot.groupby(['Nombre Vendedor', 'Estado'])['Total sin Impuestos (CTE)'].sum().unstack(fill_value=0)
    
    if 'ACEPTADA' not in por_vendedor.columns or 'PROCESADA' not in por_vendedor.columns:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='ACEPTADAS',
        x=por_vendedor.index,
        y=por_vendedor['ACEPTADA'],
        marker_color=COLOR_LIGHT,
        text=por_vendedor['ACEPTADA'].apply(fmt_ars),
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='PROCESADAS',
        x=por_vendedor.index,
        y=por_vendedor['PROCESADA'],
        marker_color=COLOR_PRIMARY,
        text=por_vendedor['PROCESADA'].apply(fmt_ars),
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Cotizaciones ACEPTADAS vs PROCESADAS por Vendedor",
        xaxis_title="Vendedor",
        yaxis_title="Monto S/Imp (ARS)",
        barmode='group',
        template=plotly_template,
        height=500
    )
    
    return fig

def grafico_heatmap_tasa_cierre(tasa_por_vendedor_lista):
    """Heatmap de tasa de cierre por vendedor y lista de precios"""
    if tasa_por_vendedor_lista is None or tasa_por_vendedor_lista.empty:
        return None
    
    # Preparar datos para heatmap
    heatmap_data = tasa_por_vendedor_lista.pivot_table(
        index='Nombre Vendedor', 
        columns='Nro. Lista de precios', 
        values='tasa_cierre_monto',
        fill_value=0
    )
    
    fig = px.imshow(
        heatmap_data,
        title="Tasa de Cierre por Vendedor y Lista de Precios (%)",
        labels={'x': 'Lista de Precios', 'y': 'Vendedor', 'color': 'Tasa de Cierre (%)'},
        template=plotly_template,
        color_continuous_scale="RdYlGn"
    )
    
    fig.update_layout(height=500)
    
    return fig

def grafico_pie_participacion(desempeno):
    """Pie chart de participación en facturación por vendedor"""
    if desempeno is None or desempeno.empty:
        return None
    
    fig = px.pie(
        desempeno,
        values='Total sin Impuestos',
        names='Nombre Vendedor',
        title="Participación en Facturación por Vendedor",
        template=plotly_template,
        color_discrete_sequence=color_sequence
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)
    
    return fig

def grafico_barras_dobles_proyeccion(proyeccion_data, objetivos):
    """Gráfico de barras dobles: acumulado vs proyección vs objetivo"""
    if proyeccion_data is None or proyeccion_data['por_vendedor'].empty:
        return None
    
    df_proyeccion = proyeccion_data['por_vendedor'].copy()
    
    # Agregar objetivos
    df_proyeccion['objetivo'] = df_proyeccion['Nombre Vendedor'].map(objetivos)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Acumulado',
        x=df_proyeccion['Nombre Vendedor'],
        y=df_proyeccion['acumulado'],
        marker_color=COLOR_LIGHT,
        text=df_proyeccion['acumulado'].apply(fmt_ars),
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Proyección',
        x=df_proyeccion['Nombre Vendedor'],
        y=df_proyeccion['proyeccion'],
        marker_color=COLOR_PRIMARY,
        text=df_proyeccion['proyeccion'].apply(fmt_ars),
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Objetivo',
        x=df_proyeccion['Nombre Vendedor'],
        y=df_proyeccion['objetivo'],
        marker_color='rgba(255, 165, 0, 0.7)',
        text=df_proyeccion['objetivo'].apply(fmt_ars),
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Acumulado vs Proyección vs Objetivo por Vendedor",
        xaxis_title="Vendedor",
        yaxis_title="Monto S/Imp (ARS)",
        barmode='group',
        template=plotly_template,
        height=500
    )
    
    return fig

def grafico_linea_proyeccion_grupal(proyeccion_data, objetivo_minimo, objetivo_ideal):
    """Gráfico de línea de proyección grupal con objetivos"""
    if proyeccion_data is None:
        return None
    
    # Simular proyección diaria para el mes
    dias_transcurridos = proyeccion_data.get('dias_transcurridos', 0)
    dias_totales = proyeccion_data.get('dias_totales', 30)
    acumulado_grupal = proyeccion_data.get('acumulado_grupal', 0)
    proyeccion_grupal = proyeccion_data.get('grupal', 0)
    
    # Crear datos para la línea
    dias = list(range(1, dias_totales + 1))
    proyeccion_diaria = []
    
    for dia in dias:
        if dia <= dias_transcurridos:
            # Valor real acumulado (simulado linealmente)
            valor = acumulado_grupal * (dia / dias_transcurridos)
        else:
            # Proyección lineal
            valor = acumulado_grupal + (proyeccion_grupal - acumulado_grupal) * ((dia - dias_transcurridos) / (dias_totales - dias_transcurridos))
        proyeccion_diaria.append(valor)
    
    fig = go.Figure()
    
    # Línea de proyección
    fig.add_trace(go.Scatter(
        x=dias,
        y=proyeccion_diaria,
        mode='lines+markers',
        name='Proyección de Facturación',
        line=dict(color=COLOR_PRIMARY, width=3),
        fill='tonexty'
    ))
    
    # Líneas de objetivos
    fig.add_hline(
        y=objetivo_minimo,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Objetivo Mínimo: {fmt_ars(objetivo_minimo)}",
        annotation_position="top right"
    )
    
    fig.add_hline(
        y=objetivo_ideal,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Objetivo Ideal: {fmt_ars(objetivo_ideal)}",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title="Proyección de Facturación Mensual",
        xaxis_title="Día del Mes",
        yaxis_title="Acumulado S/Imp (ARS)",
        template=plotly_template,
        height=500
    )
    
    return fig
