-- Crear base de datos
CREATE DATABASE IF NOT EXISTS hotel
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;
USE hotel;

-- Tablas auxiliares / lookup
CREATE TABLE promocion_temporada (
id_promocion_temporada INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
fecha_promocion DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
<<>>
CREATE TABLE nivel_fidelidad (
id_nivel_fidelidad INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
nivel VARCHAR(45),
beneficios VARCHAR(1000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE estado_pago (
id_estado_pago INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
nombre_estado_pago VARCHAR(45)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE metodo_pago (
id_metodo_pago INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
nombre VARCHAR(45),
descripcion VARCHAR(200),
fecha_creacion DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE servicios_especiales (
id_servicios_especiales INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
nombre VARCHAR(100),
precio DECIMAL(18,2),
descripcion VARCHAR(1000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE ruta (
id_ruta INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
origen VARCHAR(100),
destino VARCHAR(100),
distancia DECIMAL(10,2),
tiempo_estimado TIME,
tarifa DECIMAL(18,2)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE tipo_habitacion (
id_tipo_habitacion INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
numero_camas INT,
tipo_cama VARCHAR(45),
banio BOOLEAN,
descripcion VARCHAR(1000),
wifi BOOLEAN,
tv BOOLEAN,
escritorio BOOLEAN,
tamano_m2 DECIMAL(8,2),
capacidad INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Cliente y contacto
CREATE TABLE cliente (
id_cliente INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
nombre VARCHAR(100),
ci VARCHAR(45),
apellido_paterno VARCHAR(100),
apellido_materno VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE contacto (
id_contacto INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
telefono VARCHAR(45),
correo_electronico VARCHAR(100),
id_cliente INT,
FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Servicios / fidelidad del cliente
CREATE TABLE cliente_servicio (
id_cliente_servicio INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_cliente INT NOT NULL,
nombre_cliente VARCHAR(100),
FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE cliente_fidelidad (
id_cliente_fidelidad INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_cliente INT NOT NULL,
puntos_acumulados INT DEFAULT 0,
fecha_actualizacion DATE,
FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Promociones (tabla que faltaba)
CREATE TABLE promocion (
id_promocion INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
codigo_promocion VARCHAR(50) UNIQUE,
descripcion VARCHAR(500),
descuento_porcentaje DECIMAL(5,2),
fecha_inicio DATE,
fecha_fin DATE,
activa BOOLEAN DEFAULT TRUE,
id_promocion_temporada INT,
FOREIGN KEY (id_promocion_temporada) REFERENCES promocion_temporada(id_promocion_temporada)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE fidelidad (
id_fidelidad INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
fecha_validez DATE,
id_promocion INT NULL,
id_nivel_fidelidad INT,
id_cliente_fidelidad INT,
FOREIGN KEY (id_nivel_fidelidad) REFERENCES nivel_fidelidad(id_nivel_fidelidad)
ON UPDATE CASCADE ON DELETE SET NULL,
FOREIGN KEY (id_cliente_fidelidad) REFERENCES cliente_fidelidad(id_cliente_fidelidad)
ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (id_promocion) REFERENCES promocion(id_promocion)
ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Habitaciones y tipos especializadas
CREATE TABLE habitacion (
id_habitacion INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
precio DECIMAL(18,2),
numero_habitacion INT,
piso INT,
id_tipo_habitacion INT,
FOREIGN KEY (id_tipo_habitacion) REFERENCES tipo_habitacion(id_tipo_habitacion)
ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE suite (
id_suite INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
jacuzzi BOOLEAN,
streaming BOOLEAN,
id_tipo_habitacion INT,
FOREIGN KEY (id_tipo_habitacion) REFERENCES tipo_habitacion(id_tipo_habitacion)
ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE premium (
id_premium INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
jacuzzi BOOLEAN,
streaming BOOLEAN,
piscina_privada BOOLEAN,
mini_bar BOOLEAN,
id_tipo_habitacion INT,
FOREIGN KEY (id_tipo_habitacion) REFERENCES tipo_habitacion(id_tipo_habitacion)
ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE presidencial (
id_presidencial INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
jacuzzi BOOLEAN,
streaming BOOLEAN,
piscina_privada BOOLEAN,
mini_bar BOOLEAN,
asistente VARCHAR(100),
id_tipo_habitacion INT,
FOREIGN KEY (id_tipo_habitacion) REFERENCES tipo_habitacion(id_tipo_habitacion)
ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Servicios especiales dependientes
CREATE TABLE spa (
id_spa INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
numero_personas INT,
duracion TIME,
precio DECIMAL(18,2),
descripcion VARCHAR(500),
id_servicios_especiales INT,
FOREIGN KEY (id_servicios_especiales) REFERENCES servicios_especiales(id_servicios_especiales)
ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Transporte
CREATE TABLE transporte (
id_transporte INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_ruta INT,
tipo_vehiculo VARCHAR(50),
capacidad INT,
fecha_hora_salida DATETIME,
fecha_hora_llegada DATETIME,
precio DECIMAL(18,2),
estado ENUM('disponible', 'reservado', 'en viaje', 'finalizado'),
FOREIGN KEY (id_ruta) REFERENCES ruta(id_ruta)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- TABLAS PRINCIPALES PARA LA APLICACIÓN

-- Tabla de Reservas
CREATE TABLE reserva (
id_reserva INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_cliente INT NOT NULL,
id_habitacion INT NOT NULL,
fecha_entrada DATE NOT NULL,
fecha_salida DATE NOT NULL,
numero_huespedes INT,
estado_reserva ENUM('pendiente', 'confirmada', 'en curso', 'completada', 'cancelada'),
fecha_reserva DATETIME DEFAULT CURRENT_TIMESTAMP,
total DECIMAL(18,2),
observaciones TEXT,
FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente) 
ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (id_habitacion) REFERENCES habitacion(id_habitacion)
ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de Pagos
CREATE TABLE pago (
id_pago INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_reserva INT NOT NULL,
id_metodo_pago INT,
id_estado_pago INT,
monto DECIMAL(18,2),
fecha_pago DATETIME,
referencia VARCHAR(100),
descripcion TEXT,
FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
ON UPDATE CASCADE ON DELETE CASCADE,
FOREIGN KEY (id_metodo_pago) REFERENCES metodo_pago(id_metodo_pago),
FOREIGN KEY (id_estado_pago) REFERENCES estado_pago(id_estado_pago)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de Facturación
CREATE TABLE factura (
id_factura INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_reserva INT NOT NULL,
id_cliente INT NOT NULL,
numero_factura VARCHAR(50) UNIQUE,
fecha_factura DATE,
subtotal DECIMAL(18,2),
iva DECIMAL(18,2),
total DECIMAL(18,2),
nit VARCHAR(20),
razon_social VARCHAR(200),
FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de Servicios Adicionales por Reserva
CREATE TABLE reserva_servicio (
id_reserva_servicio INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_reserva INT NOT NULL,
id_servicios_especiales INT NOT NULL,
cantidad INT DEFAULT 1,
fecha_servicio DATE,
hora_servicio TIME,
total_servicio DECIMAL(18,2),
FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
FOREIGN KEY (id_servicios_especiales) REFERENCES servicios_especiales(id_servicios_especiales)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de Reserva de Transporte
CREATE TABLE reserva_transporte (
id_reserva_transporte INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_reserva INT,
id_transporte INT,
numero_personas INT,
fecha_reserva DATETIME,
FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
FOREIGN KEY (id_transporte) REFERENCES transporte(id_transporte)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de Check-in/Check-out
CREATE TABLE registro_hospedaje (
id_registro INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
id_reserva INT NOT NULL,
fecha_checkin DATETIME,
fecha_checkout DATETIME,
id_empleado_checkin INT,
id_empleado_checkout INT,
observaciones TEXT,
FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- DATOS INICIALES DE EJEMPLO (opcional)

INSERT INTO estado_pago (nombre_estado_pago) VALUES 
('pendiente'),
('completado'),
('rechazado'),
('reembolsado');

INSERT INTO metodo_pago (nombre, descripcion, fecha_creacion) VALUES 
('Efectivo', 'Pago en efectivo en recepción', NOW()),
('Tarjeta de Crédito', 'Pago con tarjeta de crédito', NOW()),
('Transferencia Bancaria', 'Transferencia bancaria', NOW()),
('PayPal', 'Pago a través de PayPal', NOW());

INSERT INTO nivel_fidelidad (nivel, beneficios) VALUES 
('Bronce', 'Descuento del 5% en reservas'),
('Plata', 'Descuento del 10%, check-in prioritario'),
('Oro', 'Descuento del 15%, upgrade de habitación, late checkout'),
('Platino', 'Descuento del 20%, todos los beneficios anteriores + spa gratuito');

INSERT INTO tipo_habitacion (numero_camas, tipo_cama, banio, descripcion, wifi, tv, escritorio, tamano_m2, capacidad) VALUES 
(1, 'Queen', 1, 'Habitación individual estándar', 1, 1, 1, 20.00, 1),
(2, 'Twin', 1, 'Habitación doble con camas separadas', 1, 1, 1, 25.00, 2),
(1, 'King', 1, 'Suite con cama king size', 1, 1, 1, 35.00, 2),
(2, 'King', 1, 'Suite presidencial con lujos', 1, 1, 1, 60.00, 4);

INSERT INTO servicios_especiales (nombre, precio, descripcion) VALUES 
('Desayuno buffet', 15.00, 'Desayuno completo buffet'),
('Spa básico', 50.00, 'Masaje relajante de 60 minutos'),
('Tour ciudad', 30.00, 'Tour guiado por la ciudad'),
('Lavandería', 10.00, 'Servicio de lavandería express');

-- ÍNDICES PARA MEJORAR EL RENDIMIENTO

CREATE INDEX idx_reserva_fechas ON reserva(fecha_entrada, fecha_salida);
CREATE INDEX idx_reserva_cliente ON reserva(id_cliente);
CREATE INDEX idx_reserva_estado ON reserva(estado_reserva);
CREATE INDEX idx_habitacion_tipo ON habitacion(id_tipo_habitacion);
CREATE INDEX idx_pago_reserva ON pago(id_reserva);
CREATE INDEX idx_cliente_ci ON cliente(ci);
CREATE INDEX idx_contacto_cliente ON contacto(id_cliente);
CREATE INDEX idx_fidelidad_cliente ON cliente_fidelidad(id_cliente);
CREATE INDEX idx_transporte_ruta ON transporte(id_ruta);
CREATE INDEX idx_transporte_estado ON transporte(estado);

-- VISTAS ÚTILES PARA LA APLICACIÓN STREAMLIT

CREATE VIEW vista_reservas_activas AS
SELECT 
    r.id_reserva,
    c.nombre AS cliente_nombre,
    c.ci AS cliente_ci,
    h.numero_habitacion,
    r.fecha_entrada,
    r.fecha_salida,
    r.estado_reserva,
    r.total,
    DATEDIFF(r.fecha_salida, r.fecha_entrada) AS noches
FROM reserva r
JOIN cliente c ON r.id_cliente = c.id_cliente
JOIN habitacion h ON r.id_habitacion = h.id_habitacion
WHERE r.estado_reserva IN ('confirmada', 'en curso');

CREATE VIEW vista_habitaciones_disponibles AS
SELECT 
    h.id_habitacion,
    h.numero_habitacion,
    h.piso,
    h.precio,
    th.tipo_cama,
    th.capacidad,
    th.tamano_m2,
    th.wifi,
    th.tv
FROM habitacion h
JOIN tipo_habitacion th ON h.id_tipo_habitacion = th.id_tipo_habitacion
WHERE h.id_habitacion NOT IN (
    SELECT id_habitacion 
    FROM reserva 
    WHERE estado_reserva IN ('confirmada', 'en curso', 'pendiente')
    AND CURDATE() BETWEEN fecha_entrada AND fecha_salida
);

CREATE VIEW vista_clientes_fidelidad AS
SELECT 
    c.id_cliente,
    c.nombre,
    c.ci,
    cf.puntos_acumulados,
    nf.nivel,
    nf.beneficios
FROM cliente c
LEFT JOIN cliente_fidelidad cf ON c.id_cliente = cf.id_cliente
LEFT JOIN fidelidad f ON cf.id_cliente_fidelidad = f.id_cliente_fidelidad
LEFT JOIN nivel_fidelidad nf ON f.id_nivel_fidelidad = nf.id_nivel_fidelidad;

CREATE VIEW vista_ingresos_mensuales AS
SELECT 
    YEAR(fecha_factura) AS año,
    MONTH(fecha_factura) AS mes,
    COUNT(*) AS numero_facturas,
    SUM(total) AS ingresos_totales
FROM factura
GROUP BY YEAR(fecha_factura), MONTH(fecha_factura)
ORDER BY año DESC, mes DESC;