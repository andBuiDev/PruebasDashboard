import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Auto-EDA Dashboard", page_icon="📈", layout="wide")

st.title("📈 Auto-EDA Dashboard Dinámico")
st.markdown("Sube cualquier archivo CSV para generar un dashboard interactivo al instante.")

# --- SIDEBAR: Configuración y subida de datos ---
st.sidebar.header("📂 Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu archivo CSV aquí", type=["csv"])
sep = st.sidebar.selectbox("Selecciona el separador del archivo:", [",", ";", r"\t"])

if uploaded_file is not None:
    try:
        # Leer el archivo con el separador escogido
        df = pd.read_csv(uploaded_file, sep=sep)
        
        # Identificar tipos de columnas (numéricas y categóricas)
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        st.success(f"Archivo cargado exitosamente: {uploaded_file.name}")
        
        # --- RESUMEN DE DATOS ---
        with st.expander("Ver Resumen de Datos Originales", expanded=False):
            st.write(f"**Dimensiones del dataset:** {df.shape[0]} filas y {df.shape[1]} columnas.")
            st.dataframe(df.head(100)) # Mostramos una muestra
        
        # --- KPIs DINÁMICOS ---
        st.subheader("📊 Métricas Generales Automáticas")
        
        if len(numeric_cols) > 0:
            # Tomamos hasta 4 columnas numéricas para mostrar promedio
            display_cols = numeric_cols[:4]
            cols = st.columns(len(display_cols) + 1)
            
            with cols[0]:
                st.metric("Total de Filas (Registros)", len(df))
            
            for i, col_name in enumerate(display_cols):
                with cols[i+1]:
                    avg_val = round(df[col_name].mean(), 2)
                    st.metric(f"Promedio de {col_name}", avg_val)
        else:
            st.metric("Total de Filas (Registros)", len(df))
            st.warning("No se encontraron columnas numéricas para calcular promedios automáticos.")
        
        st.divider()

        # --- CONSTRUCTOR DE GRÁFICOS (Self-Service BI) ---
        st.subheader("🎨 Generador de Gráficos (Self-Service BI)")
        st.markdown("Elige cómo graficar tus datos. Selecciona qué columnas quieres comparar para que el gráfico se dibuje al instante.")
        
        # Opciones interactivas para el usuario
        col_opt1, col_opt2, col_opt3, col_opt4 = st.columns(4)
        
        with col_opt1:
            chart_type = st.selectbox("Tipo de Gráfico", ["Dispersión (Scatter)", "Barras (Bar)", "Histograma", "Cajas (Box)"])
        with col_opt2:
            x_axis = st.selectbox("Eje X", options=df.columns.tolist())
        with col_opt3:
            # Recomendar Y numérico si es posible, pero dejar elegir
            y_axis_options = df.columns.tolist()
            y_axis = st.selectbox("Eje Y", options=y_axis_options, index=1 if len(y_axis_options)>1 else 0)
        with col_opt4:
            color_opt = st.selectbox("Color (Agrupar por - Opcional)", ["Ninguno"] + categorical_cols)

        # Configurar la variable de color para plotly
        color_val = color_opt if color_opt != "Ninguno" else None
        
        # Desplegar el gráfico
        plot_container = st.container()
        
        try:
            with plot_container:
                if chart_type == "Dispersión (Scatter)":
                    fig = px.scatter(df, x=x_axis, y=y_axis, color=color_val, 
                                     title=f"Relación entre {y_axis} y {x_axis}")
                elif chart_type == "Barras (Bar)":
                    # Usamos bar de Plotly tal cual (aplica suma por defecto si hay múltiples entadas)
                    fig = px.bar(df, x=x_axis, y=y_axis, color=color_val, 
                                 title=f"Gráfico de Barras de {y_axis} por {x_axis}")
                elif chart_type == "Histograma":
                    fig = px.histogram(df, x=x_axis, color=color_val, 
                                       title=f"Distribución (Histograma) de {x_axis}")
                elif chart_type == "Cajas (Box)":
                    fig = px.box(df, x=x_axis, y=y_axis, color=color_val, 
                                 title=f"Distribución (Boxplot) de {y_axis} agrupado por {x_axis}")
                
                if color_val:
                    fig.update_layout(showlegend=True)
                
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"No se pudo generar el gráfico con la combinación seleccionada. Algunos gráficos requieren que uno de los ejes sea estrictamente numérico. ¡Intenta cambiar los ejes! (Error técnico: {e})")

    except Exception as e:
        st.error(f"Ocurrió un error al intentar leer el archivo. Selecciona un separador distinto o verifica que sea un CSV válido. (Error técnico: {e})")
else:
    st.info("👈 Utiliza el botón en la barra lateral izquierda para subir tu archivo CSV y generar el dashboard mágico.")
