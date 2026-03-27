import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Dashboard Emisiones CO2 Canadá", page_icon="🌎", layout="wide")

# Función para cargar y limpiar datos
@st.cache_data
def load_data():
    file_path = 'Emissions_Canada_CO2.csv'
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_csv(file_path)
    # Limpieza basada en el notebook original
    df = df.drop_duplicates()
    df.columns = [
        'Make', 'Model', 'Vehicle_Class', 'Engine_Size_L', 'Cylinders',
        'Transmission', 'Fuel_Type', 'Fuel_Consumption_City_L_100km',
        'Fuel_Consumption_Hwy_L_100km', 'Fuel_Consumption_Comb_L_100km',
        'Fuel_Consumption_Comb_mpg', 'CO2_Emissions_g_km'
    ]
    return df

st.title("🌎 Dashboard de Análisis de Vehículos y Emisiones de CO2")
st.markdown("Basado en el conjunto de datos de emisiones de CO2 de vehículos en Canadá.")

df = load_data()

if df is None:
    st.error("⚠️ No se encontró el archivo `Emissions_Canada_CO2.csv`. Por favor, colócalo en la misma carpeta que este script para continuar.")
else:
    # --- SIDEBAR ---
    st.sidebar.header("🔍 Filtros")
    
    # Filtro de Marcas
    all_makes = df['Make'].unique().tolist()
    # Por defecto seleccionamos solo algunas marcas para no saturar los gráficos iniciales
    selected_makes = st.sidebar.multiselect("Selecciona la Marca:", all_makes, default=all_makes[:5])
    
    # Filtro de Tipo de Combustible
    all_fuels = df['Fuel_Type'].unique().tolist()
    selected_fuels = st.sidebar.multiselect("Selecciona el Tipo de Combustible:", all_fuels, default=all_fuels)
    
    # Aplicar filtros
    if selected_makes and selected_fuels:
        df_filtered = df[(df['Make'].isin(selected_makes)) & (df['Fuel_Type'].isin(selected_fuels))]
    else:
        df_filtered = df.copy()

    # --- KPIs ---
    st.subheader("📊 Métricas Generales (según selección)")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Vehículos", len(df_filtered))
    with col2:
        avg_co2 = round(df_filtered['CO2_Emissions_g_km'].mean(), 2)
        st.metric("Promedio CO2 (g/km)", avg_co2)
    with col3:
        avg_engine = round(df_filtered['Engine_Size_L'].mean(), 2)
        st.metric("Promedio Tamaño Motor (L)", avg_engine)
    with col4:
        avg_consumo = round(df_filtered['Fuel_Consumption_Comb_L_100km'].mean(), 2)
        st.metric("Consumo Promedio (L/100km)", avg_consumo)
        
    st.divider()

    # --- GRÁFICOS INTERACTIVOS ---
    st.subheader("📈 Exploración Visual")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Gráfico 1: Emisiones de CO2 por Marca usando un Box Plot
        fig_make_co2 = px.box(df_filtered, x='Make', y='CO2_Emissions_g_km', color='Make',
                              title="Distribución de Emisiones de CO2 por Marca",
                              labels={'Make': 'Marca', 'CO2_Emissions_g_km': 'Emisiones CO2 (g/km)'})
        fig_make_co2.update_layout(showlegend=False, xaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_make_co2, use_container_width=True)
        
    with col_chart2:
        # Gráfico 2: Relación Tamaño Motor vs Emisiones Scatter Plot
        fig_engine_co2 = px.scatter(df_filtered, x='Engine_Size_L', y='CO2_Emissions_g_km',
                                    color='Fuel_Type', hover_data=['Make', 'Model'],
                                    title="Tamaño del Motor vs Emisiones de CO2",
                                    labels={'Engine_Size_L': 'Tamaño del Motor (L)', 'CO2_Emissions_g_km': 'Emisiones CO2 (g/km)', 'Fuel_Type': 'Combustible'})
        st.plotly_chart(fig_engine_co2, use_container_width=True)

    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        # Gráfico 3: Cantidad de vehículos por tipo de combustible (similar al notebook original)
        fuel_counts = df_filtered['Fuel_Type'].value_counts().reset_index()
        fuel_counts.columns = ['Fuel_Type', 'Count']
        fig_fuel = px.bar(fuel_counts, x='Fuel_Type', y='Count', color='Fuel_Type',
                          title="Cantidad de Vehículos por Tipo de Combustible",
                          labels={'Fuel_Type': 'Tipo de Combustible', 'Count': 'Cantidad de Vehículos'})
        fig_fuel.update_layout(showlegend=False)
        st.plotly_chart(fig_fuel, use_container_width=True)
        
    with col_chart4:
        # Gráfico 4: Histograma Distribución del consumo de combustible
        fig_hist = px.histogram(df_filtered, x='Fuel_Consumption_Comb_L_100km', nbins=30,
                                title="Distribución de Consumo Combinado (L/100km)",
                                labels={'Fuel_Consumption_Comb_L_100km': 'Consumo Combinado (L/100km)'})
        fig_hist.update_layout(showlegend=False)
        st.plotly_chart(fig_hist, use_container_width=True)
        
    # --- TABLA DE DATOS ---
    with st.expander("Ver Datos Originales Filtrados"):
        st.dataframe(df_filtered)
