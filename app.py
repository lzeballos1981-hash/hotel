import streamlit as st
import pymysql
import pandas as pd

# Configurar p¨¢gina
st.set_page_config(page_title="Hotel App", layout="wide")

# T¨ªtulo
st.title("?? Sistema Hotelero - Versi¨®n Simple")

# Funci¨®n de conexi¨®n
def get_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="hotel",
            charset='utf8mb4'
        )
        return conn
    except Exception as e:
        st.error(f"Error de conexi¨®n: {str(e)}")
        return None

# Men¨²
menu = st.sidebar.selectbox(
    "Men¨²",
    ["Dashboard", "Habitaciones", "Clientes", "Reservas"]
)

if menu == "Dashboard":
    st.header("?? Dashboard")
    
    conn = get_connection()
    if conn:
        try:
            # Obtener conteos b¨¢sicos
            with conn.cursor() as cursor:
                # Total habitaciones
                cursor.execute("SELECT COUNT(*) as total FROM habitacion")
                total_hab = cursor.fetchone()[0]
                
                # Total clientes
                cursor.execute("SELECT COUNT(*) as total FROM cliente")
                total_cli = cursor.fetchone()[0]
                
                # Total reservas
                cursor.execute("SELECT COUNT(*) as total FROM reserva")
                total_res = cursor.fetchone()[0]
            
            # Mostrar m¨¦tricas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Habitaciones", total_hab)
            with col2:
                st.metric("Clientes", total_cli)
            with col3:
                st.metric("Reservas", total_res)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            conn.close()
    else:
        st.info("Configura la conexi¨®n a la base de datos")

elif menu == "Habitaciones":
    st.header("??? Habitaciones")
    
    conn = get_connection()
    if conn:
        try:
            query = """
                SELECT h.numero_habitacion, h.piso, h.precio,
                       th.tipo_cama, th.capacidad
                FROM habitacion h
                JOIN tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
                ORDER BY h.piso, h.numero_habitacion
            """
            
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # Filtros simples
                st.subheader("Filtrar por capacidad")
                capacidad = st.slider("Capacidad m¨ªnima", 1, 10, 1)
                df_filtrado = df[df['capacidad'] >= capacidad]
                st.write(f"Mostrando {len(df_filtrado)} habitaciones")
            else:
                st.info("No hay habitaciones registradas")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            conn.close()

elif menu == "Clientes":
    st.header("?? Clientes")
    
    conn = get_connection()
    if conn:
        try:
            query = "SELECT * FROM cliente ORDER BY nombre LIMIT 50"
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # Estad¨ªsticas
                st.subheader("Estad¨ªsticas")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Clientes", len(df))
                with col2:
                    st.metric("Con CI registrado", df['ci'].notna().sum())
            else:
                st.info("No hay clientes registrados")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            conn.close()

elif menu == "Reservas":
    st.header("?? Reservas")
    
    conn = get_connection()
    if conn:
        try:
            query = """
                SELECT r.id_reserva, c.nombre, r.fecha_entrada, 
                       r.fecha_salida, r.estado_reserva, r.total
                FROM reserva r
                JOIN cliente c ON r.id_cliente = c.id_cliente
                ORDER BY r.fecha_entrada DESC
                LIMIT 20
            """
            
            df = pd.read_sql(query, conn)
            
            if not df.empty:
                # Filtro por estado
                estados = df['estado_reserva'].unique()
                estado_seleccionado = st.multiselect(
                    "Filtrar por estado",
                    estados,
                    default=estados
                )
                
                if estado_seleccionado:
                    df_filtrado = df[df['estado_reserva'].isin(estado_seleccionado)]
                    st.dataframe(df_filtrado, use_container_width=True)
                    
                    # Resumen
                    st.subheader("Resumen")
                    col1, col2 = st.columns(2)
                    with col1:
                        ingresos = df_filtrado['total'].sum()
                        st.metric("Ingresos totales", f"${ingresos:,.2f}")
                    with col2:
                        promedio = df_filtrado['total'].mean()
                        st.metric("Promedio por reserva", f"${promedio:,.2f}")
                else:
                    st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay reservas registradas")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            conn.close()

# Pie de p¨¢gina
st.divider()
st.caption("Sistema Hotelero v1.0 - Desarrollado con Streamlit")