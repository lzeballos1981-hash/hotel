import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

# Configurar p芍gina
st.set_page_config(
    page_title="Sistema Hotelero",
    page_icon="??",
    layout="wide"
)

# Funci車n de conexi車n a la base de datos
@st.cache_resource
def get_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",  # Cambia seg迆n tu configuraci車n
            password="",  # Cambia seg迆n tu configuraci車n
            database="hotel",
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.Error as err:
        st.error(f"Error de conexi車n: {err}")
        return None

# Ejecutar consultas SQL
def ejecutar_query(query, params=None, fetch=True):
    conn = get_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch and query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.rowcount
    except pymysql.Error as err:
        st.error(f"Error en consulta: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

# Convertir resultados a DataFrame
def query_to_df(query, params=None):
    result = ejecutar_query(query, params)
    if result:
        return pd.DataFrame(result)
    return pd.DataFrame()

# Inicializar estado de sesi車n
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "Dashboard"

# Resto del c車digo se mantiene igual desde aqu赤...
# [Todo el resto del c車digo que te envi谷 anteriormente permanece igual]
# Solo aseg迆rate de que las funciones de conexi車n usen pymysql