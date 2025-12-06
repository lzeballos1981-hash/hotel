# -*- coding: utf-8 -*-
"""
Sistema Hotelero - Streamlit App
Autor: Tu Nombre
"""

import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import sys

# Configurar encoding
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# Configurar p芍gina
st.set_page_config(
    page_title="Sistema Hotelero",
    page_icon="??",
    layout="wide"
)

# Funci車n de conexi車n a la base de datos
@st.cache_resource
def init_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",  # Cambia seg迆n tu configuraci車n
            password="",  # Cambia seg迆n tu configuraci車n
            database="hotel",
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn
    except pymysql.Error as err:
        st.error(f"Error de conexi車n: {err}")
        return None

# Obtener conexi車n
conn = init_connection()

# Ejecutar consultas SQL
def run_query(query, params=None):
    try:
        if conn:
            with conn.cursor() as cur:
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    result = cur.fetchall()
                    return result
                else:
                    conn.commit()
                    return cur.rowcount
    except pymysql.Error as e:
        st.error(f"Error en consulta: {e}")
        return None
    except Exception as e:
        st.error(f"Error general: {e}")
        return None

# Convertir resultados a DataFrame
def get_dataframe(query, params=None):
    result = run_query(query, params)
    if result:
        # Convertir bytes a strings si es necesario
        df = pd.DataFrame(result)
        # Limpiar columnas de texto
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
        return df
    return pd.DataFrame()

# Inicializar estado de sesi車n
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "dashboard"

# T赤tulo principal
st.title("?? Sistema de Gesti車n Hotelera")

# Men迆 lateral
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2421/2421129.png", width=100)
    st.title("Men迆 Principal")
    
    # Botones del men迆
    if st.button("?? Dashboard", use_container_width=True):
        st.session_state.pagina_actual = "dashboard"
    
    if st.button("?? Reservas", use_container_width=True):
        st.session_state.pagina_actual = "reservas"
    
    if st.button("??? Habitaciones", use_container_width=True):
        st.session_state.pagina_actual = "habitaciones"
    
    if st.button("?? Clientes", use_container_width=True):
        st.session_state.pagina_actual = "clientes"
    
    if st.button("?? Pagos", use_container_width=True):
        st.session_state.pagina_actual = "pagos"
    
    if st.button("?? Transporte", use_container_width=True):
        st.session_state.pagina_actual = "transporte"
    
    st.divider()
    st.caption(f"Sesi車n: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# P芍GINA: DASHBOARD
if st.session_state.pagina_actual == "dashboard":
    st.header("?? Panel de Control")
    
    # M谷tricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_reservas = get_dataframe("SELECT COUNT(*) as total FROM reserva")
        st.metric("Total Reservas", 
                 total_reservas.iloc[0]['total'] if not total_reservas.empty else 0)
    
    with col2:
        habitaciones_total = get_dataframe("SELECT COUNT(*) as total FROM habitacion")
        st.metric("Total Habitaciones", 
                 habitaciones_total.iloc[0]['total'] if not habitaciones_total.empty else 0)
    
    with col3:
        clientes_total = get_dataframe("SELECT COUNT(*) as total FROM cliente")
        st.metric("Total Clientes", 
                 clientes_total.iloc[0]['total'] if not clientes_total.empty else 0)
    
    with col4:
        ingresos = get_dataframe("SELECT SUM(total) as total FROM reserva WHERE estado_reserva != 'cancelada'")
        ingreso_val = ingresos.iloc[0]['total'] if not ingresos.empty and ingresos.iloc[0]['total'] else 0
        st.metric("Ingresos Totales", f"${ingreso_val:,.2f}")
    
    st.divider()
    
    # Gr芍ficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Reservas por Estado")
        estados = get_dataframe("""
            SELECT estado_reserva, COUNT(*) as cantidad 
            FROM reserva 
            GROUP BY estado_reserva
        """)
        if not estados.empty:
            fig = px.pie(estados, values='cantidad', names='estado_reserva')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Habitaciones por Tipo")
        tipos = get_dataframe("""
            SELECT th.tipo_cama, COUNT(*) as cantidad
            FROM habitacion h
            JOIN tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
            GROUP BY th.tipo_cama
        """)
        if not tipos.empty:
            fig = px.bar(tipos, x='tipo_cama', y='cantidad', color='tipo_cama')
            st.plotly_chart(fig, use_container_width=True)
    
    # 迆ltimas reservas
    st.subheader("迆ltimas Reservas")
    ultimas_reservas = get_dataframe("""
        SELECT r.id_reserva, c.nombre, r.fecha_entrada, r.fecha_salida, 
               r.estado_reserva, r.total
        FROM reserva r
        JOIN cliente c ON r.id_cliente = c.id_cliente
        ORDER BY r.fecha_reserva DESC
        LIMIT 5
    """)
    
    if not ultimas_reservas.empty:
        st.dataframe(ultimas_reservas, use_container_width=True)
    else:
        st.info("No hay reservas registradas")

# P芍GINA: RESERVAS
elif st.session_state.pagina_actual == "reservas":
    st.header("?? Gesti車n de Reservas")
    
    tab1, tab2 = st.tabs(["Nueva Reserva", "Ver Reservas"])
    
    with tab1:
        st.subheader("Crear Nueva Reserva")
        
        # Formulario simple
        with st.form("form_reserva"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre del Cliente")
                ci = st.text_input("CI del Cliente")
                fecha_entrada = st.date_input("Fecha de Entrada", value=date.today())
            
            with col2:
                telefono = st.text_input("Tel谷fono")
                fecha_salida = st.date_input("Fecha de Salida", value=date.today())
                numero_personas = st.number_input("N迆mero de Personas", min_value=1, max_value=10, value=2)
            
            # Buscar habitaciones disponibles
            if fecha_entrada and fecha_salida and fecha_salida > fecha_entrada:
                if st.form_submit_button("Buscar Habitaciones Disponibles"):
                    habitaciones = get_dataframe("""
                        SELECT h.id_habitacion, h.numero_habitacion, h.precio,
                               th.tipo_cama, th.capacidad
                        FROM habitacion h
                        JOIN tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
                        WHERE th.capacidad >= %s
                        AND h.id_habitacion NOT IN (
                            SELECT id_habitacion FROM reserva 
                            WHERE (%s < fecha_salida AND %s > fecha_entrada)
                            AND estado_reserva IN ('confirmada', 'en curso')
                        )
                    """, (numero_personas, fecha_entrada, fecha_salida))
                    
                    if not habitaciones.empty:
                        st.success(f"Se encontraron {len(habitaciones)} habitaciones disponibles")
                        st.dataframe(habitaciones)
                        
                        # Seleccionar habitaci車n
                        habitacion_selec = st.selectbox(
                            "Seleccionar Habitaci車n:",
                            habitaciones.apply(lambda x: f"Habitaci車n {x['numero_habitacion']} - ${x['precio']}/noche", axis=1)
                        )
                        
                        if st.button("Confirmar Reserva"):
                            st.success("Reserva creada exitosamente!")
                    else:
                        st.warning("No hay habitaciones disponibles para esas fechas")
    
    with tab2:
        st.subheader("Todas las Reservas")
        
        reservas = get_dataframe("""
            SELECT r.id_reserva, c.nombre, c.ci, h.numero_habitacion,
                   r.fecha_entrada, r.fecha_salida, r.estado_reserva, r.total
            FROM reserva r
            JOIN cliente c ON r.id_cliente = c.id_cliente
            JOIN habitacion h ON r.id_habitacion = h.id_habitacion
            ORDER BY r.fecha_entrada DESC
        """)
        
        if not reservas.empty:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                estado_filtro = st.multiselect(
                    "Filtrar por estado:",
                    reservas['estado_reserva'].unique(),
                    default=reservas['estado_reserva'].unique()
                )
            
            # Aplicar filtro
            if estado_filtro:
                reservas_filtradas = reservas[reservas['estado_reserva'].isin(estado_filtro)]
                st.dataframe(reservas_filtradas, use_container_width=True)
            else:
                st.dataframe(reservas, use_container_width=True)
        else:
            st.info("No hay reservas registradas")

# P芍GINA: HABITACIONES
elif st.session_state.pagina_actual == "habitaciones":
    st.header("??? Gesti車n de Habitaciones")
    
    # Mostrar todas las habitaciones
    habitaciones = get_dataframe("""
        SELECT h.id_habitacion, h.numero_habitacion, h.piso, h.precio,
               th.tipo_cama, th.capacidad, th.wifi, th.tv, th.banio
        FROM habitacion h
        JOIN tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
        ORDER BY h.piso, h.numero_habitacion
    """)
    
    if not habitaciones.empty:
        # Crear tarjetas
        cols = st.columns(3)
        for idx, hab in habitaciones.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    st.subheader(f"#{hab['numero_habitacion']}")
                    st.write(f"**Piso:** {hab['piso']}")
                    st.write(f"**Tipo:** {hab['tipo_cama']}")
                    st.write(f"**Capacidad:** {hab['capacidad']} personas")
                    st.write(f"**Precio:** ${hab['precio']:.2f}/noche")
                    
                    # Amenities
                    amenities = []
                    if hab['wifi']: amenities.append("WiFi")
                    if hab['tv']: amenities.append("TV")
                    if hab['banio']: amenities.append("Ba?o")
                    
                    if amenities:
                        st.caption(f"Amenities: {', '.join(amenities)}")
        
        st.divider()
        st.subheader("Vista Tabular")
        st.dataframe(habitaciones, use_container_width=True)
    else:
        st.info("No hay habitaciones registradas")

# P芍GINA: CLIENTES
elif st.session_state.pagina_actual == "clientes":
    st.header("?? Gesti車n de Clientes")
    
    tab1, tab2 = st.tabs(["Lista de Clientes", "Nuevo Cliente"])
    
    with tab1:
        clientes = get_dataframe("""
            SELECT c.*, ct.telefono, ct.correo_electronico
            FROM cliente c
            LEFT JOIN contacto ct ON c.id_cliente = ct.id_cliente
            ORDER BY c.nombre
        """)
        
        if not clientes.empty:
            st.dataframe(clientes, use_container_width=True)
        else:
            st.info("No hay clientes registrados")
    
    with tab2:
        with st.form("form_cliente"):
            st.subheader("Registrar Nuevo Cliente")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre *")
                apellido_paterno = st.text_input("Apellido Paterno")
                ci = st.text_input("CI *")
            
            with col2:
                apellido_materno = st.text_input("Apellido Materno")
                telefono = st.text_input("Tel谷fono")
                email = st.text_input("Email")
            
            if st.form_submit_button("Guardar Cliente"):
                if nombre and ci:
                    # Insertar cliente
                    run_query("""
                        INSERT INTO cliente (nombre, ci, apellido_paterno, apellido_materno)
                        VALUES (%s, %s, %s, %s)
                    """, (nombre, ci, apellido_paterno, apellido_materno))
                    
                    st.success("Cliente registrado exitosamente")
                    st.rerun()
                else:
                    st.error("Nombre y CI son obligatorios")

# P芍GINA: PAGOS
elif st.session_state.pagina_actual == "pagos":
    st.header("?? Gesti車n de Pagos")
    
    pagos = get_dataframe("""
        SELECT p.id_pago, r.id_reserva, c.nombre as cliente,
               p.monto, p.fecha_pago, p.referencia
        FROM pago p
        JOIN reserva r ON p.id_reserva = r.id_reserva
        JOIN cliente c ON r.id_cliente = c.id_cliente
        ORDER BY p.fecha_pago DESC
    """)
    
    if not pagos.empty:
        # M谷tricas
        col1, col2 = st.columns(2)
        with col1:
            total = pagos['monto'].sum()
            st.metric("Total Recaudado", f"${total:,.2f}")
        with col2:
            promedio = pagos['monto'].mean()
            st.metric("Promedio por Pago", f"${promedio:,.2f}")
        
        st.dataframe(pagos, use_container_width=True)
    else:
        st.info("No hay pagos registrados")

# P芍GINA: TRANSPORTE
elif st.session_state.pagina_actual == "transporte":
    st.header("?? Gesti車n de Transporte")
    
    rutas = get_dataframe("""
        SELECT * FROM ruta ORDER BY origen, destino
    """)
    
    if not rutas.empty:
        for _, ruta in rutas.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{ruta['origen']} ↙ {ruta['destino']}**")
                    st.caption(f"Distancia: {ruta['distancia']} km")
                with col2:
                    st.write(f"Tiempo: {ruta['tiempo_estimado']}")
                    st.write(f"Tarifa: ${ruta['tarifa']:.2f}")
                with col3:
                    if st.button("Reservar", key=f"reserva_{ruta['id_ruta']}"):
                        st.info("Funcionalidad de reserva en desarrollo")
        
        st.divider()
        st.subheader("Agregar Nueva Ruta")
        
        with st.form("form_ruta"):
            col1, col2 = st.columns(2)
            with col1:
                origen = st.text_input("Origen")
                distancia = st.number_input("Distancia (km)", min_value=0.0)
            with col2:
                destino = st.text_input("Destino")
                tarifa = st.number_input("Tarifa ($)", min_value=0.0)
            
            if st.form_submit_button("Guardar Ruta"):
                if origen and destino:
                    run_query("""
                        INSERT INTO ruta (origen, destino, distancia, tarifa)
                        VALUES (%s, %s, %s, %s)
                    """, (origen, destino, distancia, tarifa))
                    st.success("Ruta agregada exitosamente")
                    st.rerun()
    else:
        st.info("No hay rutas registradas")

# Footer
st.divider()
st.caption(f"? 2024 Sistema Hotelero | 迆ltima actualizaci車n: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Cerrar conexi車n al final
if conn:
    conn.close()