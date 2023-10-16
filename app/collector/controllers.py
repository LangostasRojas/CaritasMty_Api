from flask import jsonify
from app.config.mssql import mssql_connect
import pymssql
import requests
from app import GOOGLE_MAPS_API_KEY

def get_collector_tickets(user_id, jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT b.idBitacora AS idTicket, b.importe AS importe, d.nombre + ' ' + d.apellidoPaterno AS nombre, d.direccion, b.estatusVisita
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
        return jsonify(result)

    except Exception as e:
        return {'error': 'Ocurrio un error al obtener tickets de recolector'}


def get_ticket_information(ticket_id, jwt_payload):
    global cnx, mssql_params
    query = """
            SELECT b.idRecolector AS idRecolector, b.idBitacora AS idTicket, b.importe, d.nombre + ' ' + d.apellidoPaterno nombre, d.direccion + ', ' + CONVERT(VARCHAR, d.codigoPostal) + ', ' + d.municipio AS direccion
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
        
        return jsonify(result[0])
        
    except Exception as e:
        return {'Error al obtener datos de ticket'}, 401


def complete_ticket(ticket_id, payment_status, jwt_payload):    
    try:
        # Verify that ticket_id is an INT
        try: 
            ticket_id = int(ticket_id)
            payment_status = int(payment_status)
        except Exception as e: return {'error': 'Campos no validos'}, 406

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
                        SET fechaVisita = GETDATE(), estatusPago = %s, estatusVisita = 2
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
            update_ticket(ticket_id, payment_status)
        except Exception as e:
            return {'error': 'Error al actualizar ticket'}, 400

        return {'completado': f'Ticket {ticket_id} marcado como recolectado'}
        
    except Exception as e:
        return {'Error al marcar como recolectado el ticket'}, 400
    

def mark_visit(ticket_id, status, jwt_payload):    
    try:
        # Verify that ticket_id is an INT
        try: 
            ticket_id = int(ticket_id)
            status = int(status)
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
            raise TypeError("Error al cambiar estatus de ticket: %s" % e)

        # Verificar si el ticket existe
        if len(result) == 0:
            return {'error': 'Ticket no encontrado'}, 404
        # Verificar que el recolector sea dueño del ticket
        if result[0]['idRecolector'] != jwt_payload['userId']:
            return {'error': 'Acceso no autorizado'}, 401
        
        
        def update_status(ticket_id, status):
            global cnx, mssql_params

            if(status not in [0,1,2]):
                return {'error': 'Status no correcto' }

            query_update = """
                        UPDATE BITACORA
                        SET estatusVisita = %s
                        Where idBitacora = %s;
                        """
            # Actualizar ticket a completado (recolectado)
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (status, ticket_id, ))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (status, ticket_id, ))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
        try:
            update_status(ticket_id, status)
        except Exception as e:
            return {'error': f'Error al insertar cambiar status {e} ' }, 400

        return {'completado': f'Status cambiado para el ticket {ticket_id}'}
        
    except Exception as e:
        return {'Error al insertar comentario'}, 400
    

# TODO
def set_comment(ticket_id, comment_id, jwt_payload):    
    try:
        # Verify that ticket_id and comment is an INT
        try: 
            ticket_id = int(ticket_id)
            comment_id = int(comment_id)
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
            raise TypeError("Error al insertar comentario: %s" % e)

        # Verificar si el ticket existe
        if len(result) == 0:
            return {'error': 'Ticket no encontrado'}, 404
        # Verificar que el recolector sea dueño del ticket
        if result[0]['idRecolector'] != jwt_payload['userId']:
            return {'error': 'Acceso no autorizado'}, 401
        
        
        def update_comment(ticket_id, comment):
            global cnx, mssql_params

            query_update = """
                        UPDATE BITACORA
                        SET comentarios = %s
                        WHERE idBitacora = %s;
                        """
            # Actualizar ticket a completado (recolectado)
            try:
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (comment, ticket_id, ))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
            except pymssql._pymssql.InterfaceError:
                print("La langosta se esta conectando...")
                cnx = mssql_connect(mssql_params)
                cursor = cnx.cursor(as_dict=True)
                cursor.execute(query_update, (comment, ticket_id, ))
                cnx.commit()  # Commit the changes to the database
                cursor.close()
        try:
            update_comment(ticket_id, comment_id)
        except Exception as e:
            return {'error': f'Error al insertar comentaro {e} ' }, 400

        return {'completado': f'Comentario añanido en Ticket {ticket_id}'}
        
    except Exception as e:
        return {'Error al insertar comentario'}, 400


def list_comments():
    try:        
        global cnx, mssql_params

        query = "SELECT idComentario AS id, comentario AS comment FROM COMENTARIOS"

        # Obtener datos para ver si es dueño del ticket
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
        return jsonify(result)
        
    except Exception as e:
        return {'Error al obtener la lista de comentarios'}, 400
    

def get_ticket_geolocation(ticket_id, jwt_payload):
    try:        
        global cnx, mssql_params

        query = """
                SELECT d.direccion + ',' + d.municipio AS direccion
                FROM BITACORA b
                JOIN DONANTES d ON b.idDonante = d.idDonante
                WHERE b.idBitacora = %s;
                """

        # Obtener datos para ver si es dueño del ticket
        try:
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query, (ticket_id, ))
        except pymssql._pymssql.InterfaceError:
            print("La langosta se esta conectando...")
            cnx = mssql_connect(mssql_params, (ticket_id, ))
            cursor = cnx.cursor(as_dict=True)
            cursor.execute(query)
        
        result = cursor.fetchall()
        cursor.close()

        # Verificar si el ticket existe
        if len(result) == 0:
            return {'error': 'Ticket no encontrado'}, 404
        
        response = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address={result[0]['direccion']}&key={GOOGLE_MAPS_API_KEY}")
        
        return response.json()['results'][0]['geometry']['location']
        
    except Exception as e:
        return {'Error al obtener la lista de comentarios'}, 400