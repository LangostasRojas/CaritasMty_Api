from flask import make_response, request, Blueprint
import sys

from app import app, CNX
from app.manager import controllers
from app.middleware.middleware import exclude_middleware

controllers.cnx = CNX

manager_bp = Blueprint('manager', __name__)

# Ayuda a generar un dropdown en el frontend y elegir un recolector diferente para un ticket (App Manager)
# Rgresa (lista) - nombre y idRecolector (pertenecen al manager)
@app.route("/get-list-collectors", methods=['GET'])
def get_list_collectors():
    # Return list of collectors
    response = controllers.get_list_collectors(request.userJWT)

    return make_response(response)


# Ver datos especificos de un recolector de ese dia (App Manager)
# Regresa - idRecolector, montoEstimado, montoRecolectado, estatusPago, estatusVisita
@app.route("/get-collector-daily-information", methods=['GET'])
def get_collector_daily_information():
    # Check if collectorId is provided in request
    if 'collectorId' not in request.args:
        return make_response({'error': 'Bad request'}, 400)

    collector_id = request.args.get('collectorId')

    response = controllers.get_collector_daily_information(collector_id, request.userJWT)

    return make_response(response)


# Pantalla de inicio de la app manager (App Manager)
# Muestra lista recolectores con lista de tickets asignados
# Regresa (lista 2D) - idRecolector, idTicket, importe, nombre, estatus (estatusVisita)
@app.route("/get-manager-collectors", methods=['GET'])
def get_manager_collectors():
    # Return list of collectors and their tickets: 
    #  (Collectors have to be related to a manager)
    response = controllers.get_manager_collectors(request.userJWT)

    return make_response(response)


# Cambiar el recolector de un ticket (App Manager)
@app.route("/change-ticket-collector", methods=['PUT'])
def change_ticket_collector():
    # Change the collector of a ticket
    # Checar que se proporciono el id del ticket
    req = request.json

    if 'ticketId' not in req or 'collectorId' not in req:
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers.change_ticket_collector(req['ticketId'], req['collectorId'], request.userJWT)
    
    return make_response(response)


# TODO - crear ruta para ver informacion especifica de un ticket (App Manager)
# Ver datos especificos de un ticket (App Manager)
# Regresa - idRecolector, idTicket, importe, nombre (donante), direccion, comentario, estatus (mismo subqueries que tiene get-collector-daily-information)
@app.route("/get-manager-ticket-information", methods=['GET'])
def get_manager_ticket_information():
    # Check if ticketId is provided in request
    if 'ticketId' not in request.args:
        return make_response({'error': 'Bad request'}, 400)

    ticket_id = request.args.get('ticketId')

    response = controllers.get_manager_ticket_information(ticket_id, request.userJWT)

    return make_response(response)
