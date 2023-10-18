from flask import jsonify
from app.config.mssql import mssql_connect
import pymssql

def get_report_information(jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT idBitacora AS idRecibo, idDonante, importe, estatusPago, ISNULL(c.comentario, '') AS comentario
            FROM BITACORA b
            LEFT JOIN COMENTARIOS c ON b.comentarios = c.idComentario
            WHERE CONVERT(DATE, b.fechaCobro) = CONVERT(DATE, GETDATE());
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()

        if (len(result) == 0):
            return {'mensaje': 'No hay datos que mostrar'}, 200
        
        # Cambiar a booleano
        for res in result:
            if res['estatusPago'] != 1: res['estatusPago'] = False
            else: res['estatusPago'] = True
        
        return jsonify(result)
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def get_zone_donations(jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT ROW_NUMBER() OVER (ORDER BY d.municipio) AS id, d.municipio, ROUND(SUM(importe), 2) AS ingresos
            FROM BITACORA b
            JOIN DONANTES d ON b.idDonante = d.idDonante
            GROUP BY d.municipio
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()

        if (len(result) == 0):
            return {'mensaje': 'No hay datos que mostrar'}, 200
        
        return jsonify(result)
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def get_completion_rate(jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT COUNT(*) AS total, 
                (SELECT COUNT(*) 
                FROM BITACORA 
                WHERE estatusPago = 1 AND CONVERT(DATE, fechaCobro) = CONVERT(DATE, GETDATE()))  AS recolectado
            FROM BITACORA
            WHERE CONVERT(DATE, fechaCobro) = CONVERT(DATE, GETDATE())
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()

        if (len(result) == 0):
            return {'mensaje': 'No hay datos que mostrar'}, 200
        
        if result[0]['recolectado'] == 0: result[0]['porcentaje'] = 0
        else: result[0]['porcentaje'] = int(result[0]['recolectado'] / result[0]['total'] * 100)
        
        return jsonify(result[0])
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401

    
def get_zone_donations(jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT ROW_NUMBER() OVER (ORDER BY d.municipio) AS id, d.municipio, ROUND(SUM(importe), 2) AS ingresos
            FROM BITACORA b
            JOIN DONANTES d ON b.idDonante = d.idDonante
            GROUP BY d.municipio
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()

        if (len(result) == 0):
            return {'mensaje': 'No hay datos que mostrar'}, 200
        
        return jsonify(result)
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def get_average_tickets(jwt_payload):
    global cnx, mssql_params
    query = """ 
            SET LANGUAGE SPANISH;
            SELECT ROW_NUMBER() OVER (ORDER BY CONVERT(DATE, fechaCobro)) AS id, COUNT(*) AS total, 
            	   ISNULL(b2.recolectado, 0) AS recolectado, DATENAME(dw, fechaCobro) as fecha
            FROM BITACORA b
            LEFT JOIN (
            	SELECT COUNT(*) AS recolectado, CONVERT(DATE, fechaCobro) AS fecha
            	FROM BITACORA
            	WHERE estatusPago = 1
            	GROUP BY CONVERT(DATE, fechaCobro)
            ) b2 ON CONVERT(DATE, b.fechaCobro) = b2.fecha
            WHERE fechaCobro >= CONVERT(DATE, GETDATE() - 7)
            GROUP BY DATENAME(dw, fechaCobro), b2.recolectado, CONVERT(DATE, fechaCobro);
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()

        if (len(result) == 0):
            return {'mensaje': 'No hay datos que mostrar'}, 200

        for res in result:
            if res['recolectado'] == 0: res['porcentaje'] = 0
            else: res['porcentaje'] = int(res['recolectado'] / res['total'] * 100)
        
        return jsonify(result)
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def get_expected_donations(jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT ROUND(SUM(importe), 2) AS donacionesEsperadas
            FROM BITACORA
            WHERE fechaCobro = CONVERT(DATE, GETDATE())
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()
        
        return jsonify(result[0])
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401
    

def get_completion_rate_by_collector(jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT ROW_NUMBER() OVER (ORDER BY u.nombre + ' ' + u.apellidoPaterno, r.recolectado) AS id, 
                   u.nombre + ' ' + u.apellidoPaterno AS nombre, COUNT(*) AS total, r.recolectado
            FROM BITACORA b
            JOIN USUARIOS u ON b.idRecolector = u.idUsuario
            JOIN (
            	SELECT COUNT(*) AS recolectado, idRecolector
            	FROM BITACORA b
            	WHERE b.estatusPago = 1
            	GROUP BY idRecolector
            ) r ON b.idRecolector = r.idRecolector
            GROUP BY u.nombre + ' ' + u.apellidoPaterno, r.recolectado;
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()

        for res in result:
            res['porcentaje'] = int(res['recolectado'] / res['total'] * 100)
        
        return jsonify(result)
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401
    

def get_collected_tickets_c_month(jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT COUNT(*) AS recolectados
            FROM BITACORA
            WHERE MONTH(fechaCobro) >= MONTH(GETDATE())
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()
        
        return jsonify(result[0])
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401
    

def get_collected_tickets_month(jwt_payload):
    global cnx, mssql_params
    query = """
            SET LANGUAGE SPANISH;
            SELECT ROW_NUMBER() OVER (ORDER BY DATENAME(MONTH, fechaCobro), b2.recolectado) AS id, 
                   COUNT(*) AS total, b2.recolectado, DATENAME(MONTH, fechaCobro) AS mes
            FROM BITACORA b
            JOIN (
                SELECT COUNT(*) AS recolectado, DATENAME(MONTH, fechaCobro) AS mes
                FROM BITACORA WHERE estatusPago = 1 
                GROUP BY DATENAME(MONTH, fechaCobro)
            ) b2 ON DATENAME(MONTH, b.fechaCobro) = b2.mes
            GROUP BY DATENAME(MONTH, fechaCobro), b2.recolectado;
            """
    try:
        if jwt_payload['role'] != 'manager':
            return {'error': 'Acceso no autorizado'}, 401
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, )
        
        result = cursor.fetchall()
        cursor.close()
        
        return jsonify(result)
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401