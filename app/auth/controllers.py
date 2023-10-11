from app.config.mssql import mssql_connect
import pymssql
import bcrypt
import jwt
import datetime
cnx = None
mssql_params = {}
from app import ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY

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
        return {'error': 'Error al iniciar sesion'}, 401