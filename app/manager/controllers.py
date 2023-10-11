from app.config.mssql import mssql_connect
import pymssql

def get_list_collectors(jwt_payload):
    try:
        # Verificar que el rol sea el de manager
        if jwt_payload['role'] != "manager":
            return {'error': 'Acceso no autorizado'}, 401
        
        def get_collectors(manager_id):
            global cnx, mssql_params
            query = """
                    SELECT nombre + ' ' + apellidoPaterno AS nombre, idUsuario AS recolectorId 
                    FROM USUARIOS
                    WHERE idEncargado = %s
                    """

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
            result = get_collectors(jwt_payload['userId'])
        except Exception as e:
            return {'error': 'Error obteniendo el listado de recolectores'}, 400
        
        if len(result) == 0:
            # TODO cambiar mensaje a JSON
            return "No hay recolectores que mostrar"

        return result
        
    except Exception as e:
        return {'Error obtener listado de recolectores'}, 400
    

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
            query = "SELECT nombre + ' ' + apellidoPaterno AS nombre, idUsuario FROM USUARIOS WHERE idEncargado = %s;"

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
                    SELECT b.idBitacora AS idTicket, b.importe, d.nombre + ' ' + d.apellidoPaterno nombre, d.direccion + ', ' + CONVERT(VARCHAR, d.codigoPostal) + ', ' + d.municipio AS direccion, b.estatusVisita AS estatus, b.estatusPago AS estatusPago
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
                    # if ticket['estatusPago'] != None and ticket['estatusPago'] == 2: ticket['estatusPago'] = 'No recolectado'
                    if ticket['estatus'] == 0: ticket['estatus'] = 'Sin Empezar'
                    elif ticket['estatus'] == 1: ticket['estatus'] = 'En Ruta'
                    else: ticket['estatus'] = 'Recolectado'

            return result
        
        resultado = []
        try:
            for collector in collectors_id:
                temp = {}
                # resultado.append(get_collector_information(collector['idUsuario']))
                temp['recolectorId'] = collector['idUsuario']
                temp['nombre'] = collector['nombre']
                temp['tickets'] = get_collector_information(collector['idUsuario'])
                temp['numTickets'] = len(temp['tickets'])

                if len(temp['tickets']) == 0:
                    continue
                resultado.append(temp)
        except Exception as e:
            return {'error': 'Error obteniendo datos del recolectora'}, 400
        
        if len(resultado) == 0:
            # TODO cambiar mensaje a JSON
            return "No hay informacion de los recolectores para el dia de hoy"
        
        return resultado
        
    except Exception as e:
        return {'Error al obtener los datos del recolector para el dia de hoy'}, 400
    

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
def get_manager_ticket_information(ticket_id, jwt_payload):
    pass