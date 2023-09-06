import pymssql
import bcrypt
import jwt
import datetime
import time
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
    query = 'UPDATE USUARIOS SET refreshtoken = %s WHERE id_usuario = %s;'

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
        cursor.execute(query, (token,))
        cnx.commit()  # Commit the changes to the database
        cursor.close()
    except Exception as e:
        print("Error al iniciar sesion:", e)
        raise TypeError("Error al iniciar sesion: %s" % e)


def sign_in(username, password):
    global cnx, mssql_params, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY
    username_value = username['username']
    password_value = password['password']
    # Parametrized query (allows only strings)
    query = 'SELECT id_usuario, username, role, password FROM USUARIOS WHERE username = %s;'

    try:
        try:
            cursor = cnx.cursor(as_dict=True)
            # Execute query using username as parameter
            cursor.execute(query, (username_value))
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (username_value))
        
        result = cursor.fetchall()
        user_password = result[0]['password'].encode('utf-8')
        
        cursor.close()

        if bcrypt.checkpw(password_value.encode('utf-8'),user_password):      
            resultado = {
                            "userId": result[0]['id_usuario'], 
                            "userName": result[0]['username'], 
                            # "name": result[0]['name'], 
                            # "lastName": result[0]['lastname'], 
                            "role": result[0]['role'],
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
        # raise TypeError("Error al iniciar sesion: %s" % e)


def get_recolector_tickets(user_id, jwt_payload):
    global cnx, mssql_params, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY
    # query = """
    #         SELECT * t.ID_NUM_PAGO, t.IMPORTE,
    #         """

    try:
        if 'userId' in jwt_payload and jwt_payload['userId'] != int(user_id):
            return {'error': 'Acceso no autorizado'}, 401

        return [
            {'idTicket': 1234, 'importe': 100.00, 'direccion': 'Calle 1', 'nombre': 'Juan'},
            {'idTicket': 1234, 'importe': 100.00, 'direccion': 'Calle 1', 'nombre': 'Juan'},
            {'idTicket': 1234, 'importe': 100.00, 'direccion': 'Calle 1', 'nombre': 'Juan'},
            ], 200

    except Exception as e:
        return {'error': 'Ocurrio un error al obtener tickets de recolector'}
        # raise TypeError(f"Error al obtener tickets de recolector: {userId}. Error: {e}")
    


if __name__ == '__main__':
    import json
    mssql_params = {}
    mssql_params['DB_HOST'] = os.getenv('DB_HOST')
    mssql_params['DB_NAME'] = os.getenv('DB_NAME')
    mssql_params['DB_USER'] = os.getenv('DB_USER')
    mssql_params['DB_PASSWORD'] = os.getenv('DB_PASSWORD')

    cnx = mssql_connect(mssql_params)