import streamlit as st

# Colores de marca
COLOR_PRIMARY = "#0099CC"      # Celeste
COLOR_DARK    = "#007AA3"      # Celeste oscuro
COLOR_LIGHT   = "#E0F4FB"      # Celeste claro
COLOR_WHITE   = "#FFFFFF"

# Configuración de Plotly
plotly_template = "plotly_white"
color_sequence = ["#0099CC", "#007AA3", "#33B5D9", "#66CCEC", "#99DDF2"]

def fmt_ars(valor, con_imp=False):
    """Formatea números en formato de peso argentino"""
    if valor is None or valor != valor:  # Check for None or NaN
        return "$0,00 ARS"
    
    sufijo = "C/IMP" if con_imp else "S/IMP"
    try:
        return f"${valor:,.2f} ARS {sufijo}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return f"${valor} ARS {sufijo}"

def inject_css():
    """Inyecta CSS personalizado en la aplicación"""
    css = """
    <style>
    .main {
        background-color: #F4F8FB;
    }
    
    .stDataFrame {
        background-color: white;
        border: 1px solid #E0F4FB;
    }
    
    .stDataFrame th {
        background-color: #0099CC;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    
    .stDataFrame td {
        text-align: center;
        padding: 8px;
    }
    
    .metric-card {
        background-color: white;
        border: 2px solid #E0F4FB;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    
    .sidebar .sidebar-content {
        background-color: white;
    }
    
    .stSelectbox > div > div > select {
        background-color: white;
    }
    
    .stDateInput > div > div > input {
        background-color: white;
    }
    
    .stButton > button {
        background-color: #0099CC;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #007AA3;
    }
    
    body {
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    
    .header-footer {
        text-align: center;
        color: #666;
        font-size: 0.9em;
        margin: 20px 0;
        padding: 10px;
        border-top: 1px solid #E0F4FB;
        border-bottom: 1px solid #E0F4FB;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def header_footer():
    """Agrega header y footer a la aplicación"""
    header_footer_html = """
    <div class="header-footer">
        <strong>Desarrollado por Andrea Mariel Furgeri | Argentina 2026</strong><br>
        Tel: 1122899249 | Mail: andreamariel.furgeri@gmail.com<br>
        LinkedIn: <a href="https://www.linkedin.com/in/andrea-furgeri" target="_blank">https://www.linkedin.com/in/andrea-furgeri</a><br>
        Todos los derechos reservados © 2026
    </div>
    """
    st.markdown(header_footer_html, unsafe_allow_html=True)

def metric_card(title, value, subtitle=""):
    """Crea una tarjeta de métrica personalizada"""
    card_html = f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {f'<div style="font-size: 0.9em; color: #999;">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
