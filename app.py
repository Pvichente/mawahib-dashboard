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

# Estilo personalizado para usar los colores de Coca-Cola
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #F40009;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexión a Google Sheets (Exportación a CSV)
sheet_id = "1jOgf6WFuJSKiAUpY-8JyU0x_8OGI_8X9Lt6QYF1L7_4"
sheet_name = "Base%20simulada%20para%20dashboard"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=600)  # Actualización automática cada 10 minutos
def load_data():
    # Leemos el CSV directamente desde la URL de Google Sheets
    df = pd.read_csv(url)
    
    # CORRECCIÓN DE FECHA: 
    # Usamos dayfirst=True para el formato 28/05/2026 y errors='coerce' por seguridad
    if 'registration date' in df.columns:
        df['registration date'] = pd.to_datetime(df['registration date'], dayfirst=True, errors='coerce')
    
    return df

# Control de errores en la carga
try:
    df = load_data()
except Exception as e:
    st.error(f"⚠️ Error al conectar con Google Sheets: {e}")
    st.stop()

# 3. Sidebar - Filtros y Branding
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/c/ce/Coca-Cola_logo.svg", width=150)
st.sidebar.title("Proyecto Mawahib")
st.sidebar.info("Colaboración estratégica: Fundes & Coca-Cola para el empoderamiento de PyMEs.") [cite: 4]

st.sidebar.header("🔍 Filtros")

# Filtro de fecha dinámico
if not df['registration date'].isnull().all():
    min_date = df['registration date'].min().date()
    max_date = df['registration date'].max().date()
    date_range = st.sidebar.date_input("Periodo de registro:", [min_date, max_date])
else:
    st.sidebar.warning("No se detectaron fechas válidas.")

# Filtros de categorías
tipos_negocio = st.sidebar.multiselect(
    "Giro del Negocio:",
    options=sorted(df['Type of business'].unique()),
    default=df['Type of business'].unique()
)

niveles_edu = st.sidebar.multiselect(
    "Nivel Educativo:",
    options=sorted(df['Education'].unique()),
    default=df['Education'].unique()
)

# Aplicación de filtros al dataframe
mask = (df['Type of business'].isin(tipos_negocio)) & (df['Education'].isin(niveles_edu))
if not df['registration date'].isnull().all() and len(date_range) == 2:
    mask = mask & (df['registration date'].dt.date >= date_range[0]) & (df['registration date'].dt.date <= date_range[1])

df_filtered = df[mask]

# 4. Cuerpo Principal del Dashboard
st.title("🥤 Mawahib: Monitoring & Analytics Dashboard")
st.subheader("Control de avance educativo - Micro, Pequeños y Medianos Empresarios") [cite: 4]

# Fila de KPIs (Scorecards)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Usuarios Registrados", f"{df_filtered['Registered'].sum()}")
col2.metric("Usuarios Activos", f"{df_filtered['Active'].sum()}")
col3.metric("Graduados", f"{df_filtered['Graduate'].sum()}")
col4.metric("Lecciones Completadas", f"{df_filtered['Number of lessons'].sum():,}")

st.divider()

# Gráficos Superiores
c1, c2 = st.columns([3, 2])

with c1:
    st.subheader("📈 Tendencia de Usuarios (Active vs Registered)")
    df_trend = df_filtered.groupby('registration date')[['Registered', 'Active']].sum().reset_index()
    fig_trend = px.line(df_trend, x='registration date', y=['Registered', 'Active'],
                        color_discrete_sequence=["#F40009", "#000000"],
                        labels={'value': 'Cantidad', 'registration date': 'Fecha'})
    fig_trend.update_layout(legend_title_text='Estado')
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("📍 Ubicación de Tenderos")
    # Streamlit requiere nombres específicos para el mapa: lat y lon
    map_data = df_filtered[['Latitud', 'Longitud']].dropna().rename(columns={'Latitud': 'lat', 'Longitud': 'lon'})
    st.map(map_data)

st.divider()

# Gráficos Inferiores
c3, c4 = st.columns(2)

with c3:
    st.subheader("🎓 Avance por Nivel Educativo")
    edu_data = df_filtered.groupby('Education')['Number of lessons'].sum().reset_index().sort_values('Number of lessons', ascending=False)
    fig_edu = px.bar(edu_data, x='Number of lessons', y='Education', 
                     orientation='h', color_discrete_sequence=['#F40009'])
    st.plotly_chart(fig_edu, use_container_width=True)

with c4:
    st.subheader("👥 Distribución por Género")
    fig_sex = px.pie(df_filtered, names='Sex', hole=0.4,
                     color_discrete_sequence=['#F40009', '#000000', '#545454'])
    st.plotly_chart(fig_sex, use_container_width=True)

# 5. Tabla de Detalle y Descarga
with st.expander("📋 Ver tabla de datos completa"):
    st.dataframe(df_filtered.drop(columns=['Latitud', 'Longitud'], errors='ignore'), use_container_width=True)
    
    # Botón para descargar CSV de lo filtrado
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar reporte filtrado (CSV)",
        data=csv,
        file_name='reporte_mawahib_filtrado.csv',
        mime='text/csv',
    )
