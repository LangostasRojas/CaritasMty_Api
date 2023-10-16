from flask import make_response, request, Blueprint
import sys

from app import app, CNX
from app.manager import controllers
from app.manager import controllers_kpis
from app.middleware.middleware import exclude_middleware
from app.helpers.check_requests import check_parameters

controllers.cnx = CNX
controllers_kpis.cnx = CNX

manager_bp = Blueprint('manager', __name__)

# Ayuda a generar un dropdown en el frontend y elegir un recolector diferente para un ticket (App Manager)
# Rgresa (lista) - nombre y idRecolector (pertenecen al manager)
@app.route("/get-list-collectors", methods=['GET'])
def get_list_collectors():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)
    
    # Return list of collectors
    response = controllers.get_list_collectors(request.userJWT)

    return make_response(response)


# Ver datos especificos de un recolector de ese dia (App Manager)
# Regresa - idRecolector, montoEstimado, montoRecolectado, estatusPago, estatusVisita
@app.route("/get-collector-daily-information", methods=['GET'])
def get_collector_daily_information():
    # Check if collectorId is provided in request
    if check_parameters(request.args.keys(), ['collectorId']):
        return make_response({'error': 'Bad request'}, 400)

    collector_id = request.args.get('collectorId')

    response = controllers.get_collector_daily_information(collector_id, request.userJWT)

    return make_response(response)


# Pantalla de inicio de la app manager (App Manager)
# Muestra lista recolectores con lista de tickets asignados
# Regresa (lista 2D) - idRecolector, idTicket, importe, nombre, estatus (estatusVisita)
@app.route("/get-manager-collectors", methods=['GET'])
def get_manager_collectors():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)

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

    if check_parameters(req.keys(), ['ticketId', 'collectorId']):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers.change_ticket_collector(req['ticketId'], req['collectorId'], request.userJWT)
    
    return make_response(response)


# TODO - crear ruta para ver informacion especifica de un ticket (App Manager)
# Ver datos especificos de un ticket (App Manager)
# Regresa - idRecolector, idTicket, importe, nombre (donante), direccion, comentario, estatus (mismo subqueries que tiene get-collector-daily-information)
@app.route("/get-manager-ticket-information", methods=['GET'])
def get_manager_ticket_information():
    # Check if ticketId is provided in request
    if check_parameters(request.args.keys(), ['ticketId']):
        return make_response({'error': 'Bad request'}, 400)

    ticket_id = request.args.get('ticketId')

    response = controllers.get_manager_ticket_information(ticket_id, request.userJWT)

    return make_response(response)


# Ayuda a generar reporte de los tickets de ese dia
# Regresa - idRecibo, idDonante, importe, estatusPago (bool), comentario
@app.route("/get-report-information", methods=['GET'])
def get_report_information():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)

    response = controllers_kpis.get_report_information(request.userJWT)

    return make_response(response)

# Ver donaciones por municipio en todo el tiempo
# Regresa - municipio, ingresos
@app.route("/get-zone-donations", methods=['GET'])
def get_zone_donations():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers_kpis.get_zone_donations(request.userJWT)

    return make_response(response)

# Ver tickets recolectados en todo el tiempo
# Regresa - total, recolectado, porcentaje
@app.route("/get-completion-rate", methods=['GET'])
def get_completion_rate():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers_kpis.get_completion_rate(request.userJWT)

    return make_response(response)


# Promedio de tickets en los ultimos 7 dias
# Regresa - total, recolectado, porcentaje, fecha
@app.route("/get-average-tickets", methods=['GET'])
def get_average_tickets():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers_kpis.get_average_tickets(request.userJWT)

    return make_response(response)


# Ver donaciones esperadas para el dia de hoy
# Regresa donacionesEsperadas
@app.route("/get-expected-donations", methods=['GET'])
def get_expected_donations():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers_kpis.get_expected_donations(request.userJWT)

    return make_response(response)


@app.route("/get-completion-rate-by-collector", methods=['GET'])
def get_completion_rate_by_collector():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers_kpis.get_completion_rate_by_collector(request.userJWT)

    return make_response(response)


@app.route("/get-collected-tickets-current-month", methods=['GET'])
def get_collected_tickets_c_month():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers_kpis.get_collected_tickets_c_month(request.userJWT)

    return make_response(response)


@app.route("/get-collected-tickets-month", methods=['GET'])
def get_collected_tickets_month():
    # Checar los argumentos
    if check_parameters(request.args.keys(), []):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers_kpis.get_collected_tickets_month(request.userJWT)

    return make_response(response)