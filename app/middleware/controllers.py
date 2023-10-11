from app.config.mssql import mssql_connect
import pymssql
cnx = None
mssql_params = {}

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