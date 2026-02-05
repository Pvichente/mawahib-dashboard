import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Mawahib Dashboard", layout="wide", page_icon="🥤")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Convertimos la URL de edición a una URL de exportación CSV
sheet_id = "1jOgf6WFuJSKiAUpY-8JyU0x_8OGI_8X9Lt6QYF1L7_4"
sheet_name = "Base%20simulada%20para%20dashboard"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data(ttl=600)  # Se actualiza cada 10 minutos
def load_data():
    df = pd.read_csv(url)
    # Limpieza básica de fechas
    if 'registration date' in df.columns:
        df['registration date'] = pd.to_datetime(df['registration date'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("Mawahib Project")
st.sidebar.markdown("Collaboration: **Fundes & Coca-Cola**")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/c/ce/Coca-Cola_logo.svg", width=100)

st.sidebar.header("Filtros de Control")
# Filtro por tipo de negocio
negocios = st.sidebar.multiselect(
    "Giro del Negocio:",
    options=df['Type of business'].unique(),
    default=df['Type of business'].unique()
)

# Filtro por educación
educacion = st.sidebar.multiselect(
    "Nivel Educativo:",
    options=df['Education'].unique(),
    default=df['Education'].unique()
)

# Aplicar filtros
df_filtered = df[(df['Type of business'].isin(negocios)) & (df['Education'].isin(educacion))]

# --- CUERPO DEL DASHBOARD ---
st.title("🥤 Dashboard Estratégico Mawahib")
st.markdown("Monitoreo de capacitación para tenderos y microempresarios (Vía Enably)")

# KPIs Principales
col1, col2, col3, col4 = st.columns(4)
col1.metric("Usuarios Registrados", f"{df_filtered['Registered'].sum()}")
col2.metric("Usuarios Activos", f"{df_filtered['Active'].sum()}")
col3.metric("Graduados", f"{df_filtered['Graduate'].sum()}")
col4.metric("Total Lecciones", f"{df_filtered['Number of lessons'].sum():,}")

st.divider()

# Gráficos Superiores
c1, c2 = st.columns(2)

with c1:
    st.subheader("Tendencia de Registro (Mawahib)")
    df_trend = df_filtered.groupby('registration date')[['Registered', 'Active']].sum().reset_index()
    fig_trend = px.line(df_trend, x='registration date', y=['Registered', 'Active'],
                        labels={'value': 'Cantidad', 'registration date': 'Fecha'},
                        color_discrete_sequence=["#F40009", "#000000"]) # Colores Coca-Cola
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    st.subheader("Ubicación de Microempresarios")
    # Streamlit usa columnas 'lat' y 'lon' o 'latitud'/'longitud'
    map_data = df_filtered[['Latitud', 'Longitud']].rename(columns={'Latitud': 'lat', 'Longitud': 'lon'})
    st.map(map_data)

# Gráficos Inferiores
c3, c4 = st.columns([2, 1])

with c3:
    st.subheader("Avance por Nivel Educativo")
    fig_edu = px.bar(df_filtered.groupby('Education')['Number of lessons'].sum().reset_index(),
                     x='Education', y='Number of lessons',
                     color_discrete_sequence=['#F40009'])
    st.plotly_chart(fig_edu, use_container_width=True)

with c4:
    st.subheader("Distribución por Género")
    fig_sex = px.pie(df_filtered, names='Sex', hole=0.4,
                     color_discrete_sequence=['#F40009', '#545454'])
    st.plotly_chart(fig_sex, use_container_width=True)

# Tabla de detalle
with st.expander("Ver detalle de datos filtrados"):
    st.dataframe(df_filtered[['Username', 'Type of business', 'Education', 'Number of lessons', 'Champion']])
