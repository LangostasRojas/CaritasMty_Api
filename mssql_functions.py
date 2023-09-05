import pymssql
import bcrypt
import jwt

cnx = None
mssql_params = {}
ACCESS_TOKEN_KEY = "637c9e8eff1fda4ce059ea3a4ff307bfb3015aa598171c6e19bfaf02b66e8c6c"
REFRESH_TOKEN_KEY = "86ec9822ce887f3efe08d207c1f9ddc2d22573180a124347fe7247ed1d27e477"

def mssql_connect(sql_creds):
    import pymssql
    cnx = pymssql.connect(
        server=sql_creds['DB_HOST'],
        user=sql_creds['DB_USER'],
        password=sql_creds['DB_PASSWORD'],
        database=sql_creds['DB_NAME'])
    return cnx


def sign_in(username, password):
    global cnx, mssql_params, ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY
    username_value = username['username']
    password_value = password['password']
    # Parametrized query (allows only strings)
    query = 'SELECT userid, username, name, lastname, role, password FROM [user] WHERE username = %s;'

    try:
        try:
            cursor = cnx.cursor(as_dict=True)
            # Execute query using username as parameter
            cursor.execute(query, (username_value))
        except pymssql._pymssql.InterfaceError:
            pass
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params)
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (username_value))
        
        result = cursor.fetchall()
        user_password = result[0]['password'].encode('utf-8')
        
        cursor.close()

        if bcrypt.checkpw(password['password'].encode('utf-8'),user_password):      
            resultado = {"userId": result[0]['userid'], 
                         "userName": result[0]['username'], 
                         "name": result[0]['name'], 
                         "lastName": result[0]['lastname'], 
                         "role": result[0]['role'],
                         }
            accessToken = jwt.encode(resultado, ACCESS_TOKEN_KEY, algorithm='HS256')
            refreshToken = jwt.encode(resultado, REFRESH_TOKEN_KEY, algorithm='HS256')
            resultado['accessToken'] = accessToken
            resultado['refreshToken'] = refreshToken

            return resultado
        else:
            return {'error': 'Usuario o contraseña incorrectos'}
        
    except Exception as e:
        raise TypeError("Error al iniciar sesion: %s" % e)


if __name__ == '__main__':
    import json
    mssql_params = {}
    mssql_params['DB_HOST'] = '10.14.255.66'
    mssql_params['DB_NAME'] = 'Caritas'
    mssql_params['DB_USER'] = 'SA'
    mssql_params['DB_PASSWORD'] = 'Shakira123.'
    cnx = mssql_connect(mssql_params)