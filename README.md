# Dashboard de Métricas de Ventas

Aplicación web completa de métricas comerciales usando **Python + Streamlit + Plotly** para analizar facturación, cotizaciones, desempeño de vendedores y proyecciones.

## Características

- **Carga de datos** desde archivos Excel exportados del sistema de gestión
- **Filtros dinámicos** por vendedores y períodos de tiempo
- **Gráficos interactivos** con Plotly Express y Graph Objects
- **Métricas comparativas** entre períodos
- **Desempeño de vendedores** con objetivos y tasas de cierre
- **Proyecciones mensuales** basadas en tendencia actual

## Requisitos

- Python 3.10+
- Las dependencias se instalan automáticamente desde `requirements.txt`

## Instalación

1. Clonar o descargar el proyecto
2. Navegar al directorio del proyecto
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```

2. **Abrir en el navegador:**
   La aplicación se abrirá automáticamente en `http://localhost:8501`

## Archivos de Entrada

### Archivo 1: `Ventas - Facturación - Resumen.xlsx`
- **Sheet:** `Resumen`
- **Columnas requeridas:**
  - `Fecha de emisión` - Fecha de la venta
  - `Nombre Vendedor` - Nombre del vendedor
  - `Cód. Lista de precios` - Código de lista usada
  - `Total sin Impuestos` - Monto neto (sin IVA)
  - `Total de Impuestos` - Monto de impuestos
  - `Total` - Monto total con impuestos

### Archivo 2: `Ventas - Cotizaciones - Resumen.xlsx`
- **Sheet:** `Resumen`
- **Columnas requeridas:**
  - `Fecha emisión` - Fecha de la cotización
  - `Nombre Vendedor` - Nombre del vendedor
  - `Nro. Lista de precios` - Número de lista
  - `Desc. lista de precios` - Descripción de lista
  - `Estado` - `ACEPTADA` (presupuesto emitido) o `PROCESADA` (venta cerrada)
  - `Total sin Impuestos (CTE)` - Monto neto
  - `Total (CTE)` - Monto con impuestos

## Secciones de la Aplicación

### 1. Carga de Datos
- Upload de archivos Excel
- Preview de datos cargados
- Validación de columnas requeridas

### 2. Facturación Comparativa
- Métricas principales (totales, operaciones, crecimiento)
- Gráficos de evolución mensual y diaria
- Comparación entre períodos
- Tabla resumen por vendedor

### 3. Ticket Promedio
- Ticket promedio general y por vendedor
- Comparación entre períodos
- Box plot de distribución
- Análisis de variación

### 4. Desempeño de Vendedores
- Objetivos individuales y grupales configurables
- Gauges de cumplimiento de objetivos
- Tasas de cierre (monto y cantidad)
- Ranking de desempeño
- Análisis por lista de precios

### 5. Proyección Mensual
- Proyección basada en días transcurridos
- Comparación con objetivos
- Análisis por vendedor y grupal
- Tendencias de cierre de mes

## Filtros Globales

### Vendedores
- Checkboxes para seleccionar vendedores
- Por defecto: Betty, Juan G, Ferrari Alan, Leandro, Cesar, Francisco, CORP Alejandro
- Posibilidad de incluir otros vendedores presentes en los datos

### Fechas
- **Período Principal:** Selector de fechas desde/hasta
- **Botones rápidos:**
  - Mes Actual
  - Mes Anterior
  - Mismo Período Mes Anterior
  - Año Completo
- **Período Comparativo:** Opcional para análisis comparativo

## Estructura del Proyecto

```
SISTEMA VENTAS/
|
|-- app.py              # Aplicación principal
|-- estilos.py          # Estilos y configuración visual
|-- filtros.py          # Funciones de filtrado y utilidades
|-- calculos.py         # Cálculos de métricas y estadísticas
|-- graficos.py         # Generación de gráficos con Plotly
|-- requirements.txt    # Dependencias del proyecto
|-- README.md          # Documentación
```

## Personalización

### Colores
Los colores principales están definidos en `estilos.py`:
- Celeste principal: `#0099CC`
- Celeste oscuro: `#007AA3`
- Celeste claro: `#E0F4FB`

### Objetivos
Los objetivos mensuales se pueden modificar directamente en la sidebar de la sección "Desempeño de Vendedores".

## Formato de Moneda

Todos los valores monetarios se muestran en formato de peso argentino:
- `$1.000.000,00 ARS S/IMP` (sin impuestos)
- `$1.210.000,00 ARS C/IMP` (con impuestos)

## Soporte

Desarrollado por Andrea Mariel Furgeri | Argentina 2026
- Tel: 1122899249
- Mail: andreamariel.furgeri@gmail.com
- LinkedIn: https://www.linkedin.com/in/andrea-furgeri

Todos los derechos reservados © 2026
