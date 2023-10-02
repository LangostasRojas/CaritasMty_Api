-- Crear Base de Datos
CREATE DATABASE Caritas
GO
USE Caritas
GO

-- Crear tablas
CREATE TABLE USUARIOS (
    idUsuario INT IDENTITY(1, 1) NOT NULL,
    username VARCHAR(30) NOT NULL,
    password VARCHAR(255) NOT NULL,
	nombre VARCHAR(20) NOT NULL,
	apellidoPaterno VARCHAR(15) NOT NULL,
	apellidoMaterno VARCHAR(15) NOT NULL,
	activo BIT NOT NULL,
    refreshtoken VARCHAR(255),
	idEncargado INT NULL,
    rol CHAR (10) NOT NULL,
    PRIMARY KEY(idUsuario),
	FOREIGN KEY (idEncargado) REFERENCES USUARIOS(idUsuario)
)

CREATE TABLE DONANTES (
    nombre VARCHAR(20) NOT NULL,
    idDonante INT IDENTITY(1, 1) NOT NULL,
    apellidoPaterno VARCHAR(15) NOT NULL,
	apellidoMaterno VARCHAR(15) NOT NULL,
    email VARCHAR(50) NOT NULL,
  	direccion VARCHAR (100) NOT NULL,
    telCasa INT NULL,
    telMovil INT NULL,
    genero CHAR(1) NOT NULL,
    PRIMARY KEY(idDonante)
)

CREATE TABLE BITACORA(
    idBitacora INT IDENTITY(1, 1) NOT NULL,
    idDonante INT NOT NULL,
    idRecolector INT NULL,
    -- id_num_pago INT NULL,
    importe FLOAT NOT NULL,
    fechaCobro DATE NOT NULL,
    fechaVisita DATETIME NULL,
    estatusPago TINYINT NOT NULL,
	estatusVisita TINYINT NOT NULL,
    comentarios VARCHAR(max) NULL,
    PRIMARY KEY(idBitacora),
    FOREIGN KEY(idDonante) REFERENCES DONANTES(idDonante),
    FOREIGN KEY(idRecolector) REFERENCES USUARIOS(idUsuario)
)

CREATE TABLE LOGS(
    id INT IDENTITY(1, 1) NOT NULL,
    ipAddress VARCHAR(20) NOT NULL,
    userAgent VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    path VARCHAR(max) NOT NULL,
    responseCode VARCHAR(3) NOT NULL,
    fecha DATETIME NOT NULL,
    token VARCHAR(255) NULL,
    PRIMARY KEY(id)
)

-- Resetear indices de las tablas
-- DBCC CHECKIDENT('USUARIOS', RESEED, 0);
-- DBCC CHECKIDENT('DONANTES', RESEED, 0);
-- DBCC CHECKIDENT('BITACORA', RESEED, 0);


-- Inserts para managers en la tabla USUARIOS
INSERT INTO USUARIOS (username, password, nombre, apellidoPaterno, apellidoMaterno, activo, refreshtoken, idEncargado, rol)
VALUES 
('user1', '$2a$12$DsRB5Urc3dEGs3591XcEFes54zm9Jbi3PZz6fYaNTn3z2onG5lbe6', 'Juan', 'Perez', 'Gomez', 1, NULL, NULL, 'manager'),
('user2', '$2a$12$DsRB5Urc3dEGs3591XcEFes54zm9Jbi3PZz6fYaNTn3z2onG5lbe6', 'María', 'Lopez', 'Rodriguez', 1, NULL, NULL, 'manager');
GO

-- Inserts para recolectores en la tabla USUARIOS
INSERT INTO USUARIOS (username, password, nombre, apellidoPaterno, apellidoMaterno, activo, refreshtoken, idEncargado, rol)
VALUES 
('user3', '$2a$12$DsRB5Urc3dEGs3591XcEFes54zm9Jbi3PZz6fYaNTn3z2onG5lbe6', 'Carlos', 'Gonzalez', 'Martinez', 1, NULL, 1, 'recolector'),
('user4', '$2a$12$DsRB5Urc3dEGs3591XcEFes54zm9Jbi3PZz6fYaNTn3z2onG5lbe6', 'Luis', 'Gutierrez', 'Hernandez', 1, NULL, 1, 'recolector'),
('user5', '$2a$12$DsRB5Urc3dEGs3591XcEFes54zm9Jbi3PZz6fYaNTn3z2onG5lbe6', 'Ana', 'Diaz', 'Ramirez', 1, NULL, 1, 'recolector'),
('user6', '$2a$12$DsRB5Urc3dEGs3591XcEFes54zm9Jbi3PZz6fYaNTn3z2onG5lbe6', 'Pedro', 'Martinez', 'Lopez', 1, NULL, 2, 'recolector');
GO

-- Inserts para la tabla DONANTES
INSERT INTO DONANTES (nombre, apellidoPaterno, apellidoMaterno, email, direccion, telCasa, telMovil, genero)
VALUES 
('Roberto', 'Gomez', 'Lopez', 'roberto@gmail.com', 'Calle 123', 123456789, 987654321, 'M'),
('Laura', 'Rodriguez', 'Gonzalez', 'laura@gmail.com', 'Av. Principal', NULL, 789456123, 'F'),
('Javier', 'Martinez', 'Perez', 'javier@gmail.com', 'Calle 456', 456123789, NULL, 'M'),
('María', 'Hernandez', 'Gomez', 'maria@gmail.com', 'Calle 789', 987654321, NULL, 'F'),
('Carlos', 'Lopez', 'Gutierrez', 'carlos@gmail.com', 'Av. Secundaria', NULL, 321654987, 'M'),
('Alejandra', 'Sanchez', 'Martinez', 'alejandra.sanchez@gmail.com', 'Calle 303', 123456789, 987654321, 'F'),
('Eduardo', 'Lopez', 'Gonzalez', 'eduardo.lopez@gmail.com', 'Av. Independencia', NULL, 789456123, 'M'),
('Isabel', 'Garcia', 'Hernandez', 'isabel.garcia@gmail.com', 'Calle 404', 456123789, NULL, 'F'),
('Diego', 'Fernandez', 'Ramirez', 'diego.fernandez@gmail.com', 'Av. Revolución', NULL, 321654987, 'M');
GO

-- Inserts para la tabla BITACORA
INSERT INTO BITACORA (idDonante, idRecolector, importe, fechaCobro, fechaVisita, estatusPago, estatusVisita, comentarios)
VALUES 
(1, 3, 123.00, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(2, 4, 79.15, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(3, 5, 721.79, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(4, 6, 234.50, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(5, 3, 89.25, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(6, 4, 324.10, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(7, 5, 453.75, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(8, 6, 567.80, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(9, 3, 132.40, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(1, 4, 189.30, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(2, 5, 298.60, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(3, 6, 456.70, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(4, 3, 134.25, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(5, 4, 239.50, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(6, 5, 342.70, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(7, 6, 456.90, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(8, 3, 567.10, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(9, 4, 789.30, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(1, 5, 890.45, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(2, 6, 1234.60, CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL);
GO
-- Modificar la fecha de cobro
-- UPDATE BITACORA
-- SET fechaCobro = CONVERT(DATE, GETDATE())

-- SELECT * FROM BITACORA
-- SELECT * FROM DONANTES
CREATE TRIGGER NoActualizarNombres
ON DONANTES
AFTER UPDATE
AS
BEGIN
    IF UPDATE(nombre) OR UPDATE(apellidoPaterno) OR UPDATE (apellidoMaterno)
    BEGIN
        RAISERROR('No puedes actualizar el nombre', 16, 1)
        ROLLBACK TRANSACTION
    END
END;
GO
ALTER TABLE DONANTES ENABLE TRIGGER NoActualizarNombres;