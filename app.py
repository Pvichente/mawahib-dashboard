import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. Configuración de la página
st.set_page_config(
    page_title="Mawahib Dashboard | FUNDES",
    layout="wide",
    page_icon="📊"
)

# 2. Estilo personalizado (Fondo blanco, letras negras e inversión de colores)
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    h1, h2, h3, p, span, label {
        color: #000000 !important;
    }
    [data-testid="stMetricValue"] {
        color: #007bff !important;
    }
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-weight: bold;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Conexión a Google Sheets
sheet_id = "1jOgf6WFuJSKiAUpY-8JyU0x_8OGI_8X9Lt6QYF1L7_4"
sheet_name = "Base%20simulada%20para%20dashboard"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(url)
    if 'registration date' in df.columns:
        df['registration date'] = pd.to_datetime(df['registration date'], dayfirst=True, errors='coerce')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"⚠️ Error al conectar con Google Sheets: {e}")
    st.stop()

# 4. Sidebar - Logo de FUNDES y Filtros
logo_path = "logo_fundes.png"
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=180)
else:
    # Backup: Logo oficial de FUNDES desde la web
    st.sidebar.image("https://fundes.org/wp-content/uploads/2021/04/logo-fundes.png", width=180)

st.sidebar.title("Mawahib Project")
st.sidebar.header("🔍 Filters")

if not df['registration date'].isnull().all():
    min_date = df['registration date'].min().date()
    max_date = df['registration date'].max().date()
    date_range = st.sidebar.date_input("Registration period:", [min_date, max_date])

tipos_negocio = st.sidebar.multiselect(
    "Business Focus::",
    options=sorted(df['Type of business'].unique()),
    default=df['Type of business'].unique()
)

mask = (df['Type of business'].isin(tipos_negocio))
if not df['registration date'].isnull().all() and len(date_range) == 2:
    mask = mask & (df['registration date'].dt.date >= date_range[0]) & (df['registration date'].dt.date <= date_range[1])

df_filtered = df[mask]

# 5. Cuerpo Principal
st.title("📊 Mawahib: Monitoring & Analytics Dashboard")
st.subheader("User lesson progress dashboard")

# KPIs corregidos
col1, col2, col3, col4 = st.columns(4)
col1.metric("Registered", f"{df_filtered['Registered'].sum()}")
col2.metric("Active", f"{df_filtered['Active'].sum()}")
col3.metric("Graduate", f"{df_filtered['Graduate'].sum()}")
col4.metric("Lessons complete", f"{df_filtered['Number of lessons'].sum():,}")

st.divider()

# Gráficos e indicadores visuales
c1, c2 = st.columns([3, 2])
with c1:
    st.subheader("📈 User Trends")
    df_trend = df_filtered.groupby('registration date')[['Registered', 'Active']].sum().reset_index()
    fig_trend = px.line(df_trend, x='registration date', y=['Registered', 'Active'],
                        color_discrete_sequence=["#007bff", "#545454"],
                        template="plotly_white")
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("📍 User location")
    map_data = df_filtered[['Latitud', 'Longitud']].dropna().rename(columns={'Latitud': 'lat', 'Longitud': 'lon'})
    st.map(map_data)

st.divider()

c3, c4 = st.columns(2)
with c3:
    st.subheader("📊 Distribution by Type of Business")
    biz_data = df_filtered['Type of business'].value_counts().reset_index()
    biz_data.columns = ['Type of business', 'Count']
    fig_biz = px.bar(biz_data, x='Count', y='Type of business', 
                     orientation='h', color_discrete_sequence=["#007bff"],
                     template="plotly_white")
    st.plotly_chart(fig_biz, use_container_width=True)

with c4:
    st.subheader("🎓 Educational Level")
    edu_data = df_filtered.groupby('Education')['Number of lessons'].sum().reset_index().sort_values('Number of lessons', ascending=False)
    fig_edu = px.bar(edu_data, x='Number of lessons', y='Education', 
                     orientation='h', color_discrete_sequence=['#545454'],
                     template="plotly_white")
    st.plotly_chart(fig_edu, use_container_width=True)

with st.expander("📋 See full data table"):
    st.dataframe(df_filtered.drop(columns=['Latitud', 'Longitud'], errors='ignore'), use_container_width=True)
