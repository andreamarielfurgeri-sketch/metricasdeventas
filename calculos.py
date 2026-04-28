import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from estilos import fmt_ars

def calcular_crecimiento(valor_actual, valor_anterior):
    """Calcula porcentaje de crecimiento entre dos valores"""
    if valor_anterior == 0 or valor_anterior is None:
        return None
    return ((valor_actual - valor_anterior) / valor_anterior) * 100

def calcular_metricas_facturacion(df_fac, df_fac_anterior=None):
    """Calcula métricas principales de facturación"""
    if df_fac is None or df_fac.empty:
        return {
            'total_sin_impuestos': 0,
            'total_con_impuestos': 0,
            'cantidad_operaciones': 0,
            'crecimiento_mes_anterior': None,
            'crecimiento_anio_anterior': None
        }
    
    # Validar que las columnas necesarias existan
    if 'Total sin Impuestos' not in df_fac.columns or 'Total' not in df_fac.columns:
        return {
            'total_sin_impuestos': 0,
            'total_con_impuestos': 0,
            'cantidad_operaciones': 0,
            'crecimiento_mes_anterior': None,
            'crecimiento_anio_anterior': None
        }
    
    total_sin_impuestos = df_fac['Total sin Impuestos'].sum()
    total_con_impuestos = df_fac['Total'].sum()
    cantidad_operaciones = len(df_fac)
    
    crecimiento_mes_anterior = None
    crecimiento_anio_anterior = None
    
    # Calcular crecimiento solo si hay datos anteriores válidos
    if (df_fac_anterior is not None and 
        not df_fac_anterior.empty and 
        'Total sin Impuestos' in df_fac_anterior.columns):
        
        total_anterior = df_fac_anterior['Total sin Impuestos'].sum()
        crecimiento_mes_anterior = calcular_crecimiento(total_sin_impuestos, total_anterior)
    
    return {
        'total_sin_impuestos': total_sin_impuestos,
        'total_con_impuestos': total_con_impuestos,
        'cantidad_operaciones': cantidad_operaciones,
        'crecimiento_mes_anterior': crecimiento_mes_anterior,
        'crecimiento_anio_anterior': crecimiento_anio_anterior
    }

def calcular_ticket_promedio(df_fac):
    """Calcula ticket promedio general y por vendedor"""
    if df_fac is None or df_fac.empty:
        return {
            'general': 0,
            'por_vendedor': pd.DataFrame(columns=['Nombre Vendedor', 'Total sin Impuestos', 'Total', 'cantidad_tickets'])
        }
    
    ticket_general = df_fac['Total sin Impuestos'].mean()
    
    tickets_vendedor = df_fac.groupby('Nombre Vendedor').agg({
        'Total sin Impuestos': 'mean',
        'Total': 'mean',
        'Nombre Vendedor': 'count'
    }).rename(columns={'Nombre Vendedor': 'cantidad_tickets'})
    
    tickets_vendedor = tickets_vendedor.reset_index()
    
    return {
        'general': ticket_general,
        'por_vendedor': tickets_vendedor
    }

def calcular_desempeno_vendedores(df_fac, objetivos, df_fac_anterior=None):
    """Calcula métricas de desempeño por vendedor"""
    if df_fac is None or df_fac.empty:
        return pd.DataFrame()
    
    # Agrupar por vendedor
    desempeno = df_fac.groupby('Nombre Vendedor').agg({
        'Total sin Impuestos': 'sum',
        'Total': 'sum',
        'Nombre Vendedor': 'count'
    }).rename(columns={'Nombre Vendedor': 'cantidad_operaciones'})
    
    desempeno = desempeno.reset_index()
    
    # Calcular % objetivo individual
    desempeno['objetivo_individual'] = desempeno['Nombre Vendedor'].map(objetivos)
    desempeno['porcentaje_objetivo'] = (desempeno['Total sin Impuestos'] / desempeno['objetivo_individual'] * 100).fillna(0)
    
    # Calcular crecimiento vs período anterior
    if df_fac_anterior is not None and not df_fac_anterior.empty:
        anterior = df_fac_anterior.groupby('Nombre Vendedor')['Total sin Impuestos'].sum().reset_index()
        desempeno = desempeno.merge(anterior, on='Nombre Vendedor', how='left', suffixes=('', '_anterior'))
        desempeno['crecimiento_porcentaje'] = desempeno.apply(
            lambda row: calcular_crecimiento(row['Total sin Impuestos'], row['Total sin Impuestos_anterior']), 
            axis=1
        )
        desempeno = desempeno.drop('Total sin Impuestos_anterior', axis=1)
    else:
        desempeno['crecimiento_porcentaje'] = 0
    
    # Calcular % de participación
    total_grupal = desempeno['Total sin Impuestos'].sum()
    desempeno['porcentaje_participacion'] = (desempeno['Total sin Impuestos'] / total_grupal * 100).fillna(0)
    
    # Calcular ranking
    desempeno = desempeno.sort_values('Total sin Impuestos', ascending=False)
    desempeno['ranking'] = range(1, len(desempeno) + 1)
    
    return desempeno

def calcular_tasa_cierre(df_cot):
    """Calcula tasas de cierre por monto y cantidad"""
    if df_cot is None or df_cot.empty:
        return {
            'monto': 0,
            'cantidad': 0,
            'por_lista': pd.DataFrame(),
            'por_vendedor': pd.DataFrame()
        }
    
    # Separar cotizaciones ACEPTADAS y PROCESADAS
    aceptadas = df_cot[df_cot['Estado'] == 'ACEPTADA']
    procesadas = df_cot[df_cot['Estado'] == 'PROCESADA']
    
    # Tasa de cierre por monto
    total_aceptadas = aceptadas['Total sin Impuestos (CTE)'].sum() if not aceptadas.empty else 0
    total_procesadas = procesadas['Total sin Impuestos (CTE)'].sum() if not procesadas.empty else 0
    
    tasa_cierre_monto = (total_procesadas / total_aceptadas * 100) if total_aceptadas > 0 else 0
    
    # Tasa de cierre por cantidad
    cant_aceptadas = len(aceptadas)
    cant_procesadas = len(procesadas)
    
    tasa_cierre_cantidad = (cant_procesadas / cant_aceptadas * 100) if cant_aceptadas > 0 else 0
    
    # Tasa de cierre por lista de precios
    tasa_por_lista = pd.DataFrame()
    
    if not df_cot.empty:
        # Agrupar por lista de precios y estado
        por_lista = df_cot.groupby(['Nro. Lista de precios', 'Estado'])['Total sin Impuestos (CTE)'].sum().unstack(fill_value=0)
        
        if 'ACEPTADA' in por_lista.columns and 'PROCESADA' in por_lista.columns:
            por_lista['tasa_cierre'] = (por_lista['PROCESADA'] / por_lista['ACEPTADA'] * 100).fillna(0)
            por_lista['tasa_cierre'] = por_lista['tasa_cierre'].replace([np.inf, -np.inf], 0)
            tasa_por_lista = por_lista.reset_index()
    
    # Tasa de cierre por vendedor
    tasa_por_vendedor = pd.DataFrame()
    
    if not df_cot.empty:
        # Agrupar por vendedor y estado
        por_vendedor = df_cot.groupby(['Nombre Vendedor', 'Estado']).agg({
            'Total sin Impuestos (CTE)': 'sum',
            'Estado': 'count'
        }).rename(columns={'Estado': 'cantidad'})
        
        # Separar montos y cantidades
        montos_vendedor = por_vendedor['Total sin Impuestos (CTE)'].unstack(fill_value=0)
        cantidades_vendedor = por_vendedor['cantidad'].unstack(fill_value=0)
        
        if 'ACEPTADA' in montos_vendedor.columns and 'PROCESADA' in montos_vendedor.columns:
            resultado = pd.DataFrame({
                'monto_aceptado': montos_vendedor['ACEPTADA'],
                'monto_procesado': montos_vendedor['PROCESADA'],
                'cantidad_aceptada': cantidades_vendedor['ACEPTADA'],
                'cantidad_procesada': cantidades_vendedor['PROCESADA']
            })
            
            resultado['tasa_cierre_monto'] = (resultado['monto_procesado'] / resultado['monto_aceptado'] * 100).fillna(0)
            resultado['tasa_cierre_cantidad'] = (resultado['cantidad_procesada'] / resultado['cantidad_aceptada'] * 100).fillna(0)
            
            # Reemplazar infinitos
            resultado['tasa_cierre_monto'] = resultado['tasa_cierre_monto'].replace([np.inf, -np.inf], 0)
            resultado['tasa_cierre_cantidad'] = resultado['tasa_cierre_cantidad'].replace([np.inf, -np.inf], 0)
            
            tasa_por_vendedor = resultado.reset_index()
    
    return {
        'monto': tasa_cierre_monto,
        'cantidad': tasa_cierre_cantidad,
        'por_lista': tasa_por_lista,
        'por_vendedor': tasa_por_vendedor
    }

def calcular_proyeccion_mensual(df_fac, fecha_hasta=None):
    """Calcula proyección mensual basada en días transcurridos"""
    if df_fac is None or df_fac.empty:
        return {'por_vendedor': pd.DataFrame(), 'grupal': 0}
    
    if fecha_hasta is None:
        fecha_hasta = datetime.now().date()
    
    fecha_hasta_dt = pd.to_datetime(fecha_hasta)
    
    # Obtener primer día del mes
    primer_dia_mes = fecha_hasta_dt.replace(day=1)
    
    # Calcular días transcurridos y totales del mes
    dias_transcurridos = (fecha_hasta_dt - primer_dia_mes).days + 1
    
    # Último día del mes
    if fecha_hasta_dt.month == 12:
        ultimo_dia_mes = fecha_hasta_dt.replace(year=fecha_hasta_dt.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        ultimo_dia_mes = fecha_hasta_dt.replace(month=fecha_hasta_dt.month + 1, day=1) - timedelta(days=1)
    
    dias_totales_mes = (ultimo_dia_mes - primer_dia_mes).days + 1
    
    # Filtrar facturación del mes actual
    fac_mes_actual = df_fac[df_fac['Fecha de emisión'] >= primer_dia_mes]
    fac_mes_actual = fac_mes_actual[fac_mes_actual['Fecha de emisión'] <= fecha_hasta_dt]
    
    if fac_mes_actual.empty:
        return {'por_vendedor': pd.DataFrame(), 'grupal': 0}
    
    # Calcular proyección por vendedor
    proyeccion_vendedor = fac_mes_actual.groupby('Nombre Vendedor')['Total sin Impuestos'].sum().reset_index()
    proyeccion_vendedor['acumulado'] = proyeccion_vendedor['Total sin Impuestos']
    proyeccion_vendedor['proyeccion'] = proyeccion_vendedor['acumulado'] * (dias_totales_mes / dias_transcurridos)
    
    # Proyección grupal
    acumulado_grupal = fac_mes_actual['Total sin Impuestos'].sum()
    proyeccion_grupal = acumulado_grupal * (dias_totales_mes / dias_transcurridos)
    
    return {
        'por_vendedor': proyeccion_vendedor,
        'grupal': proyeccion_grupal,
        'acumulado_grupal': acumulado_grupal,
        'dias_transcurridos': dias_transcurridos,
        'dias_totales': dias_totales_mes
    }

def preparar_datos_comparativos(df_fac, fechas_periodo, fechas_comparativo):
    """Prepara DataFrames para períodos principal y comparativo"""
    if df_fac is None:
        return None, None
    
    df_fac['Fecha de emisión'] = pd.to_datetime(df_fac['Fecha de emisión'])
    
    # Período principal
    if fechas_periodo:
        fecha_desde, fecha_hasta = fechas_periodo
        df_principal = df_fac[
            (df_fac['Fecha de emisión'] >= pd.to_datetime(fecha_desde)) &
            (df_fac['Fecha de emisión'] <= pd.to_datetime(fecha_hasta))
        ]
    else:
        df_principal = df_fac.copy()
    
    # Período comparativo
    df_comparativo = None
    if fechas_comparativo:
        fecha_desde_comp, fecha_hasta_comp = fechas_comparativo
        df_comparativo = df_fac[
            (df_fac['Fecha de emisión'] >= pd.to_datetime(fecha_desde_comp)) &
            (df_fac['Fecha de emisión'] <= pd.to_datetime(fecha_hasta_comp))
        ]
    
    return df_principal, df_comparativo
