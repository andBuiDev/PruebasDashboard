import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Dashboard", page_icon="✨", layout="wide")

# --- INYECCIÓN DE CSS PREMIUM ---
st.markdown("""
<style>
    /* Ocultar el menú de hamburguesa y footer por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Configuración Base tipográfica */
    .stApp {
        background-color: #f4f7f6;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Estilos para las tarjetas de KPIs (Glassmorphism & Shadows) */
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        color: #2c3e50;
        font-weight: 800;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #7f8c8d;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, white 0%, #fbfbfb 100%);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        border: 1px solid rgba(255, 255, 255, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Ajuste para los separadores */
    hr {
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        border: 0;
        height: 1px;
        background: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.1), rgba(0,0,0,0));
    }
    
    /* Sombras para los contenedores de gráficos */
    .stPlotlyChart {
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05);
        padding: 15px;
        border: 1px solid #f0f0f0;
    }
    
    /* Input UI Style */
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 8px;
        border: 1px solid #dfe6e9;
    }
</style>
""", unsafe_allow_html=True)


# Función Cerebro: Detección Automática de Temática
@st.cache_data
def detect_dataset_theme(columns):
    cols_text = " ".join(columns).lower()
    
    # 1. Medio Ambiente / Vehículos
    if any(word in cols_text for word in ['co2', 'emission', 'fuel', 'engine', 'make', 'model', 'car']):
        return "Medio Ambiente & Vehículos", "🌿", px.colors.sequential.Greens, "#2ca02c"
    
    # 2. Finanzas / Ventas / Dinero
    elif any(word in cols_text for word in ['sale', 'price', 'cost', 'revenue', 'profit', 'money', 'discount', 'usd']):
        return "Finanzas & Ventas", "💰", px.colors.sequential.Tealgrn, "#17becf"
    
    # 3. Salud / Personas / Demografía
    elif any(word in cols_text for word in ['patient', 'health', 'disease', 'age', 'gender', 'name', 'user']):
        return "Salud & Demografía", "🏥", px.colors.sequential.Magenta, "#d62728"
    
    # 4. Tema Default Corporativo
    else:
        return "Datos Corporativos", "📊", px.colors.sequential.Blues, "#1f77b4"


# --- SIDEBAR: Zona de Carga UX ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8653/8653130.png", width=60)
    st.header("📂 Carga de Datos")
    uploaded_file = st.file_uploader("Arrastra tu archivo CSV aquí:", type=["csv"])
    sep = st.selectbox("Formato del separador:", [",", ";", r"\t"])
    st.markdown("---")
    st.markdown("✨ *Sube un archivo y mira cómo el diseño se adapta a tus datos por arte de magia.*")


# --- CUERPO PRINCIPAL ---
if uploaded_file is not None:
    try:
        # Extraer el Nombre del Archivo y darle formato de Título
        # Ej: "emisiones_co2.csv" -> "Emisiones Co2"
        file_name_clean = uploaded_file.name.replace(".csv", "").replace("_", " ").title()
        
        # Leer el CSV
        df = pd.read_csv(uploaded_file, sep=sep)
        
        # Detectar el Tema con las Heríticas
        tema_nombre, emoji, paleta_colores, color_base = detect_dataset_theme(df.columns.tolist())
        
        # Encabezado Dinámico Principal
        st.markdown(f"<h1 style='text-align: center; color: #2c3e50;'>{emoji} Análisis Dinámico:<br> {file_name_clean}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #7f8c8d; font-size:18px; margin-top:-10px;'>Tema de Interfaz: <span style='color:{color_base}; font-weight:bold;'>{tema_nombre}</span> • Registros: <b>{len(df):,}</b></p>", unsafe_allow_html=True)
        
        st.divider()
        
        # Preparación de las Columnas Numéricas vs Categóricas
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # --- TARJETAS PREMIUM KPIs ---
        st.markdown("<h3 style='color: #2c3e50; font-weight: 700;'>🎯 Resumen Clave</h3>", unsafe_allow_html=True)
        
        if len(numeric_cols) > 0:
            display_cols = numeric_cols[:4] # Mostrar hasta 4 columnas de impacto numérico
            cols = st.columns(len(display_cols))
            
            for i, col_name in enumerate(display_cols):
                with cols[i]:
                    avg_val = df[col_name].mean()
                    # Formateo si tiene decimales largos
                    if pd.isna(avg_val):
                        formatted_val = "N/A"
                    elif avg_val.is_integer():
                        formatted_val = f"{int(avg_val):,}"
                    else:
                        formatted_val = f"{avg_val:,.2f}"
                        
                    st.metric(f"Promedio {col_name}", formatted_val)
        else:
            st.warning("El dataset no tiene columnas numéricas puras detectables.")
            
        st.divider()

        # --- MOTOR DE CREACIÓN VISUAL (Self-Service) ---
        st.markdown(f"<h3 style='color: #2c3e50; font-weight: 700;'>{emoji} Generador de Gráficos Mágicos</h3>", unsafe_allow_html=True)
        
        col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
        
        with col_opt1:
            chart_type = st.selectbox("Forma del Gráfico", ["Dispersión (Scatter)", "Barras (Bar)", "Histograma", "Cajas (Box)"])
        with col_opt2:
            x_axis = st.selectbox("Eje Principal X", options=df.columns.tolist())
        with col_opt3:
            # Sugerir columna Y numérica preferentemente si es que existen
            y_axis_options = numeric_cols if numeric_cols else df.columns.tolist()
            y_axis = st.selectbox("Eje Secundario Y", options=y_axis_options)
        with col_opt4:
            color_opt = st.selectbox("Aplicar Color / Agrupar por", ["Ninguno"] + categorical_cols)

        color_val = color_opt if color_opt != "Ninguno" else None
        
        # Lienzo del gráfico inyectando la Paleta Smart
        try:
            if chart_type == "Dispersión (Scatter)":
                fig = px.scatter(df, x=x_axis, y=y_axis, color=color_val, 
                                 title=f"<b>Análisis:</b> Interacción de {y_axis} vs {x_axis}", 
                                 color_continuous_scale=paleta_colores, 
                                 color_discrete_sequence=[color_base, "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"] if not color_val else px.colors.qualitative.Pastel)
                                 
            elif chart_type == "Barras (Bar)":
                fig = px.bar(df, x=x_axis, y=y_axis, color=color_val, 
                             title=f"<b>Comparativa:</b> Suma Total de {y_axis} dado {x_axis}",
                             color_continuous_scale=paleta_colores, 
                             color_discrete_sequence=[color_base, "#1f77b4", "#ff7f0e"] if not color_val else px.colors.qualitative.Pastel)
                             
            elif chart_type == "Histograma":
                fig = px.histogram(df, x=x_axis, color=color_val, 
                                   title=f"<b>Frecuencia:</b> Distribución del {x_axis}",
                                   color_discrete_sequence=[color_base, "#1f77b4", "#ff7f0e"] if not color_val else px.colors.qualitative.Pastel)
                                   
            elif chart_type == "Cajas (Box)":
                fig = px.box(df, x=x_axis, y=y_axis, color=color_val, 
                             title=f"<b>Validación Outliers:</b> Comportamiento de {y_axis} por {x_axis}",
                             color_discrete_sequence=[color_base, "#1f77b4", "#ff7f0e"] if not color_val else px.colors.qualitative.Pastel)
            
            # --- MEJORANDO EL DISEÑO DE LA LIBRERIA PLOTLY ---
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", 
                paper_bgcolor="rgba(0,0,0,0)",
                font_family="Segoe UI",
                title_font_size=20,
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                title_x=0.01,
                margin=dict(l=40, r=40, t=60, b=40),
            )
            # Acostar la leyenda si aplica color
            if color_val:
                fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            else:
                fig.update_layout(showlegend=False)

            # Insertamos el gráfico y un poco de espacio
            st.write("")
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"⚠️ Elige otra combinación de columnas (Algunos gráficos matemáticos piden ejes de números obligatorios). Error: {e}")

        st.write("")
        st.write("")
        # Resumen de Datos Raw con Expansor Integrado a los Estilos
        with st.expander("🔍 Explorar Datos Crudos Originales (Primeras 100 filas)"):
            st.dataframe(df.head(100), use_container_width=True)

    except Exception as e:
        st.error(f"🛑 Error severo intentando leer tu Excel/CSV. ¿Es un documento dañado o su separador distinto a la coma? Detalle: {e}")
        
else:
    # Pantalla de Bienvenida (Placeholder vacío)
    st.markdown("""
        <div style='text-align: center; padding: 60px 20px; background-color: white; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border: 2px dashed #bdc3c7;'>
            <h1 style='color: #2c3e50; font-weight:800;'>🚀 El Smart Dashboard está Esperando</h1>
            <p style='color: #7f8c8d; font-size:18px;'>Sube un archivo de ventas, de médicos o de autos... Yo adaptaré sola mi paleta de colores, mis tarjetas y mi título a tu data.</p>
        </div>
    """, unsafe_allow_html=True)
