"""
Sistema de Validación Automática de Datos tipo Power BI
Validación robusta, limpieza automática y manejo de errores para datasets de ventas
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
import warnings

# Ignorar advertencias de pandas para salida limpia
warnings.filterwarnings('ignore', category=FutureWarning)


class ValidadorDatos:
    """
    Clase principal para validación y preparación de datos de ventas
    Funciona como un pipeline robusto tipo Power BI
    """
    
    def __init__(self, nombre_dataset: str = "Ventas"):
        """
        Inicializa el validador de datos
        
        Args:
            nombre_dataset: Nombre descriptivo del dataset para logs
        """
        self.nombre_dataset = nombre_dataset
        self.errores = []
        self.advertencias = []
        self.estadisticas = {}
        self.df_original = None
        self.df_validado = None
        self.score_calidad = 0
        
        # Configuración de columnas esperadas
        self.columnas_obligatorias = ['fecha', 'vendedor', 'ventas']
        self.columnas_opcionales = ['tipo', 'categoria', 'region']
        
    def validar_y_preparar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline completo de validación y preparación de datos
        
        Args:
            df: DataFrame original a validar
            
        Returns:
            DataFrame validado y limpio
            
        Raises:
            ValueError: Si hay errores críticos que impiden continuar
        """
        self.df_original = df.copy()
        self.df_validado = df.copy()
        
        try:
            # 1. Validación básica de estructura
            self._validar_estructura_basica()
            
            # 2. Validación de columnas obligatorias
            self._validar_columnas_obligatorias()
            
            # 3. Validación y limpieza de tipos de datos
            self._validar_y_limpiar_tipos()
            
            # 4. Manejo de valores nulos y corruptos
            self._manejar_valores_nulos()
            
            # 5. Normalización de datos
            self._normalizar_datos()
            
            # 6. Validación final de calidad
            self._validar_calidad_final()
            
            # 7. Calcular score de calidad
            self._calcular_score_calidad()
            
            return self.df_validado
            
        except Exception as e:
            self.errores.append(f"Error crítico en validación: {str(e)}")
            raise ValueError(f"Error en validación de datos: {str(e)}")
    
    def _validar_estructura_basica(self) -> None:
        """Valida la estructura básica del DataFrame"""
        if self.df_validado is None or self.df_validado.empty:
            raise ValueError("El DataFrame está vacío o es None")
        
        self.estadisticas['filas_originales'] = len(self.df_validado)
        self.estadisticas['columnas_originales'] = len(self.df_validado.columns)
        
        # Validar que no sea un DataFrame completamente vacío
        if self.df_validado.isna().all().all():
            raise ValueError("El DataFrame contiene solo valores nulos")
    
    def _validar_columnas_obligatorias(self) -> None:
        """Valida que existan todas las columnas obligatorias"""
        columnas_faltantes = []
        
        for columna in self.columnas_obligatorias:
            if columna not in self.df_validado.columns:
                columnas_faltantes.append(columna)
        
        if columnas_faltantes:
            error_msg = f"Columnas obligatorias faltantes: {', '.join(columnas_faltantes)}"
            self.errores.append(error_msg)
            raise ValueError(error_msg)
        
        # Validar que las columnas obligatorias no estén completamente vacías
        for columna in self.columnas_obligatorias:
            if self.df_validado[columna].isna().all():
                self.advertencias.append(f"Columna '{columna}' está completamente vacía")
    
    def _validar_y_limpiar_tipos(self) -> None:
        """Valida y corrige tipos de datos para cada columna"""
        
        # Validar y limpiar columna 'fecha'
        self._validar_columna_fecha()
        
        # Validar y limpiar columna 'vendedor'
        self._validar_columna_vendedor()
        
        # Validar y limpiar columna 'ventas'
        self._validar_columna_ventas()
        
        # Validar columnas opcionales si existen
        for columna in self.columnas_opcionales:
            if columna in self.df_validado.columns:
                self._validar_columna_opcional(columna)
    
    def _validar_columna_fecha(self) -> None:
        """Valida y limpia la columna de fecha"""
        columna = 'fecha'
        
        try:
            # Convertir a datetime, errores se convierten en NaT
            self.df_validado[columna] = pd.to_datetime(self.df_validado[columna], errors='coerce')
            
            # Contar fechas inválidas
            fechas_invalidas = self.df_validado[columna].isna().sum()
            if fechas_invalidas > 0:
                self.advertencias.append(f"Se encontraron {fechas_invalidas} fechas inválidas (convertidas a NaT)")
            
            # Validar rango de fechas razonable
            fechas_validas = self.df_validado[columna].dropna()
            if not fechas_validas.empty:
                fecha_min = fechas_validas.min()
                fecha_max = fechas_validas.max()
                
                # Validar que las fechas no sean futuras (con tolerancia de 1 día)
                hoy = pd.Timestamp.now()
                if fecha_max > hoy + pd.Timedelta(days=1):
                    self.advertencias.append(f"Se detectaron fechas futuras (máxima: {fecha_max.strftime('%Y-%m-%d')})")
                
                # Validar que no sean fechas muy antiguas (más de 10 años)
                fecha_limite_antigua = hoy - pd.Timedelta(days=365*10)
                if fecha_min < fecha_limite_antigua:
                    self.advertencias.append(f"Se detectaron fechas muy antiguas (mínima: {fecha_min.strftime('%Y-%m-%d')})")
            
        except Exception as e:
            self.errores.append(f"Error al procesar columna 'fecha': {str(e)}")
            raise
    
    def _validar_columna_vendedor(self) -> None:
        """Valida y limpia la columna de vendedor"""
        columna = 'vendedor'
        
        try:
            # Convertir a string
            self.df_validado[columna] = self.df_validado[columna].astype(str)
            
            # Limpiar espacios y valores vacíos
            self.df_validado[columna] = self.df_validado[columna].str.strip()
            
            # Reemplazar valores vacíos o genéricos
            valores_invalidos = ['', 'nan', 'None', 'null', 'NaN', 'NULL', 'NA', 'na']
            mask_invalidos = self.df_validado[columna].isin(valores_invalidos)
            cantidad_invalidos = mask_invalidos.sum()
            
            if cantidad_invalidos > 0:
                self.advertencias.append(f"Se encontraron {cantidad_invalidos} valores vacíos o inválidos en columna 'vendedor'")
                # Marcar como NaN para posterior manejo
                self.df_validado.loc[mask_invalidos, columna] = np.nan
            
            # Validar que no haya vendedores numéricos
            vendedores_numericos = self.df_validado[columna].str.replace('.', '', regex=True).str.replace('-', '', regex=True).str.isdigit()
            cantidad_numericos = vendedores_numericos.sum()
            
            if cantidad_numericos > 0:
                self.advertencias.append(f"Se detectaron {cantidad_numericos} vendedores con formato numérico")
            
        except Exception as e:
            self.errores.append(f"Error al procesar columna 'vendedor': {str(e)}")
            raise
    
    def _validar_columna_ventas(self) -> None:
        """Valida y limpia la columna de ventas"""
        columna = 'ventas'
        
        try:
            # Convertir a numérico, errores se convierten en NaN
            self.df_validado[columna] = pd.to_numeric(self.df_validado[columna], errors='coerce')
            
            # Contar valores inválidos
            ventas_invalidas = self.df_validado[columna].isna().sum()
            if ventas_invalidas > 0:
                self.advertencias.append(f"Se encontraron {ventas_invalidas} valores de ventas inválidos (convertidos a NaN)")
            
            # Validar valores negativos (pueden ser válidos para devoluciones, pero advertir)
            ventas_negativas = (self.df_validado[columna] < 0).sum()
            if ventas_negativas > 0:
                self.advertencias.append(f"Se detectaron {ventas_negativas} ventas con valores negativos")
            
            # Validar valores extremadamente grandes (outliers)
            ventas_validas = self.df_validado[columna].dropna()
            if not ventas_validas.empty:
                q99 = ventas_validas.quantile(0.99)
                outliers = (self.df_validado[columna] > q99 * 10).sum()
                if outliers > 0:
                    self.advertencias.append(f"Se detectaron {outliers} valores extremadamente grandes (posibles outliers)")
            
        except Exception as e:
            self.errores.append(f"Error al procesar columna 'ventas': {str(e)}")
            raise
    
    def _validar_columna_opcional(self, columna: str) -> None:
        """Valida y limpia columnas opcionales"""
        try:
            # Convertir a string para columnas categóricas
            if self.df_validado[columna].dtype == 'object':
                self.df_validado[columna] = self.df_validado[columna].astype(str).str.strip()
                
                # Reemplazar valores vacíos
                valores_invalidos = ['', 'nan', 'None', 'null', 'NaN', 'NULL']
                mask_invalidos = self.df_validado[columna].isin(valores_invalidos)
                cantidad_invalidos = mask_invalidos.sum()
                
                if cantidad_invalidos > 0:
                    self.advertencias.append(f"Se encontraron {cantidad_invalidos} valores inválidos en columna '{columna}'")
                    self.df_validado.loc[mask_invalidos, columna] = np.nan
            
        except Exception as e:
            self.advertencias.append(f"Error al procesar columna opcional '{columna}': {str(e)}")
    
    def _manejar_valores_nulos(self) -> None:
        """Maneja valores nulos y corruptos"""
        filas_originales = len(self.df_validado)
        total_eliminadas = 0  # Variable siempre definida
        
        # Eliminar filas con valores nulos críticos
        columnas_criticas = ['fecha', 'ventas']  # vendedor puede ser opcional en algunos casos
        
        for columna in columnas_criticas:
            if columna in self.df_validado.columns:
                nulos_antes = self.df_validado[columna].isna().sum()
                if nulos_antes > 0:
                    # Calcular filas antes de eliminar
                    filas_antes_eliminar = len(self.df_validado)
                    
                    # Eliminar filas con nulos en esta columna
                    self.df_validado = self.df_validado.dropna(subset=[columna])
                    
                    # Calcular cuántas filas se eliminaron
                    filas_despues_eliminar = len(self.df_validado)
                    eliminadas = filas_antes_eliminar - filas_despues_eliminar
                    total_eliminadas += eliminadas
                    
                    self.advertencias.append(f"Eliminadas {eliminadas} filas con {columna} nulo/corrupto")
        
        # Para vendedor, si está nulo, reemplazar con 'Desconocido'
        if 'vendedor' in self.df_validado.columns:
            nulos_vendedor = self.df_validado['vendedor'].isna().sum()
            if nulos_vendedor > 0:
                self.df_validado['vendedor'] = self.df_validado['vendedor'].fillna('Desconocido')
                self.advertencias.append(f"Reemplazados {nulos_vendedor} vendedores nulos por 'Desconocido'")
        
        filas_finales = len(self.df_validado)
        filas_eliminadas = filas_originales - filas_finales
        
        if filas_eliminadas > 0:
            self.advertencias.append(f"Total de filas eliminadas: {filas_eliminadas} ({(filas_eliminadas/filas_originales*100):.1f}%)")
        
        self.estadisticas['filas_despues_limpieza'] = filas_finales
        self.estadisticas['filas_eliminadas'] = filas_eliminadas
    
    def _normalizar_datos(self) -> None:
        """Normaliza y estandariza los datos"""
        # Ordenar por fecha
        if 'fecha' in self.df_validado.columns:
            self.df_validado = self.df_validado.sort_values('fecha')
        
        # Resetear índice si hay filas duplicadas
        if self.df_validado.index.duplicated().any():
            self.df_validado = self.df_validado.reset_index(drop=True)
            self.advertencias.append("Reset de índice debido a filas duplicadas")
    
    def _validar_calidad_final(self) -> None:
        """Validación final de calidad de datos"""
        # Validar que queden datos suficientes
        if len(self.df_validado) == 0:
            raise ValueError("No quedan datos válidos después de la limpieza")
        
        # Validar que no haya valores nulos en columnas críticas
        columnas_criticas = ['fecha', 'ventas']
        for columna in columnas_criticas:
            if columna in self.df_validado.columns:
                nulos = self.df_validado[columna].isna().sum()
                if nulos > 0:
                    self.errores.append(f"Columna crítica '{columna}' todavía tiene {nulos} valores nulos")
        
        # Validar rangos de fechas
        if 'fecha' in self.df_validado.columns:
            fechas_validas = self.df_validado['fecha'].dropna()
            if not fechas_validas.empty:
                dias_diferencia = (fechas_validas.max() - fechas_validas.min()).days
                if dias_diferencia < 0:
                    self.errores.append("Las fechas tienen orden incorrecto")
                elif dias_diferencia == 0:
                    self.advertencias.append("Todos los datos son del mismo día")
        
        # Validar consistencia de ventas
        if 'ventas' in self.df_validado.columns:
            ventas_validas = self.df_validado['ventas'].dropna()
            if not ventas_validas.empty:
                if ventas_validas.sum() == 0:
                    self.advertencias.append("El total de ventas es cero")
                elif ventas_validas.sum() < 0:
                    self.advertencias.append("El total de ventas es negativo (posibles devoluciones)")
    
    def _calcular_score_calidad(self) -> None:
        """Calcula un score de calidad de datos (0-100)"""
        score = 100
        
        # Penalizar errores críticos
        score -= len(self.errores) * 20
        
        # Penalizar advertencias
        score -= len(self.advertencias) * 5
        
        # Penalizar pérdida de datos
        if 'filas_originales' in self.estadisticas and 'filas_despues_limpieza' in self.estadisticas:
            perdida_porcentaje = (self.estadisticas['filas_originales'] - self.estadisticas['filas_despues_limpieza']) / self.estadisticas['filas_originales']
            score -= perdida_porcentaje * 30
        
        # Asegurar que el score esté en rango 0-100
        self.score_calidad = max(0, min(100, score))
    
    def mostrar_resultados_validacion(self) -> None:
        """Muestra los resultados de la validación en Streamlit"""
        st.markdown("### Validación de Datos")
        
        # Score de calidad
        color_score = "green" if self.score_calidad >= 80 else "orange" if self.score_calidad >= 60 else "red"
        st.markdown(f"**Score de Calidad:** :{color_score}[{self.score_calidad:.1f}/100]")
        
        # Estadísticas
        with st.expander("Estadísticas de Procesamiento", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Filas Originales", self.estadisticas.get('filas_originales', 0))
                st.metric("Columnas", self.estadisticas.get('columnas_originales', 0))
            
            with col2:
                st.metric("Filas Finales", self.estadisticas.get('filas_despues_limpieza', 0))
                st.metric("Filas Eliminadas", self.estadisticas.get('filas_eliminadas', 0))
        
        # Errores críticos
        if self.errores:
            st.error("### Errores Críticos Encontrados")
            for error in self.errores:
                st.error(f"· {error}")
        
        # Advertencias
        if self.advertencias:
            st.warning("### Advertencias")
            for advertencia in self.advertencias:
                st.warning(f"· {advertencia}")
        
        # Estado final
        if self.errores:
            st.error("### Estado: DATOS INVÁLIDOS")
            st.error("No se puede continuar con los datos actuales. Por favor, corrija los errores mencionados.")
        elif self.score_calidad >= 80:
            st.success("### Estado: DATOS VÁLIDOS")
            st.success("Los datos son aptos para análisis.")
        else:
            st.warning("### Estado: DATOS ACEPTABLES")
            st.warning("Los datos son usables, pero se recomienda revisar las advertencias.")
    
    def get_resumen(self) -> Dict[str, Any]:
        """Devuelve un resumen de la validación"""
        return {
            'score_calidad': self.score_calidad,
            'errores': len(self.errores),
            'advertencias': len(self.advertencias),
            'filas_originales': self.estadisticas.get('filas_originales', 0),
            'filas_finales': self.estadisticas.get('filas_despues_limpieza', 0),
            'estado': 'válido' if not self.errores and self.score_calidad >= 80 else 'aceptable' if not self.errores else 'inválido'
        }


def validar_y_preparar_datos(df: pd.DataFrame, nombre_dataset: str = "Ventas") -> pd.DataFrame:
    """
    Función principal para validar y preparar datos
    
    Args:
        df: DataFrame a validar
        nombre_dataset: Nombre descriptivo del dataset
        
    Returns:
        DataFrame validado y limpio
        
    Raises:
        ValueError: Si hay errores críticos que impiden continuar
    """
    validador = ValidadorDatos(nombre_dataset)
    df_validado = validador.validar_y_preparar_datos(df)
    
    # Mostrar resultados en Streamlit
    validador.mostrar_resultados_validacion()
    
    return df_validado


@st.cache_data
def validar_y_preparar_datos_cache(df: pd.DataFrame, nombre_dataset: str = "Ventas") -> pd.DataFrame:
    """
    Versión cacheada de la función de validación para optimización
    
    Args:
        df: DataFrame a validar
        nombre_dataset: Nombre descriptivo del dataset
        
    Returns:
        DataFrame validado y limpio
    """
    return validar_y_preparar_datos(df, nombre_dataset)
