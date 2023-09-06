-- Creacion de TABLAS

CREATE TABLE USUARIOS (
    id_usuario int IDENTITY(1, 1) NOT NULL,
    username varchar(255) NOT NULL,
    password varchar(255) NOT NULL,
    refreshtoken varchar(255) NULL,
    role CHAR (10) NOT NULL,
    PRIMARY KEY(id_usuario)
)

CREATE TABLE MANAGERS (
    id_manager int NOT NULL,
    nombre varchar(255) NULL,
    activo int NULL,
    PRIMARY KEY (id_manager),
    FOREIGN KEY (id_manager) REFERENCES USUARIOS(id_usuario)
)

CREATE TABLE RECOLECTORES (
    id_recolector int NOT NULL,
    nombre varchar(300) NULL,
    id_zona int NULL,
    activo int NULL,
    PRIMARY KEY (id_recolector),
    FOREIGN KEY (id_recolector) REFERENCES USUARIOS(id_usuario)
)

CREATE TABLE DONANTES (
    id_donante int IDENTITY(1, 1) NOT NULL,
    a_paterno varchar(100) NOT NULL,
    a_materno varchar(100) NULL,
    nombre varchar(100) NOT NULL,
    email varchar(50) NOT NULL,
  	direccion varchar (100) NOT NULL,
    tel_casa int NULL,
    tel_movil int NULL,
    ultimo_donativo int NULL,
    id_genero int NULL,
    PRIMARY KEY(id_donante)
)

CREATE TABLE DONATIVOS(
    id_donativo int IDENTITY(1, 1) NOT NULL,
    id_donante int NOT NULL,
    importe float NULL,
    id_estatus int NULL,
    PRIMARY KEY(id_donativo),
    FOREIGN KEY(id_donante) REFERENCES DONANTES(id_donante)
)

CREATE TABLE BITACORA(
    id_bitacora int IDENTITY(1, 1) NOT NULL,
    id_donativo int NOT NULL,
    id_num_pago int NULL,
    id_recolector int NULL,
    fecha_cobro date NULL,
    fecha_pago date NULL,
    fecha_visita date NULL,
    id_recibo varchar(50) NULL,
    estatus_pago int NULL,
    comentarios varchar(max) NULL,
    fecha_confirmacion datetime NULL,
    fecha_status_pagado datetime NULL,
    fecha_reprogramacion datetime NULL,
    reprogramacion_telefonista int NULL DEFAULT ((0)),
    PRIMARY KEY(id_bitacora),
    FOREIGN KEY(id_donativo) REFERENCES DONATIVOS(id_donativo),
    FOREIGN KEY(id_recolector) REFERENCES RECOLECTORES(id_recolector)
)

-- INSERTS

 -- USUARIOS
INSERT INTO USUARIOS (username, password, refreshtoken, role)
VALUES ('user1', '$2a$12$DsRB5Urc3dEGs3591XcEFes54zm9Jbi3PZz6fYaNTn3z2onG5lbe6', NULL, 'manager');

INSERT INTO USUARIOS (username, password, refreshtoken, role)
VALUES ('user2', '$2a$12$DsRB5Urc3dEGs3591XcEFes54zm9Jbi3PZz6fYaNTn3z2onG5lbe6', NULL, 'repartidor');


-- MANAGER 

INSERT INTO MANAGERS (id_manager, nombre, activo)
VALUES (1, 'Jose Placencia', 1);

-- Repartidor
INSERT INTO RECOLECTORES (id_recolector, nombre, id_zona, activo)
VALUES (2, 'Ricardo Joseua', 2, 1);

-- Donante

INSERT INTO DONANTES (a_paterno, a_materno, nombre, email, direccion, tel_casa, tel_movil, ultimo_donativo, id_genero)
VALUES ('Gómez', 'Hernández', 'Ana', 'ana@example.com', 'Calle 123, Ciudad', 12345678, 98765432, 100, 1);

INSERT INTO DONANTES (a_paterno, a_materno, nombre, email, direccion, tel_casa, tel_movil, ultimo_donativo, id_genero)
VALUES ('López', 'Martínez', 'Carlos', 'carlos@example.com', 'Avenida 456, Pueblo', 98765432, 12345678, 200, 2);

-- Donativo

INSERT INTO DONATIVOS (id_donante, importe, id_estatus)
VALUES (1, 50.00, 0);

INSERT INTO DONATIVOS (id_donante, importe, id_estatus)
VALUES (2, 75.00, 1);

-- BITACORA

INSERT INTO BITACORA (id_donativo, id_num_pago, id_recolector, fecha_cobro, fecha_pago, fecha_visita, id_recibo, estatus_pago, comentarios, fecha_confirmacion, fecha_status_pagado, fecha_reprogramacion, reprogramacion_telefonista)
VALUES (1, 1, 2, '2023-09-06', '2023-09-07', '2023-09-08', 'REC001', 1, 'Comentario 1', '2023-09-09', '2023-09-10', '2023-09-11', 0);

INSERT INTO BITACORA (id_donativo, id_num_pago, id_recolector, fecha_cobro, fecha_pago, fecha_visita, id_recibo, estatus_pago, comentarios, fecha_confirmacion, fecha_status_pagado, fecha_reprogramacion, reprogramacion_telefonista)
VALUES (2, 2, 2, '2023-09-07', '2023-09-08', '2023-09-09', 'REC002', 2, 'Comentario 2', '2023-09-10', '2023-09-11', '2023-09-12', 0);
