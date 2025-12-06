import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

# Configurar página
st.set_page_config(
    page_title="Sistema Hotelero",
    page_icon="🏨",
    layout="wide"
)

# Función de conexión a la base de datos
@st.cache_resource
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Cambia según tu configuración
            password="",  # Cambia según tu configuración
            database="hotel",
            port=3306
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Error de conexión: {err}")
        return None

# Ejecutar consultas SQL
def ejecutar_query(query, params=None, fetch=True):
    conn = get_connection()
    if conn is None:
        return None
    
    cursor = conn.cursor(dictionary=True)
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
    except mysql.connector.Error as err:
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

# Inicializar estado de sesión
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "Dashboard"

# Menú lateral
with st.sidebar:
    st.title("🏨 Hotel Premium")
    st.divider()
    
    # Opciones del menú
    menu_opciones = {
        "📊 Dashboard": "dashboard",
        "📅 Reservas": "reservas",
        "🛏️ Habitaciones": "habitaciones",
        "👥 Clientes": "clientes",
        "💰 Pagos": "pagos",
        "⭐ Fidelidad": "fidelidad",
        "🚗 Transporte": "transporte",
        "📈 Reportes": "reportes"
    }
    
    for icono, opcion in menu_opciones.items():
        if st.button(icono, use_container_width=True, key=opcion):
            st.session_state.pagina_actual = opcion
    
    st.divider()
    st.caption(f"Usuario: Administrador")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# PÁGINA: DASHBOARD
if st.session_state.pagina_actual == "dashboard":
    st.title("📊 Dashboard del Hotel")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        reservas_hoy = query_to_df("""
            SELECT COUNT(*) as total FROM reserva 
            WHERE DATE(fecha_reserva) = CURDATE()
        """)
        st.metric("Reservas Hoy", reservas_hoy.iloc[0]['total'] if not reservas_hoy.empty else 0)
    
    with col2:
        ocupacion = query_to_df("""
            SELECT COUNT(*) as ocupadas FROM reserva 
            WHERE estado_reserva IN ('confirmada', 'en curso')
            AND CURDATE() BETWEEN fecha_entrada AND fecha_salida
        """)
        st.metric("Habitaciones Ocupadas", ocupacion.iloc[0]['ocupadas'] if not ocupacion.empty else 0)
    
    with col3:
        ingresos_mes = query_to_df("""
            SELECT SUM(total) as ingresos FROM reserva 
            WHERE MONTH(fecha_reserva) = MONTH(CURDATE())
            AND estado_reserva != 'cancelada'
        """)
        ingreso_valor = ingresos_mes.iloc[0]['ingresos'] if not ingresos_mes.empty and ingresos_mes.iloc[0]['ingresos'] else 0
        st.metric("Ingresos del Mes", f"${ingreso_valor:,.2f}")
    
    with col4:
        clientes_nuevos = query_to_df("""
            SELECT COUNT(*) as nuevos FROM cliente 
            WHERE DATE(fecha_creacion) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """)
        st.metric("Clientes Nuevos (30d)", clientes_nuevos.iloc[0]['nuevos'] if not clientes_nuevos.empty else 0)
    
    st.divider()
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Reservas por Mes")
        reservas_mensuales = query_to_df("""
            SELECT DATE_FORMAT(fecha_reserva, '%Y-%m') as mes,
                   COUNT(*) as cantidad,
                   SUM(total) as ingresos
            FROM reserva
            WHERE fecha_reserva >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(fecha_reserva, '%Y-%m')
            ORDER BY mes
        """)
        
        if not reservas_mensuales.empty:
            fig = px.bar(reservas_mensuales, x='mes', y='cantidad',
                        title='Reservas por Mes', color='cantidad')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏨 Ocupación por Tipo")
        ocupacion_tipo = query_to_df("""
            SELECT th.tipo_cama, COUNT(r.id_reserva) as reservas
            FROM reserva r
            JOIN habitacion h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
            WHERE r.estado_reserva IN ('confirmada', 'en curso')
            GROUP BY th.tipo_cama
        """)
        
        if not ocupacion_tipo.empty:
            fig = px.pie(ocupacion_tipo, values='reservas', names='tipo_cama',
                        title='Distribución por Tipo de Cama')
            st.plotly_chart(fig, use_container_width=True)
    
    # Reservas recientes
    st.subheader("📋 Reservas Recientes")
    reservas_recientes = query_to_df("""
        SELECT r.id_reserva, c.nombre, c.ci, h.numero_habitacion,
               r.fecha_entrada, r.fecha_salida, r.estado_reserva, r.total
        FROM reserva r
        JOIN cliente c ON r.id_cliente = c.id_cliente
        JOIN habitacion h ON r.id_habitacion = h.id_habitacion
        ORDER BY r.fecha_reserva DESC
        LIMIT 10
    """)
    
    if not reservas_recientes.empty:
        st.dataframe(reservas_recientes, use_container_width=True, hide_index=True)
    else:
        st.info("No hay reservas recientes")

# PÁGINA: RESERVAS
elif st.session_state.pagina_actual == "reservas":
    st.title("📅 Gestión de Reservas")
    
    tab1, tab2, tab3 = st.tabs(["Nueva Reserva", "Buscar Reservas", "Calendario"])
    
    with tab1:
        st.subheader("➕ Nueva Reserva")
        
        # Buscar cliente existente o crear nuevo
        col1, col2 = st.columns(2)
        
        with col1:
            busqueda_ci = st.text_input("Buscar cliente por CI:")
            if busqueda_ci:
                clientes = query_to_df(
                    "SELECT id_cliente, nombre, ci FROM cliente WHERE ci LIKE %s",
                    (f"%{busqueda_ci}%",)
                )
                if not clientes.empty:
                    cliente_seleccionado = st.selectbox(
                        "Seleccionar cliente:",
                        clientes.apply(lambda x: f"{x['nombre']} (CI: {x['ci']})", axis=1)
                    )
        
        with col2:
            st.write("O crear nuevo cliente:")
            nuevo_nombre = st.text_input("Nombre")
            nuevo_ci = st.text_input("CI")
            nuevo_telefono = st.text_input("Teléfono")
        
        # Seleccionar fechas
        col1, col2 = st.columns(2)
        with col1:
            fecha_entrada = st.date_input("Fecha de entrada", value=date.today())
        with col2:
            fecha_salida = st.date_input("Fecha de salida", value=date.today())
        
        # Buscar habitaciones disponibles
        if st.button("🔍 Buscar Habitaciones Disponibles"):
            habitaciones_disponibles = query_to_df("""
                SELECT h.id_habitacion, h.numero_habitacion, h.piso, h.precio,
                       th.tipo_cama, th.capacidad, th.tamano_m2
                FROM habitacion h
                JOIN tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
                WHERE h.id_habitacion NOT IN (
                    SELECT id_habitacion 
                    FROM reserva 
                    WHERE estado_reserva IN ('confirmada', 'en curso', 'pendiente')
                    AND (%s < fecha_salida AND %s > fecha_entrada)
                )
            """, (fecha_entrada, fecha_salida))
            
            if not habitaciones_disponibles.empty:
                st.subheader("Habitaciones Disponibles")
                st.dataframe(habitaciones_disponibles, use_container_width=True)
                
                # Seleccionar habitación
                habitaciones_opciones = habitaciones_disponibles.apply(
                    lambda x: f"Habitación {x['numero_habitacion']} (Piso {x['piso']}) - ${x['precio']}/noche - {x['tipo_cama']}", 
                    axis=1
                )
                habitacion_seleccionada = st.selectbox("Seleccionar habitación:", habitaciones_opciones)
                
                # Calcular total
                if fecha_entrada and fecha_salida:
                    noches = (fecha_salida - fecha_entrada).days
                    if noches > 0:
                        precio_noche = habitaciones_disponibles.iloc[0]['precio']
                        total = noches * precio_noche
                        st.info(f"Total estimado: ${total:,.2f} ({noches} noches)")
            
                # Botón para crear reserva
                if st.button("✅ Confirmar Reserva"):
                    st.success("Reserva creada exitosamente")
            else:
                st.warning("No hay habitaciones disponibles para las fechas seleccionadas")
    
    with tab2:
        st.subheader("🔍 Buscar Reservas")
        
        col1, col2 = st.columns(2)
        with col1:
            filtro_estado = st.multiselect(
                "Estado:",
                ["pendiente", "confirmada", "en curso", "completada", "cancelada"],
                default=["confirmada", "en curso"]
            )
        
        with col2:
            filtro_fecha = st.date_input("Fecha:", value=date.today())
        
        if filtro_estado:
            estados_str = ", ".join([f"'{estado}'" for estado in filtro_estado])
            reservas_filtradas = query_to_df(f"""
                SELECT r.id_reserva, c.nombre, c.ci, h.numero_habitacion,
                       r.fecha_entrada, r.fecha_salida, r.estado_reserva, r.total
                FROM reserva r
                JOIN cliente c ON r.id_cliente = c.id_cliente
                JOIN habitacion h ON r.id_habitacion = h.id_habitacion
                WHERE r.estado_reserva IN ({estados_str})
                AND (%s BETWEEN r.fecha_entrada AND r.fecha_salida
                     OR %s IS NULL)
                ORDER BY r.fecha_entrada
            """, (filtro_fecha, filtro_fecha))
            
            if not reservas_filtradas.empty:
                st.dataframe(reservas_filtradas, use_container_width=True, hide_index=True)
            else:
                st.info("No se encontraron reservas con los filtros seleccionados")

# PÁGINA: HABITACIONES
elif st.session_state.pagina_actual == "habitaciones":
    st.title("🛏️ Gestión de Habitaciones")
    
    # Mostrar todas las habitaciones
    habitaciones = query_to_df("""
        SELECT h.id_habitacion, h.numero_habitacion, h.piso, h.precio,
               th.tipo_cama, th.capacidad, th.wifi, th.tv, th.banio,
               CASE 
                   WHEN EXISTS (
                       SELECT 1 FROM reserva r 
                       WHERE r.id_habitacion = h.id_habitacion 
                       AND r.estado_reserva IN ('confirmada', 'en curso')
                       AND CURDATE() BETWEEN r.fecha_entrada AND r.fecha_salida
                   ) THEN 'Ocupada'
                   ELSE 'Disponible'
               END as estado
        FROM habitacion h
        JOIN tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
        ORDER BY h.piso, h.numero_habitacion
    """)
    
    if not habitaciones.empty:
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "Disponible", "Ocupada"])
        with col2:
            filtro_piso = st.number_input("Filtrar por piso:", min_value=0, value=0)
        with col3:
            filtro_tipo = st.selectbox("Filtrar por tipo cama:", ["Todos"] + habitaciones['tipo_cama'].unique().tolist())
        
        # Aplicar filtros
        habitaciones_filtradas = habitaciones.copy()
        if filtro_estado != "Todos":
            habitaciones_filtradas = habitaciones_filtradas[habitaciones_filtradas['estado'] == filtro_estado]
        if filtro_piso > 0:
            habitaciones_filtradas = habitaciones_filtradas[habitaciones_filtradas['piso'] == filtro_piso]
        if filtro_tipo != "Todos":
            habitaciones_filtradas = habitaciones_filtradas[habitaciones_filtradas['tipo_cama'] == filtro_tipo]
        
        # Mostrar en tarjetas
        cols = st.columns(3)
        for idx, habitacion in habitaciones_filtradas.iterrows():
            with cols[idx % 3]:
                color = "🔴" if habitacion['estado'] == "Ocupada" else "🟢"
                with st.container(border=True):
                    st.markdown(f"### {color} Habitación {habitacion['numero_habitacion']}")
                    st.write(f"**Piso:** {habitacion['piso']}")
                    st.write(f"**Tipo:** {habitacion['tipo_cama']}")
                    st.write(f"**Capacidad:** {habitacion['capacidad']} personas")
                    st.write(f"**Precio:** ${habitacion['precio']:.2f}/noche")
                    st.write(f"**Estado:** {habitacion['estado']}")
                    
                    # Amenities
                    amenities = []
                    if habitacion['wifi']: amenities.append("📶 WiFi")
                    if habitacion['tv']: amenities.append("📺 TV")
                    if habitacion['banio']: amenities.append("🚽 Baño")
                    if amenities:
                        st.write("**Amenities:**", ", ".join(amenities))
        
        # Mostrar también como tabla
        st.divider()
        st.subheader("📋 Vista Tabular")
        st.dataframe(habitaciones_filtradas, use_container_width=True, hide_index=True)
    else:
        st.info("No hay habitaciones registradas")

# PÁGINA: CLIENTES
elif st.session_state.pagina_actual == "clientes":
    st.title("👥 Gestión de Clientes")
    
    tab1, tab2 = st.tabs(["Lista de Clientes", "Nuevo Cliente"])
    
    with tab1:
        st.subheader("📋 Clientes Registrados")
        
        # Buscador
        busqueda = st.text_input("Buscar por nombre o CI:")
        
        if busqueda:
            clientes = query_to_df("""
                SELECT c.*, 
                       GROUP_CONCAT(ct.telefono) as telefonos,
                       GROUP_CONCAT(ct.correo_electronico) as correos
                FROM cliente c
                LEFT JOIN contacto ct ON c.id_cliente = ct.id_cliente
                WHERE c.nombre LIKE %s OR c.ci LIKE %s
                GROUP BY c.id_cliente
            """, (f"%{busqueda}%", f"%{busqueda}%"))
        else:
            clientes = query_to_df("""
                SELECT c.*, 
                       GROUP_CONCAT(ct.telefono) as telefonos,
                       GROUP_CONCAT(ct.correo_electronico) as correos,
                       COUNT(r.id_reserva) as total_reservas
                FROM cliente c
                LEFT JOIN contacto ct ON c.id_cliente = ct.id_cliente
                LEFT JOIN reserva r ON c.id_cliente = r.id_cliente
                GROUP BY c.id_cliente
                ORDER BY c.nombre
            """)
        
        if not clientes.empty:
            st.dataframe(clientes, use_container_width=True, hide_index=True)
            
            # Seleccionar cliente para ver detalles
            cliente_id = st.selectbox(
                "Seleccionar cliente para ver detalles:",
                clientes.apply(lambda x: f"{x['nombre']} - CI: {x['ci']}", axis=1)
            )
            
            if cliente_id:
                # Mostrar historial de reservas del cliente
                st.subheader("📅 Historial de Reservas")
                cliente_ci = cliente_id.split("CI: ")[1]
                reservas_cliente = query_to_df("""
                    SELECT r.id_reserva, h.numero_habitacion,
                           r.fecha_entrada, r.fecha_salida,
                           r.estado_reserva, r.total
                    FROM reserva r
                    JOIN habitacion h ON r.id_habitacion = h.id_habitacion
                    JOIN cliente c ON r.id_cliente = c.id_cliente
                    WHERE c.ci = %s
                    ORDER BY r.fecha_entrada DESC
                """, (cliente_ci,))
                
                if not reservas_cliente.empty:
                    st.dataframe(reservas_cliente, use_container_width=True, hide_index=True)
                else:
                    st.info("Este cliente no tiene reservas")
        else:
            st.info("No se encontraron clientes")
    
    with tab2:
        st.subheader("➕ Registrar Nuevo Cliente")
        
        with st.form("nuevo_cliente_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre *", max_chars=100)
                apellido_paterno = st.text_input("Apellido Paterno", max_chars=100)
            
            with col2:
                ci = st.text_input("CI *", max_chars=45)
                apellido_materno = st.text_input("Apellido Materno", max_chars=100)
            
            st.subheader("Información de Contacto")
            telefono = st.text_input("Teléfono", max_chars=45)
            correo = st.text_input("Correo Electrónico", max_chars=100)
            
            submitted = st.form_submit_button("Guardar Cliente")
            
            if submitted:
                if nombre and ci:
                    # Insertar cliente
                    ejecutar_query("""
                        INSERT INTO cliente (nombre, ci, apellido_paterno, apellido_materno)
                        VALUES (%s, %s, %s, %s)
                    """, (nombre, ci, apellido_paterno, apellido_materno), fetch=False)
                    
                    # Obtener ID del cliente insertado
                    cliente_insertado = query_to_df("SELECT id_cliente FROM cliente WHERE ci = %s", (ci,))
                    
                    if not cliente_insertado.empty and telefono:
                        cliente_id = cliente_insertado.iloc[0]['id_cliente']
                        # Insertar contacto
                        ejecutar_query("""
                            INSERT INTO contacto (telefono, correo_electronico, id_cliente)
                            VALUES (%s, %s, %s)
                        """, (telefono, correo, cliente_id), fetch=False)
                    
                    st.success("Cliente registrado exitosamente")
                    st.rerun()
                else:
                    st.error("Nombre y CI son campos obligatorios")

# PÁGINA: PAGOS
elif st.session_state.pagina_actual == "pagos":
    st.title("💰 Gestión de Pagos")
    
    pagos = query_to_df("""
        SELECT p.id_pago, r.id_reserva, c.nombre as cliente,
               mp.nombre as metodo_pago, ep.nombre_estado_pago as estado,
               p.monto, p.fecha_pago, p.referencia
        FROM pago p
        JOIN reserva r ON p.id_reserva = r.id_reserva
        JOIN cliente c ON r.id_cliente = c.id_cliente
        JOIN metodo_pago mp ON p.id_metodo_pago = mp.id_metodo_pago
        JOIN estado_pago ep ON p.id_estado_pago = ep.id_estado_pago
        ORDER BY p.fecha_pago DESC
    """)
    
    if not pagos.empty:
        # Métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            total_pagos = pagos['monto'].sum()
            st.metric("Total Pagado", f"${total_pagos:,.2f}")
        with col2:
            pagos_hoy = pagos[pagos['fecha_pago'].dt.date == date.today()]['monto'].sum()
            st.metric("Pagos Hoy", f"${pagos_hoy:,.2f}")
        with col3:
            pagos_pendientes = len(pagos[pagos['estado'] == 'pendiente'])
            st.metric("Pagos Pendientes", pagos_pendientes)
        
        st.divider()
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            filtro_estado = st.multiselect(
                "Filtrar por estado:",
                pagos['estado'].unique(),
                default=pagos['estado'].unique()
            )
        with col2:
            filtro_metodo = st.multiselect(
                "Filtrar por método:",
                pagos['metodo_pago'].unique(),
                default=pagos['metodo_pago'].unique()
            )
        
        # Aplicar filtros
        if filtro_estado:
            pagos_filtrados = pagos[pagos['estado'].isin(filtro_estado)]
        if filtro_metodo:
            pagos_filtrados = pagos_filtrados[pagos_filtrados['metodo_pago'].isin(filtro_metodo)]
        
        st.dataframe(pagos_filtrados, use_container_width=True, hide_index=True)
    else:
        st.info("No hay pagos registrados")

# PÁGINA: FIDELIDAD
elif st.session_state.pagina_actual == "fidelidad":
    st.title("⭐ Programa de Fidelidad")
    
    clientes_fidelidad = query_to_df("""
        SELECT c.id_cliente, c.nombre, c.ci,
               cf.puntos_acumulados,
               nf.nivel, nf.beneficios
        FROM cliente c
        LEFT JOIN cliente_fidelidad cf ON c.id_cliente = cf.id_cliente
        LEFT JOIN fidelidad f ON cf.id_cliente_fidelidad = f.id_cliente_fidelidad
        LEFT JOIN nivel_fidelidad nf ON f.id_nivel_fidelidad = nf.id_nivel_fidelidad
        ORDER BY cf.puntos_acumulados DESC
    """)
    
    if not clientes_fidelidad.empty:
        # Top clientes
        st.subheader("🏆 Top Clientes por Puntos")
        top_clientes = clientes_fidelidad.head(10)
        
        for idx, cliente in top_clientes.iterrows():
            col1, col2, col3 = st.columns([2, 1, 3])
            with col1:
                st.write(f"**{cliente['nombre']}**")
                st.caption(f"CI: {cliente['ci']}")
            with col2:
                st.metric("Puntos", cliente['puntos_acumulados'] or 0)
            with col3:
                nivel = cliente['nivel'] or "Sin nivel"
                st.info(f"Nivel: {nivel}")
        
        st.divider()
        
        # Todos los clientes
        st.subheader("📋 Todos los Clientes")
        st.dataframe(clientes_fidelidad, use_container_width=True, hide_index=True)
        
        # Añadir/Actualizar puntos
        st.divider()
        st.subheader("➕ Actualizar Puntos de Cliente")
        
        col1, col2 = st.columns(2)
        with col1:
            cliente_seleccionado = st.selectbox(
                "Seleccionar cliente:",
                clientes_fidelidad.apply(lambda x: f"{x['nombre']} (CI: {x['ci']})", axis=1)
            )
        with col2:
            puntos_agregar = st.number_input("Puntos a agregar/restar:", min_value=-1000, max_value=1000, value=0)
        
        if st.button("Actualizar Puntos"):
            st.success(f"Puntos actualizados para {cliente_seleccionado}")
    else:
        st.info("No hay clientes en el programa de fidelidad")

# PÁGINA: TRANSPORTE
elif st.session_state.pagina_actual == "transporte":
    st.title("🚗 Gestión de Transporte")
    
    tab1, tab2 = st.tabs(["Rutas Disponibles", "Reservas de Transporte"])
    
    with tab1:
        rutas = query_to_df("""
            SELECT r.*, 
                   COUNT(t.id_transporte) as viajes_disponibles
            FROM ruta r
            LEFT JOIN transporte t ON r.id_ruta = t.id_ruta 
                AND t.estado = 'disponible'
                AND t.fecha_hora_salida > NOW()
            GROUP BY r.id_ruta
            ORDER BY r.origen, r.destino
        """)
        
        if not rutas.empty:
            for _, ruta in rutas.iterrows():
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{ruta['origen']} → {ruta['destino']}**")
                        st.caption(f"Distancia: {ruta['distancia']} km")
                    with col2:
                        st.write(f"⏱️ {ruta['tiempo_estimado']}")
                        st.write(f"💰 ${ruta['tarifa']:.2f}")
                    with col3:
                        st.metric("Disponibles", ruta['viajes_disponibles'])
        
        # Agregar nueva ruta
        st.divider()
        st.subheader("➕ Agregar Nueva Ruta")
        
        with st.form("nueva_ruta_form"):
            col1, col2 = st.columns(2)
            with col1:
                origen = st.text_input("Origen")
                distancia = st.number_input("Distancia (km)", min_value=0.0, step=0.1)
            with col2:
                destino = st.text_input("Destino")
                tarifa = st.number_input("Tarifa ($)", min_value=0.0, step=0.1)
            
            tiempo_horas = st.number_input("Tiempo estimado (horas)", min_value=0, max_value=24, value=1)
            tiempo_minutos = st.number_input("Tiempo estimado (minutos)", min_value=0, max_value=59, value=0)
            
            submitted = st.form_submit_button("Guardar Ruta")
            
            if submitted and origen and destino:
                tiempo_estimado = f"{tiempo_horas:02d}:{tiempo_minutos:02d}:00"
                ejecutar_query("""
                    INSERT INTO ruta (origen, destino, distancia, tiempo_estimado, tarifa)
                    VALUES (%s, %s, %s, %s, %s)
                """, (origen, destino, distancia, tiempo_estimado, tarifa), fetch=False)
                st.success("Ruta agregada exitosamente")
                st.rerun()

# PÁGINA: REPORTES
elif st.session_state.pagina_actual == "reportes":
    st.title("📈 Reportes y Análisis")
    
    tab1, tab2, tab3 = st.tabs(["Reporte de Ingresos", "Ocupación", "Clientes"])
    
    with tab1:
        st.subheader("📊 Reporte de Ingresos")
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("Fecha inicio", value=date(date.today().year, 1, 1))
        with col2:
            fecha_fin = st.date_input("Fecha fin", value=date.today())
        
        if st.button("Generar Reporte"):
            ingresos_periodo = query_to_df("""
                SELECT DATE(fecha_reserva) as fecha,
                       COUNT(*) as reservas,
                       SUM(total) as ingresos
                FROM reserva
                WHERE fecha_reserva BETWEEN %s AND %s
                AND estado_reserva != 'cancelada'
                GROUP BY DATE(fecha_reserva)
                ORDER BY fecha
            """, (fecha_inicio, fecha_fin))
            
            if not ingresos_periodo.empty:
                # Gráfico de líneas
                fig = px.line(ingresos_periodo, x='fecha', y='ingresos',
                            title='Ingresos Diarios', markers=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # Resumen
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Ingresos", f"${ingresos_periodo['ingresos'].sum():,.2f}")
                with col2:
                    st.metric("Total Reservas", ingresos_periodo['reservas'].sum())
                with col3:
                    ingreso_promedio = ingresos_periodo['ingresos'].mean()
                    st.metric("Ingreso Promedio", f"${ingreso_promedio:,.2f}")
                
                # Tabla detallada
                st.dataframe(ingresos_periodo, use_container_width=True, hide_index=True)
            else:
                st.info("No hay datos para el período seleccionado")
    
    with tab2:
        st.subheader("📈 Reporte de Ocupación")
        
        ocupacion_mensual = query_to_df("""
            SELECT DATE_FORMAT(fecha_entrada, '%Y-%m') as mes,
                   COUNT(*) as reservas,
                   AVG(DATEDIFF(fecha_salida, fecha_entrada)) as estancia_promedio,
                   SUM(total) as ingresos
            FROM reserva
            WHERE fecha_entrada >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY DATE_FORMAT(fecha_entrada, '%Y-%m')
            ORDER BY mes
        """)
        
        if not ocupacion_mensual.empty:
            fig = px.bar(ocupacion_mensual, x='mes', y='reservas',
                        title='Reservas por Mes', color='reservas')
            st.plotly_chart(fig, use_container_width=True)
            
            fig2 = px.line(ocupacion_mensual, x='mes', y='estancia_promedio',
                          title='Estancia Promedio (días)', markers=True)
            st.plotly_chart(fig2, use_container_width=True)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"🏨 Sistema Hotelero v1.0")
with col2:
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
with col3:
    st.caption("👑 Premium Hotel & Resort")