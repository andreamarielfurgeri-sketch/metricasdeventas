#!/usr/bin/env python3
"""
Dashboard de Métricas de Ventas - Versión Simplificada
Esta versión usa solo las librerías estándar de Python para demostración
"""

import os
import sys
from pathlib import Path

def crear_demo_html():
    """Crea una página HTML demostrativa del dashboard"""
    
    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Métricas de Ventas</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background-color: #F4F8FB;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #0099CC, #007AA3);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .nav-sidebar {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .nav-button {
            display: block;
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            background: #0099CC;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        .nav-button:hover {
            background: #007AA3;
        }
        .nav-button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .section h2 {
            color: #0099CC;
            margin-top: 0;
            border-bottom: 2px solid #E0F4FB;
            padding-bottom: 10px;
        }
        .metric-card {
            background: #F8FBFD;
            border: 2px solid #E0F4FB;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #0099CC;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 1em;
            color: #666;
            margin-bottom: 10px;
        }
        .upload-area {
            border: 2px dashed #0099CC;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            background: #F8FBFD;
            margin: 20px 0;
        }
        .file-input {
            margin: 20px 0;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            width: 100%;
        }
        .info-box {
            background: #E0F4FB;
            border-left: 4px solid #0099CC;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .demo-chart {
            background: linear-gradient(135deg, #E0F4FB, #F8FBFD);
            height: 300px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #0099CC;
            font-weight: bold;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin: 40px 0;
            padding: 20px;
            border-top: 1px solid #E0F4FB;
            border-bottom: 1px solid #E0F4FB;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .progress-bar {
            background: #E0F4FB;
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            background: linear-gradient(90deg, #0099CC, #007AA3);
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard de Métricas de Ventas</h1>
            <p>Análisis completo de facturación, cotizaciones y desempeño comercial</p>
        </div>

        <div class="nav-sidebar">
            <h3>Navegación</h3>
            <button class="nav-button">Inicio</button>
            <button class="nav-button">Facturación Comparativa</button>
            <button class="nav-button">Ticket Promedio</button>
            <button class="nav-button">Desempeño de Vendedores</button>
            <button class="nav-button">Proyección Mensual</button>
        </div>

        <div class="section">
            <h2>Estado del Sistema</h2>
            <div class="info-box">
                <strong>Estado:</strong> Aplicación Python/Streamlt lista para ejecutar<br>
                <strong>Archivos:</strong> 7 archivos creados exitosamente<br>
                <strong>Dependencias:</strong> Requiere instalación de pip y paquetes
            </div>
        </div>

        <div class="section">
            <h2>Carga de Datos</h2>
            <div class="grid">
                <div class="upload-area">
                    <h3>Archivo de Facturación</h3>
                    <p>Ventas - Facturación - Resumen.xlsx</p>
                    <input type="file" class="file-input" accept=".xlsx">
                </div>
                <div class="upload-area">
                    <h3>Archivo de Cotizaciones</h3>
                    <p>Ventas - Cotizaciones - Resumen.xlsx</p>
                    <input type="file" class="file-input" accept=".xlsx">
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Métricas Principales (Demo)</h2>
            <div class="grid">
                <div class="metric-card">
                    <div class="metric-label">Total Facturado S/Imp</div>
                    <div class="metric-value">$1.234.567,89 ARS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Total Facturado C/Imp</div>
                    <div class="metric-value">$1.493.827,15 ARS</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Cantidad de Operaciones</div>
                    <div class="metric-value">156</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Crecimiento vs Mes Anterior</div>
                    <div class="metric-value">+12.5%</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>Gráficos (Demo)</h2>
            <div class="demo-chart">
                Gráfico de Barras - Facturación Mensual
            </div>
            <div class="demo-chart">
                Gráfico de Líneas - Evolución Diaria
            </div>
            <div class="demo-chart">
                Gráfico Circular - Participación por Vendedor
            </div>
        </div>

        <div class="section">
            <h2>Desempeño de Vendedores</h2>
            <div class="info-box">
                <strong>Objetivos Configurables:</strong><br>
                - Betty: $100.000.000 ARS<br>
                - Juan G: $100.000.000 ARS<br>
                - Cesar: $100.000.000 ARS<br>
                - Francisco: $100.000.000 ARS<br>
                - Ferrari Alan: $100.000.000 ARS<br>
                - Leandro: $50.000.000 ARS<br>
                - CORP Alejandro: $100.000.000 ARS
            </div>
            <h3>Progreso Grupal</h3>
            <div>
                <p>Objetivo Mínimo: $550.000.000 ARS</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 75%;"></div>
                </div>
                <p>75% completado</p>
            </div>
            <div>
                <p>Objetivo Ideal: $850.000.000 ARS</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 48%;"></div>
                </div>
                <p>48% completado</p>
            </div>
        </div>

        <div class="section">
            <h2>Instalación y Ejecución</h2>
            <div class="info-box">
                <h3>Pasos para ejecutar la aplicación completa:</h3>
                <ol>
                    <li>Instalar herramientas de desarrollo: <code>xcode-select --install</code></li>
                    <li>Instalar dependencias: <code>pip install -r requirements.txt</code></li>
                    <li>Ejecutar aplicación: <code>streamlit run app.py</code></li>
                    <li>Abrir navegador en: <code>http://localhost:8501</code></li>
                </ol>
            </div>
        </div>

        <div class="footer">
            <strong>Desarrollado por Andrea Mariel Furgeri | Argentina 2026</strong><br>
            Tel: 1122899249 | Mail: andreamariel.furgeri@gmail.com<br>
            LinkedIn: https://www.linkedin.com/in/andrea-furgeri<br>
            Todos los derechos reservados © 2026
        </div>
    </div>

    <script>
        // Simulación de interactividad
        document.querySelectorAll('.nav-button').forEach(button => {
            button.addEventListener('click', function() {
                alert('Esta es una versión demo. Para la funcionalidad completa, ejecute la aplicación Streamlit.');
            });
        });

        document.querySelectorAll('.file-input').forEach(input => {
            input.addEventListener('change', function() {
                alert('Esta es una versión demo. Para procesar archivos, ejecute la aplicación Streamlit.');
            });
        });
    </script>
</body>
</html>
    """
    
    return html_content

def main():
    """Función principal"""
    print("Dashboard de Métricas de Ventas - Versión Demo")
    print("=" * 50)
    
    # Crear archivo HTML demo
    html_content = crear_demo_html()
    
    with open('dashboard_demo.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Archivo demo creado: dashboard_demo.html")
    print("Para ver la demostración, abra este archivo en su navegador web.")
    
    # Intentar abrir en navegador (sistema macOS)
    try:
        import subprocess
        subprocess.run(['open', 'dashboard_demo.html'])
        print("Abriendo demostración en navegador...")
    except:
        print("No se pudo abrir automáticamente. Por favor, abra dashboard_demo.html manualmente.")
    
    print("\n" + "=" * 50)
    print("INSTRUCCIONES PARA APLICACIÓN COMPLETA:")
    print("1. Instalar herramientas de desarrollo: xcode-select --install")
    print("2. Instalar dependencias: pip3 install -r requirements.txt")
    print("3. Ejecutar: streamlit run app.py")
    print("4. Abrir: http://localhost:8501")
    print("=" * 50)

if __name__ == "__main__":
    main()
