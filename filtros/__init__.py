import streamlit as st
import pandas as pd
from datetime import date, timedelta
import calendar

# ── VENDEDORES POR DEFECTO ──────────────────────────────────────────────────
VENDEDORES_DEFAULT = [
    'Betty', 'Juan G', 'Ferrari Alan', 'Leandro',
    'Cesar', 'Francisco', 'CORP Alejandro'
]

def _primer_dia_mes(d: date) -> date:
    return d.replace(day=1)

def _ultimo_dia_mes(d: date) -> date:
    ultimo = calendar.monthrange(d.year, d.month)[1]
    return d.replace(day=ultimo)

def _mes_anterior(d: date) -> date:
    primer = _primer_dia_mes(d)
    return _primer_dia_mes(primer - timedelta(days=1))


def init_filtros(df_fac, df_cot):
    """Inicializa session_state de filtros. Solo escribe si la key no existe."""
    hoy = date.today()

    # Vendedores disponibles
    vendedores = set()
    if df_fac is not None:
        vendedores.update(df_fac['Nombre Vendedor'].dropna().unique().tolist())
    if df_cot is not None:
        vendedores.update(df_cot['Nombre Vendedor'].dropna().unique().tolist())
    vendedores = sorted(vendedores)

    if 'f_vendedores_disponibles' not in st.session_state:
        st.session_state['f_vendedores_disponibles'] = vendedores

    if 'f_vendedores' not in st.session_state:
        st.session_state['f_vendedores'] = [
            v for v in VENDEDORES_DEFAULT if v in vendedores
        ]

    if 'f_desde' not in st.session_state:
        st.session_state['f_desde'] = _primer_dia_mes(hoy)

    if 'f_hasta' not in st.session_state:
        st.session_state['f_hasta'] = hoy

    if 'f_comparar' not in st.session_state:
        st.session_state['f_comparar'] = False

    if 'f_comp_desde' not in st.session_state:
        mes_ant = _mes_anterior(hoy)
        st.session_state['f_comp_desde'] = _primer_dia_mes(mes_ant)

    if 'f_comp_hasta' not in st.session_state:
        mes_ant = _mes_anterior(hoy)
        st.session_state['f_comp_hasta'] = _ultimo_dia_mes(mes_ant)


def panel_filtros():
    """
    Renderiza el panel completo de filtros en el sidebar.
    Retorna dict con los filtros activos.
    Llamar UNA SOLA VEZ desde el sidebar de app.py.
    """
    hoy = date.today()
    vendedores_disponibles = st.session_state.get('f_vendedores_disponibles', [])

    # ── VENDEDORES ────────────────────────────────────────────────────────────
    st.sidebar.markdown("### Vendedores")

    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("Todos", key="btn_todos"):
        st.session_state['f_vendedores'] = vendedores_disponibles[:]
        st.rerun()
    if col_b.button("Ninguno", key="btn_ninguno"):
        st.session_state['f_vendedores'] = []
        st.rerun()

    vendedores_seleccionados = []
    for v in vendedores_disponibles:
        marcado = v in st.session_state.get('f_vendedores', [])
        checked = st.sidebar.checkbox(v, value=marcado, key=f"chk_{v}")
        if checked:
            vendedores_seleccionados.append(v)

    st.session_state['f_vendedores'] = vendedores_seleccionados

    # ── PERÍODO PRINCIPAL ─────────────────────────────────────────────────────
    st.sidebar.markdown("### Período Principal")

    # Botones de acceso rápido
    c1, c2 = st.sidebar.columns(2)
    c3, c4 = st.sidebar.columns(2)

    if c1.button("Mes Actual", key="btn_mes_actual"):
        st.session_state['f_desde'] = _primer_dia_mes(hoy)
        st.session_state['f_hasta'] = hoy
        st.rerun()

    if c2.button("Mes Anterior", key="btn_mes_ant"):
        mes_ant = _mes_anterior(hoy)
        st.session_state['f_desde'] = _primer_dia_mes(mes_ant)
        st.session_state['f_hasta'] = _ultimo_dia_mes(mes_ant)
        st.rerun()

    if c3.button("Mismo Per. Ant.", key="btn_mismo_per"):
        # Mismo rango de días pero mes anterior
        desde = st.session_state['f_desde']
        hasta = st.session_state['f_hasta']
        delta = hasta - desde
        mes_ant = _mes_anterior(desde)
        nueva_desde = mes_ant.replace(day=desde.day)
        nueva_hasta = nueva_desde + delta
        st.session_state['f_desde'] = nueva_desde
        st.session_state['f_hasta'] = nueva_hasta
        st.rerun()

    if c4.button("Año Completo", key="btn_anio"):
        st.session_state['f_desde'] = date(hoy.year, 1, 1)
        st.session_state['f_hasta'] = hoy
        st.rerun()

    # Date inputs — key separada del valor guardado en session_state
    desde_val = st.sidebar.date_input(
        "Desde",
        value=st.session_state['f_desde'],
        key='_input_desde',
        format="DD/MM/YYYY"
    )
    hasta_val = st.sidebar.date_input(
        "Hasta",
        value=st.session_state['f_hasta'],
        key='_input_hasta',
        format="DD/MM/YYYY"
    )

    # Sincronizar si el usuario editó manualmente
    if desde_val != st.session_state['f_desde']:
        st.session_state['f_desde'] = desde_val
    if hasta_val != st.session_state['f_hasta']:
        st.session_state['f_hasta'] = hasta_val

    # ── PERÍODO COMPARATIVO ───────────────────────────────────────────────────
    st.sidebar.markdown("### Comparativo")

    comparar = st.sidebar.checkbox(
        "Activar comparación",
        value=st.session_state.get('f_comparar', False),
        key='_chk_comparar'
    )
    st.session_state['f_comparar'] = comparar

    if comparar:
        cc1, cc2 = st.sidebar.columns(2)
        cc3, _ = st.sidebar.columns(2)

        if cc1.button("Mes Ant.", key="btn_comp_mes_ant"):
            mes_ant = _mes_anterior(hoy)
            st.session_state['f_comp_desde'] = _primer_dia_mes(mes_ant)
            st.session_state['f_comp_hasta'] = _ultimo_dia_mes(mes_ant)
            st.rerun()

        if cc2.button("Mismo Per. Mes Ant.", key="btn_comp_mismo"):
            desde = st.session_state['f_desde']
            hasta = st.session_state['f_hasta']
            delta = hasta - desde
            mes_ant = _mes_anterior(desde)
            nueva_desde = mes_ant.replace(day=desde.day)
            st.session_state['f_comp_desde'] = nueva_desde
            st.session_state['f_comp_hasta'] = nueva_desde + delta
            st.rerun()

        if cc3.button("Mismo Per. Año Ant.", key="btn_comp_anio_ant"):
            desde = st.session_state['f_desde']
            hasta = st.session_state['f_hasta']
            st.session_state['f_comp_desde'] = desde.replace(year=desde.year - 1)
            st.session_state['f_comp_hasta'] = hasta.replace(year=hasta.year - 1)
            st.rerun()

        comp_desde_val = st.sidebar.date_input(
            "Comp. Desde",
            value=st.session_state['f_comp_desde'],
            key='_input_comp_desde',
            format="DD/MM/YYYY"
        )
        comp_hasta_val = st.sidebar.date_input(
            "Comp. Hasta",
            value=st.session_state['f_comp_hasta'],
            key='_input_comp_hasta',
            format="DD/MM/YYYY"
        )

        if comp_desde_val != st.session_state['f_comp_desde']:
            st.session_state['f_comp_desde'] = comp_desde_val
        if comp_hasta_val != st.session_state['f_comp_hasta']:
            st.session_state['f_comp_hasta'] = comp_hasta_val

    # ── RETORNAR DICT DE FILTROS ──────────────────────────────────────────────
    return {
        'vendedores':  st.session_state['f_vendedores'],
        'fecha_desde': st.session_state['f_desde'],
        'fecha_hasta': st.session_state['f_hasta'],
        'comparar':    st.session_state['f_comparar'],
        'comp_desde':  st.session_state.get('f_comp_desde'),
        'comp_hasta':  st.session_state.get('f_comp_hasta'),
    }


def aplicar_filtros_fac(df_fac: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    """Filtra df_fac por vendedores y rango de fechas principal."""
    if df_fac is None or df_fac.empty:
        return pd.DataFrame()
    mask = (
        (df_fac['Nombre Vendedor'].isin(filtros['vendedores'])) &
        (df_fac['Fecha de emisión'] >= pd.Timestamp(filtros['fecha_desde'])) &
        (df_fac['Fecha de emisión'] <= pd.Timestamp(filtros['fecha_hasta']))
    )
    return df_fac[mask].copy()


def aplicar_filtros_cot(df_cot: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    """Filtra df_cot por vendedores y rango de fechas principal."""
    if df_cot is None or df_cot.empty:
        return pd.DataFrame()
    mask = (
        (df_cot['Nombre Vendedor'].isin(filtros['vendedores'])) &
        (df_cot['Fecha emisión'] >= pd.Timestamp(filtros['fecha_desde'])) &
        (df_cot['Fecha emisión'] <= pd.Timestamp(filtros['fecha_hasta']))
    )
    return df_cot[mask].copy()


def aplicar_filtros_fac_comp(df_fac: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    """Filtra df_fac por vendedores y rango de fechas COMPARATIVO."""
    if not filtros.get('comparar'):
        return pd.DataFrame()
    if df_fac is None or df_fac.empty:
        return pd.DataFrame()
    if not filtros.get('comp_desde') or not filtros.get('comp_hasta'):
        return pd.DataFrame()
    mask = (
        (df_fac['Nombre Vendedor'].isin(filtros['vendedores'])) &
        (df_fac['Fecha de emisión'] >= pd.Timestamp(filtros['comp_desde'])) &
        (df_fac['Fecha de emisión'] <= pd.Timestamp(filtros['comp_hasta']))
    )
    return df_fac[mask].copy()


def aplicar_filtros_cot_comp(df_cot: pd.DataFrame, filtros: dict) -> pd.DataFrame:
    """Filtra df_cot por vendedores y rango de fechas COMPARATIVO."""
    if not filtros.get('comparar'):
        return pd.DataFrame()
    if df_cot is None or df_cot.empty:
        return pd.DataFrame()
    if not filtros.get('comp_desde') or not filtros.get('comp_hasta'):
        return pd.DataFrame()
    mask = (
        (df_cot['Nombre Vendedor'].isin(filtros['vendedores'])) &
        (df_cot['Fecha emisión'] >= pd.Timestamp(filtros['comp_desde'])) &
        (df_cot['Fecha emisión'] <= pd.Timestamp(filtros['comp_hasta']))
    )
    return df_cot[mask].copy()