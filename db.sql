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
    municipio VARCHAR(30) NOT NULL,
    codigoPostal INT NULL,
    telCasa INT NULL,
    telMovil INT NULL,
    genero CHAR(1) NOT NULL,
    PRIMARY KEY(idDonante)
)

CREATE TABLE COMENTARIOS(
    idComentario INT IDENTITY(1, 1) NOT NULL,
    comentario VARCHAR(50) NOT NULL,
    PRIMARY KEY(idComentario)
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
    comentarios INT,
    PRIMARY KEY(idBitacora),
    FOREIGN KEY(idDonante) REFERENCES DONANTES(idDonante),
    FOREIGN KEY(idRecolector) REFERENCES USUARIOS(idUsuario),
    FOREIGN KEY(comentarios) REFERENCES COMENTARIOS(idComentario)
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
INSERT INTO DONANTES (nombre, apellidoPaterno, apellidoMaterno, email, direccion, municipio, codigoPostal, telCasa, telMovil, genero)
VALUES 
('Roberto', 'Gomez', 'Lopez', 'roberto@gmail.com', 'Av. Eugenio Garza Sada 2501 Sur, Tecnológico', 'Monterrey', 64849, 123456789, 987654321, 'M'),
('Laura', 'Rodriguez', 'Gonzalez', 'laura@gmail.com', 'Dinamarca 451, Del Carmen', 'Monterrey', 64710 , NULL, 789456123, 'F'),
('Javier', 'Martinez', 'Perez', 'javier@gmail.com', 'Puerto Topolobampo 4603, Colinia Valle de, Las Brisas', 'Monterrey', 64790, 456123789, NULL, 'M'),
('María', 'Hernandez', 'Gomez', 'maria@gmail.com', 'Carretera Nacional km 267.7 Colonia, La Estanzuela', 'Monterrey', 64986, 987654321, NULL, 'F'),
('Carlos', 'Lopez', 'Gutierrez', 'carlos@gmail.com', 'Lince 1000, Cumbres Elite, Sector Villas', 'Monterrey', 64349, NULL, 321654987, 'M'),
('Alejandra', 'Sanchez', 'Martinez', 'alejandra.sanchez@gmail.com', 'Av. Dr. Ignacio Morones Prieto 290, Sin Nombre de Col 11', 'Santa Catarina', 66180, 123456789, 987654321, 'F'),
('Eduardo', 'Lopez', 'Gonzalez', 'eduardo.lopez@gmail.com', 'Av. Pablo Livas 2011, La Pastora', 'Guadalupe', 67140, NULL, 789456123, 'M'),
('Isabel', 'Garcia', 'Hernandez', 'isabel.garcia@gmail.com', 'Niños Héroes, Ciudad Universitaria', 'San Nicolás de los Garza', 66451, 456123789, NULL, 'F'),
('Diego', 'Fernandez', 'Ramirez', 'diego.fernandez@gmail.com', 'Av Eloy Cavazos, Jardines de La Pastora', 'Guadalupe', 67140, NULL, 321654987, 'M');
GO

-- Inserts para la tabla BITACORA
INSERT INTO BITACORA (idDonante, idRecolector, importe, fechaCobro, fechaVisita, estatusPago, estatusVisita, comentarios)
VALUES 
(1, 3, 123.00, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(2, 4, 79.15, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(3, 5, 721.79, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(4, 6, 234.50, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(5, 3, 89.25, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(6, 4, 324.10, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(7, 5, 453.75, CONVERT(DATE, GETDATE()), NULL, 2, 2, 2),
(8, 6, 567.80, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(9, 3, 132.40, CONVERT(DATE, GETDATE()), NULL, 2, 2, 3),
(1, 4, 189.30, CONVERT(DATE, GETDATE()), NULL, 2, 2, 4),
(2, 5, 298.60, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(3, 6, 456.70, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(4, 3, 134.25, CONVERT(DATE, GETDATE()), NULL, 2, 2, 5),
(5, 4, 239.50, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(6, 5, 342.70, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(7, 6, 456.90, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(8, 3, 567.10, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(9, 4, 789.30, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL),
(1, 5, 890.45, CONVERT(DATE, GETDATE()), NULL, 2, 2, 6),
(2, 6, 1234.60, CONVERT(DATE, GETDATE()), NULL, 1, 2, NULL);
GO

INSERT INTO BITACORA (idDonante, idRecolector, importe, fechaCobro, fechaVisita, estatusPago, estatusVisita, comentarios)
VALUES 
(1, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(2, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(3, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(4, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(5, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(6, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(7, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(8, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL),
(9, ROUND(RAND() * 3 + 3, 0), ROUND(RAND() * 700 + 200, 2), CONVERT(DATE, GETDATE()), NULL, 0, 0, NULL)
GO


INSERT INTO COMENTARIOS (comentario)
VALUES
('comentario 1'),
('comentario 2'),
('comentario 3'),
('comentario 4'),
('comentario 5'),
('comentario 6');
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


-- Crear usuario
USE master
GO
CREATE LOGIN Langostas WITH PASSWORD = '$YbZB5ZwPZlfbiLB1tW4'; -- Se ejecuta en master
GO

-- Ejectuar en master
CREATE USER Langostas FOR LOGIN Langostas;
GO

-- Ejecutar en db
USE Caritas
CREATE USER Langostas FOR LOGIN Langostas WITH DEFAULT_SCHEMA = dbo;
GO

-- Dar Permisos
USE Caritas;
GO
GRANT SELECT, UPDATE, INSERT ON SCHEMA::dbo TO Langostas
GO