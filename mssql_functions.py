import pymssql
import bcrypt
import jwt
from flask import jsonify
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
        print("Error al iniciar sesion:", e)
        raise TypeError("Error al iniciar sesion: %s" % e)


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
            cursor.execute(query, (username))
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (username))
        
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
        return {'error': e}, 401


def get_collector_tickets(user_id, jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT b.idBitacora, b.importe, d.nombre+ ' ' + d.apellidoPaterno AS nombre, d.direccion
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
            cursor.execute(query, (user_id,))
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (user_id,))

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
            cursor.execute(query, (ticket_id,))
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (ticket_id,))
        
        result = cursor.fetchall()
        cursor.close()

        if len(result) == 0:
            return {'error': 'Ticket no encontrado'}, 404
        if result[0]['idRecolector'] != jwt_payload['userId']:
            return {'error': 'Acceso no autorizado'}, 401
        
        return result[0]
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def complete_ticket(ticket_id, jwt_payload):    
    try:
        # Verificar que ticket_id sea un entero
        try: ticket_id = int(ticket_id)
        except Exception as e: return {'error': 'Ticket no valido'}, 406

        def get_recolector_id(ticket_id):
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
                cursor.execute(query_get_id, (ticket_id,))
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_get_id, (ticket_id,))
            
            result = cursor.fetchall()
            cursor.close()
            return result
        
        try:
            result = get_recolector_id(ticket_id)
        except Exception as e:
            raise TypeError("Error al actualizar ticket: %s" % e)

        # Verificar si el ticket existe
        if len(result) == 0:
            return {'error': 'Ticket no encontrado'}, 404
        # Verificar que el recolector sea dueño del ticket
        if result[0]['idRecolector'] != jwt_payload['userId']:
            return {'error': 'Acceso no autorizado'}, 401
        
        
        def update_ticket(ticket_id):
            global cnx, mssql_params
            query_update = """
                        UPDATE BITACORA
                        SET fechaVisita = GETDATE(), estatusPago = 1, estatusVisita = 1
                        WHERE idBitacora = %s;
                        """

            # Actualizar ticket a completado (recolectado)
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (ticket_id,))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (ticket_id,))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
        try:
            update_ticket(ticket_id)
        except Exception as e:
            return {'error': 'Error al actualizar ticket'}, 400

        return jsonify(f'Ticket {ticket_id} marcado como recolectado')
        
    except Exception as e:
        return {'Error al marcar como recolectado el ticket'}, 400


if __name__ == '__main__':
    import json
    mssql_params = {}
    mssql_params['DB_HOST'] = os.getenv('DB_HOST')
    mssql_params['DB_NAME'] = os.getenv('DB_NAME')
    mssql_params['DB_USER'] = os.getenv('DB_USER')
    mssql_params['DB_PASSWORD'] = os.getenv('DB_PASSWORD')

    cnx = mssql_connect(mssql_params)