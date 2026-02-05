import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración de la página
st.set_page_config(
    page_title="Mawahib Dashboard | Fundes & Coca-Cola",
    layout="wide",
    page_icon="🥤"
)

# 2. Estilo personalizado (Fondo blanco, letras negras)
st.markdown("""
    <style>
    /* Fondo principal blanco */
    .stApp {
        background-color: #ffffff;
    }
    /* Color de texto general negro */
    h1, h2, h3, p, span, label {
        color: #000000 !important;
    }
    /* Estilo de los cuadros de métricas (KPIs) */
    [data-testid="stMetricValue"] {
        color: #F40009 !important; /* Valor en rojo Coca-Cola para resaltar */
    }
    [data-testid="stMetricLabel"] {
        color: #000000 !important; /* Etiquetas en negro */
        font-weight: bold;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
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

# 4. Sidebar - Filtros
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/c/ce/Coca-Cola_logo.svg", width=150)
st.sidebar.title("Proyecto Mawahib")

st.sidebar.header("🔍 Filtros")

# Filtro de fecha
if not df['registration date'].isnull().all():
    min_date = df['registration date'].min().date()
    max_date = df['registration date'].max().date()
    date_range = st.sidebar.date_input("Periodo de registro:", [min_date, max_date])
else:
    st.sidebar.warning("No se detectaron fechas válidas.")

tipos_negocio = st.sidebar.multiselect(
    "Giro del Negocio:",
    options=sorted(df['Type of business'].unique()),
    default=df['Type of business'].unique()
)

# Aplicación de filtros
mask = (df['Type of business'].isin(tipos_negocio))
if not df['registration date'].isnull().all() and len(date_range) == 2:
    mask = mask & (df['registration date'].dt.date >= date_range[0]) & (df['registration date'].dt.date <= date_range[1])

df_filtered = df[mask]

# 5. Cuerpo Principal
st.title("🥤 Mawahib: Monitoring & Analytics Dashboard")
st.subheader("Control de avance educativo - Micro, Pequeños y Medianos Empresarios")

# KPIs Ajustados según requerimiento
col1, col2, col3, col4 = st.columns(4)
col1.metric("Registered", f"{df_filtered['Registered'].sum()}")
col2.metric("Active", f"{df_filtered['Active'].sum()}")
col3.metric("Graduate", f"{df_filtered['Graduate'].sum()}")
col4.metric("Lessons complete", f"{df_filtered['Number of lessons'].sum():,}")

st.divider()

# Gráficos
c1, c2 = st.columns([3, 2])

with c1:
    st.subheader("📈 Tendencia de Usuarios")
    df_trend = df_filtered.groupby('registration date')[['Registered', 'Active']].sum().reset_index()
    fig_trend = px.line(df_trend, x='registration date', y=['Registered', 'Active'],
                        color_discrete_sequence=["#F40009", "#545454"],
                        template="plotly_white")
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("📍 Ubicación de Tenderos")
    map_data = df_filtered[['Latitud', 'Longitud']].dropna().rename(columns={'Latitud': 'lat', 'Longitud': 'lon'})
    st.map(map_data)

st.divider()

c3, c4 = st.columns(2)

with c3:
    # Nuevo gráfico: Distribución de frecuencias de Type of Business (Horizontal)
    st.subheader("📊 Distribution by Type of Business")
    biz_data = df_filtered['Type of business'].value_counts().reset_index()
    biz_data.columns = ['Type of business', 'Count']
    fig_biz = px.bar(biz_data, x='Count', y='Type of business', 
                     orientation='h', color_discrete_sequence=['#F40009'],
                     template="plotly_white")
    st.plotly_chart(fig_biz, use_container_width=True)

with c4:
    st.subheader("🎓 Avance por Nivel Educativo")
    edu_data = df_filtered.groupby('Education')['Number of lessons'].sum().reset_index().sort_values('Number of lessons', ascending=False)
    fig_edu = px.bar(edu_data, x='Number of lessons', y='Education', 
                     orientation='h', color_discrete_sequence=['#545454'],
                     template="plotly_white")
    st.plotly_chart(fig_edu, use_container_width=True)

# Tabla de detalle
with st.expander("📋 Ver tabla de datos completa"):
    st.dataframe(df_filtered.drop(columns=['Latitud', 'Longitud'], errors='ignore'), use_container_width=True)
