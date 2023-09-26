import pymssql
import bcrypt
import jwt
import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
cnx = None
mssql_params = {}
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')
REFRESH_TOKEN_KEY = os.getenv('REFRESH_TOKEN_KEY')

def mssql_connect(sql_creds):
    import pymssql
    cnx = pymssql.connect(
        server=sql_creds['DB_HOST'],
        user=sql_creds['DB_USER'],
        password=sql_creds['DB_PASSWORD'],
        database=sql_creds['DB_NAME'])
    return cnx


def calculate_expiration():
    return datetime.datetime.utcnow() + datetime.timedelta(days=1)


def post_refresh_token(token, userId):
    global cnx, mssql_params
    query = 'UPDATE USUARIOS SET refreshtoken = %s WHERE idUsuario = %s;'

    try:
        cursor = cnx.cursor(as_dict=True)
        cursor.execute(query, (token, userId))
        cnx.commit()  # Commit the changes to the database
        cursor.close()
    except pymssql.InterfaceError as ie:
        print('Error executing SQL query:', ie)
        # Reconnect to the database
        cnx = mssql_connect(mssql_params)
        cursor = cnx.cursor(as_dict=True)
        cursor.execute(query, (token, userId))
        cnx.commit()  # Commit the changes to the database
        cursor.close()
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def sign_in(username, password):
    global cnx, mssql_params, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY
    # Parametrized query (allows only strings)
    query = """
            SELECT idUsuario, username, rol, password, nombre, apellidoPaterno + ' ' + apellidoMaterno AS apellidos
            FROM USUARIOS WHERE username = %s;
            """

    try:
        try:
            cursor = cnx.cursor(as_dict=True)
            # Execute query using username as parameter
            cursor.execute(query, (username, ))
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (username, ))
        
        result = cursor.fetchall()
        user_password = result[0]['password'].encode('utf-8')
        
        cursor.close()

        if bcrypt.checkpw(password.encode('utf-8'), user_password):      
            resultado = {
                            "userId": result[0]['idUsuario'], 
                            "userName": result[0]['username'], 
                            "name": result[0]['nombre'], 
                            "lastName": result[0]['apellidos'], 
                            "role": result[0]['rol'].strip(' '),
                            "exp": calculate_expiration()
                        }
            
            accessToken = jwt.encode(resultado, ACCESS_TOKEN_KEY, algorithm='HS256')
            refreshToken = jwt.encode(resultado, REFRESH_TOKEN_KEY, algorithm='HS256')
            resultado['accessToken'] = accessToken
            resultado['refreshToken'] = refreshToken

            post_refresh_token(refreshToken, resultado['userId'])
            return resultado

        else:
            return {'error': 'Usuario o contraseña incorrectos'}, 401
    
    except Exception as e:
        return {'error': 'Error al iniciar sesi'}, 401


def get_collector_tickets(user_id, jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT b.idBitacora AS idTicket, b.importe AS importe, d.nombre + ' ' + d.apellidoPaterno AS nombre, d.direccion
            FROM USUARIOS u
            JOIN BITACORA b ON b.idRecolector = u.idUsuario
            JOIN DONANTES d ON d.idDonante = b.idDonante
            WHERE u.idUsuario= %s AND b.estatusPago = 0 AND CONVERT(DATE, b.fechaCobro) = CONVERT(DATE, GETDATE());
            """

    try:
        # Verificar que user_id sea un entero
        try: user_id = int(user_id)
        except Exception as e: return {'error': 'Usuario invalido'}, 406

        # Verificar que no se este intentando acceder a tickets de otro recolector 
        if 'userId' in jwt_payload and jwt_payload['userId'] != int(user_id):
            return {'error': 'Acceso no autorizado'}, 401
        
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (user_id, ))
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (user_id, ))

        result = cursor.fetchall()
        cursor.close()
        
        return result

    except Exception as e:
        return {'error': 'Ocurrio un error al obtener tickets de recolector'}
    

def get_ticket_information(ticket_id, jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT b.idRecolector AS idRecolector, b.idBitacora AS idTicket, b.importe, d.nombre + ' ' + d.apellidoPaterno nombre, d.direccion
            FROM USUARIOS u
            JOIN BITACORA b ON u.idUsuario = b.idRecolector
            JOIN DONANTES d ON b.idDonante = d.idDonante
            WHERE b.idBitacora = %s;
            """
    
    try:
        # Verificar que ticket_id sea un entero
        try: ticket_id = int(ticket_id)
        except Exception as e: return {'error': 'Ticket no valido'}, 406

        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (ticket_id, ))
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (ticket_id, ))
        
        result = cursor.fetchall()
        cursor.close()

        if len(result) == 0:
            return {'error': 'Ticket no encontrado'}, 404
        if result[0]['idRecolector'] != jwt_payload['userId']:
            return {'error': 'Acceso no autorizado'}, 401
        
        return result[0]
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def complete_ticket(ticket_id, payment_status, jwt_payload):    
    try:
        # Verify that ticket_id is an INT
        try: ticket_id = int(ticket_id)
        except Exception as e: return {'error': 'Ticket no valido'}, 406

        def get_collector_id(ticket_id):
            global cnx, mssql_params
            query_get_id = """
                        SELECT u.idUsuario AS idRecolector, b.idBitacora AS ticketId
                        FROM USUARIOS u
                        JOIN BITACORA b ON u.idUsuario = b.idRecolector
                        WHERE b.idBitacora = %s;
                        """

            # Obtener datos para ver si es dueño del ticket
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_get_id, (ticket_id, ))
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_get_id, (ticket_id, ))
            
            result = cursor.fetchall()
            cursor.close()
            return result
        
        try:
            result = get_collector_id(ticket_id)
        except Exception as e:
            raise TypeError("Error al actualizar ticket: %s" % e)

        # Verificar si el ticket existe
        if len(result) == 0:
            return {'error': 'Ticket no encontrado'}, 404
        # Verificar que el recolector sea dueño del ticket
        if result[0]['idRecolector'] != jwt_payload['userId']:
            return {'error': 'Acceso no autorizado'}, 401
        
        
        def update_ticket(ticket_id, payment_status):
            global cnx, mssql_params
            query_update = """
                        UPDATE BITACORA
                        SET fechaVisita = GETDATE(), estatusPago = %s, estatusVisita = 1
                        WHERE idBitacora = %s;
                        """

            # Actualizar ticket a completado (recolectado)
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (payment_status, ticket_id, ))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (payment_status, ticket_id, ))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
        try:
            update_ticket(ticket_id)
        except Exception as e:
            return {'error': 'Error al actualizar ticket'}, 400

        return {'completado': f'Ticket {ticket_id} marcado como recolectado'}
        
    except Exception as e:
        return {'Error al marcar como recolectado el ticket'}, 400


def log_request(ip_address, user_agent, method, path, response_code, jwt):
    global cnx, mssql_params
    query = """
        INSERT INTO LOGS (ipAddress, userAgent, method, path, responseCode, token, fecha)
        VALUES (%s, %s, %s, %s, %s, %s, GETDATE());
        """
    
    try:
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (ip_address, user_agent, method, path, response_code, jwt))
            cnx.commit()  # Commit the changes to the database
            cursor.close()
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (ip_address, user_agent, method, path, response_code, jwt))
            cnx.commit()  # Commit the changes to the database
            cursor.close()
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def get_collector_daily_information(collector_id, jwt_payload):
    try:
        # Verify that collector_id is an INT
        try: collector_id = int(collector_id)
        except Exception as e: return {'error': 'Id recolector no valido'}, 406

        def get_manager_id(collector_id):
            global cnx, mssql_params
            query_get_id = """
                        SELECT idEncargado
                        FROM USUARIOS 
                        WHERE idUsuario = %s;
                        """

            # Obtener datos para ver si el id de manager es el correcto
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_get_id, (collector_id, ))
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_get_id, (collector_id, ))
            
            result = cursor.fetchall()
            cursor.close()
            return result
        
        try:
            result = get_manager_id(collector_id)
        except Exception as e:
            return {'error': 'Error al obtener id de manager'}, 400

        # Verificar que el recolector exista o que no sea un manager
        if len(result) == 0 or result[0]['idEncargado'] == None:
            return {'error': 'Recolector no encontrado'}, 404
        # Verificar que el id de manager sea el correcto
        if result[0]['idEncargado'] != jwt_payload['userId']:
            return {'error': 'Acceso no autorizado'}, 401
        
        def get_collector_information(collector_id):
            global cnx, mssql_params
            query_update = """
                        SELECT b.idRecolector, SUM(b.importe) AS montoEstimado, COALESCE(avance.montoRecolectado, 0) AS montoRecolectado, 
                            CASE 
                                WHEN EXISTS (
                                    SELECT 1
                                    FROM BITACORA b2
                                    WHERE b2.idRecolector = b.idRecolector
                                        AND b2.estatusPago = 0
                                ) THEN 'Pendiente'
                                ELSE 'Completado'
                            END AS estatusPago,
                            CASE 
                                WHEN EXISTS (
                                    SELECT 1
                                    FROM BITACORA b2
                                    WHERE b2.idRecolector = b.idRecolector
                                        AND b2.estatusVisita <> 0
                                    ) THEN 'En Ruta'
                                ELSE 'Sin Empezar'
                            END AS estatusVisita
                        FROM USUARIOS u
                        JOIN BITACORA b ON b.idRecolector = u.idUsuario
                        LEFT JOIN (
                            SELECT b2.idRecolector, SUM(b2.importe) as MontoRecolectado
                            FROM USUARIOS u2
                            JOIN BITACORA b2 ON b2.idRecolector = u2.idUsuario
                            WHERE u2.idUsuario = %s AND b2.estatusPago = 1 AND CONVERT(DATE, b2.fechaCobro) = CONVERT(DATE, GETDATE())
                            GROUP BY b2.idRecolector
                        ) avance ON avance.idRecolector = b.idRecolector
                        WHERE u.idUsuario= %s AND CONVERT(DATE, b.fechaCobro) = CONVERT(DATE, GETDATE())
                        GROUP BY b.idRecolector, avance.MontoRecolectado;
                        """

            # Obtener datos del recolector para ese dia
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (collector_id, collector_id ))
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (collector_id, collector_id))
                
            result = cursor.fetchall()
            cursor.close()
            return result
        
        try:
            result = get_collector_information(collector_id)
        except Exception as e:
            return {'error': 'Error obtener datos del recolector'}, 400
        
        if len(result) == 0:
            # TODO cambiar mensaje a JSON
            return "No hay informacion del recolector para el dia de hoy"
        
        resultado = {
                    "montoEstimado": result[0]['montoEstimado'], 
                    "montoRecolectado": result[0]['montoRecolectado'],
                    "idRecolector": result[0]['idRecolector'],
                    }

        if result[0]['estatusPago'] == 'Completado': resultado['estatus'] = 'Completado'
        elif result[0]['estatusVisita'] == 'En Ruta': resultado['estatus'] = 'En Ruta'
        else: resultado['estatus'] = 'Sin Empezar'

        return resultado
        
    except Exception as e:
        return {'Error al obtener los datos del recolector para el dia de hoy'}, 400
    

def get_manager_collectors(jwt_payload):
    try:
        # Verificar que el rol sea el de manager
        if jwt_payload['role'] != "manager":
            return {'error': 'Acceso no autorizado'}, 401
        
        def get_collectors_id(manager_id):
            global cnx, mssql_params
            query = "SELECT idUsuario FROM USUARIOS WHERE idEncargado = %s;"

            # Obtener datos del recolector para ese dia
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query, (manager_id, ))
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query, (manager_id, ))
                
            result = cursor.fetchall()
            cursor.close()
            return result
        
        try:
            collectors_id = get_collectors_id(jwt_payload['userId'])
        except Exception as e:
            return {'error': 'Error obteniendo ids de recolectores'}, 400

        def get_collector_information(collector_id):
            global cnx, mssql_params
            query = """
                    SELECT b.idRecolector AS idRecolector, b.idBitacora AS idTicket, b.importe, d.nombre + ' ' + d.apellidoPaterno nombre, d.direccion, b.estatusVisita AS estatus
                    FROM USUARIOS u
                    JOIN BITACORA b ON u.idUsuario = b.idRecolector
                    JOIN DONANTES d ON b.idDonante = d.idDonante
                    WHERE b.idRecolector = %s;
                    """

            # Obtener datos del recolector para ese dia
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query, (collector_id, ))
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query, (collector_id, ))
                
            result = cursor.fetchall()
            cursor.close()

            # Cambiar estatus de recoleccion a texto
            if len(result) != 0:
                for ticket in result:
                    if ticket['estatus'] == 0: ticket['estatus'] = 'Sin Empezar'
                    elif ticket['estatus'] == 1: ticket['estatus'] = 'En Ruta'
                    else: ticket['estatus'] = 'Completado'

            return result
        
        resultado = []
        try:
            for collector in collectors_id:
                resultado.append(get_collector_information(collector['idUsuario']))                
        except Exception as e:
            return {'error': 'Error obteniendo datos del recolector'}, 400
        
        if len(resultado) == 0:
            # TODO cambiar mensaje a JSON
            return "No hay informacion de los recolectores para el dia de hoy"
        
        return resultado
        
    except Exception as e:
        return {'Error al obtener los datos del recolector para el dia de hoy'}, 400


def get_list_collectors(jwt_payload):
    try:
        # Verificar que el rol sea el de manager
        if jwt_payload['role'] != "manager":
            return {'error': 'Acceso no autorizado'}, 401
        
        def get_collectors():
            global cnx, mssql_params
            query = "SELECT nombre + ' ' + apellidoPaterno AS nombre, idUsuario AS recolectorId FROM USUARIOS"

            # Obtener datos del recolector para ese dia
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query)
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query)
                
            result = cursor.fetchall()
            cursor.close()
            return result
        
        try:
            result = get_collectors()
        except Exception as e:
            return {'error': 'Error obteniendo el listado de recolectores'}, 400
        
        if len(result) == 0:
            # TODO cambiar mensaje a JSON
            return "No hay recolectores que mostrar"

        return result
        
    except Exception as e:
        return {'Error obtener listado de recolectores'}, 400


def change_ticket_collector(ticket_id, new_collector_id, jwt_payload):
    try:
        # Verify that ticket_id is an INT
        try: ticket_id = int(ticket_id)
        except Exception as e: return {'error': 'Ticket no valido'}, 406

        def get_manager_id(collector_id):
            global cnx, mssql_params
            query = """
                    SELECT idEncargado
                    FROM USUARIOS 
                    WHERE idUsuario = %s;
                    """

            # Obtener datos para ver si el id de manager es el correcto
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query, (collector_id, ))
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query, (collector_id, ))
            
            result = cursor.fetchall()
            cursor.close()
            return result
        
        try:
            result = get_manager_id(new_collector_id)
        except Exception as e:
            return {'error': 'Error al obtener id de manager'}, 400

        # Verificar que el recolector exista o que no sea un manager
        if len(result) == 0 or result[0]['idEncargado'] == None:
            return {'error': 'Recolector no encontrado'}, 404
        # Verificar que el id de manager sea el correcto
        if result[0]['idEncargado'] != jwt_payload['userId']:
            return {'error': 'Acceso no autorizado'}, 401
        

        def check_ticket_existence(ticket_id):
            global cnx, mssql_params
            query = """
                    SELECT *
                    FROM BITACORA
                    WHERE idBitacora = %s;
                    """

            # Obtener datos para ver si el id de manager es el correcto
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query, (ticket_id, ))
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query, (ticket_id, ))
            
            result = cursor.fetchall()
            cursor.close()
            return result
        
        try:
            result = check_ticket_existence(ticket_id)
        except Exception as e:
            return {'error': 'Error al obtener id de manager'}, 400
        
        # Verificar si el ticket existe
        if len(result) == 0:
            return {'error': 'Ticket no encontrado'}, 404
                
        
        def update_ticket(ticket_id, new_collector_id):
            global cnx, mssql_params
            query_update = """
                        UPDATE BITACORA
                        SET idRecolector = %s
                        WHERE idBitacora = %s;
                        """

            # Actualizar ticket a completado (recolectado)
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (new_collector_id, ticket_id, ))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (new_collector_id, ticket_id, ))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
        try:
            update_ticket(ticket_id, new_collector_id)
        except Exception as e:
            return {'error': 'Error al actualizar ticket'}, 400

        return {'completado': f'Ticket {ticket_id} asignado a recolector con id: {new_collector_id}'}
        
    except Exception as e:
        return {'Error al marcar como recolectado el ticket'}, 400


# TODO
def mark_visit(ticket_id, jwt_payload):
    pass


# TODO
def set_comment(ticket_id, comment, jwt_payload):
    pass


# TODO
def get_manager_ticket_information(ticket_id, jwt_payload):
    pass


if __name__ == '__main__':
    import json
    mssql_params = {}
    mssql_params['DB_HOST'] = os.getenv('DB_HOST')
    mssql_params['DB_NAME'] = os.getenv('DB_NAME')
    mssql_params['DB_USER'] = os.getenv('DB_USER')
    mssql_params['DB_PASSWORD'] = os.getenv('DB_PASSWORD')

    cnx = mssql_connect(mssql_params)