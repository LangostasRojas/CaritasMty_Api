from flask import make_response, request, Blueprint
import sys

from app import app, CNX
from app.collector import controllers
from app. middleware.middleware import exclude_middleware
from app.helpers.check_requests import check_parameters

controllers.cnx = CNX

collector_bp = Blueprint('collector', __name__)

# TODO - Change route in frontend to /get-collector-tickets (Quizas se ocupe hacer modificaciones en frontend en como se llaman las variables que recibe)
# Ver los tickets que tiene asignados un recolector (App Recolector)
# Regresa (lista) - idTicket, importe, nombre (donante), direccion
@app.route("/get-recolector-tickets", methods=['GET'])
# @app.route("/get-collector-tickets", methods=['GET'])
def get_recolector_tickets():
    # Checar que se proporciono el id del recolector
    if check_parameters(request.args.keys(), ['userId']):
        return make_response({'error': 'Bad request'}, 400)
    
    user_id = request.args.get('userId')

    response = controllers.get_collector_tickets(user_id, request.userJWT)

    return make_response(response)


# Ver los datos especificos de un ticket (App Recolector)
# Regresa - idRecolector, idTicket, importe, nombre (donante), direccion
@app.route("/get-ticket-information", methods=['GET'])
def get_ticket_information():
    # Checar que se proporciono el id del ticket
    if check_parameters(request.args.keys(), ['ticketId']):
        return make_response({'error': 'Bad request'}, 400)

    ticket_id = request.args.get('ticketId')

    response = controllers.get_ticket_information(ticket_id, request.userJWT)

    return make_response(response)


# Marcar un ticket como completado (App Recolector)
# Marcar ticket como recolectado (1) o no recolectado (2)
@app.route("/mark-completed", methods=['POST'])
def complete_ticket():
    # Mark a ticket as collected
    req = request.json

    # Checar que se proporciono el id del ticket y estatus (0: pendiente, 1: recolectado, 2: no recolectado)
    if check_parameters(req.keys(), ['ticketId', 'estatus']):
        return make_response({'error': 'Bad request'}, 400)

    ticket_id = req['ticketId']
    status = req['estatus']

    response = controllers.complete_ticket(ticket_id, status, request.userJWT)

    return make_response(response)


# Marcar el estatus de visita de un ticket (App Recolector)
# estatusVisita: 0 - Pendiente, 1 - En camino, 2 - Visitado
@app.route("/mark-visit", methods=['POST'])
def mark_visit():
    # Mark a ticket as visited
    req = request.json

    # Checar que se proporciono el id del ticket y estatus (0: pendiente, 1: en camino, 2: visitado)
    if check_parameters(req.keys(), ['ticketId', 'estatus']):
        return make_response({'error': 'Bad request'}, 400)

    ticket_id = req['ticketId']
    status = req['estatus']

    response = controllers.mark_visit(ticket_id, status, request.userJWT)

    return make_response(response)


# Escribir un comentario en un ticket (App Recolector)
@app.route("/set-comment", methods=['POST'])
def set_comment():
    # Set comment to a ticket
    req = request.json

    # Checar que se proporciono el id del ticket y el comentario
    if check_parameters(req.keys(), ['ticketId', 'comment']):
        return make_response({'error': 'Bad request'}, 400)
    
    response = controllers.set_comment(req['ticketId'], req['comment'], request.userJWT)

    return make_response(response)


# Enviar lista de comentarios disponibles (App Recolector)
# Regresa (json) - idComentario, comentario
@exclude_middleware
@app.route("/get-list-comments", methods=['GET'])
def list_comments():
    if check_parameters(request.args.keys(), {}):
        return make_response({'error': 'Bad request'}, 400)

    response = controllers.list_comments()

    return make_response(response)


# Enviar lista de comentarios disponibles (App Recolector)
# Regresa (json) - idComentario, comentario
@app.route("/get-geolocation", methods=['GET'])
def get_ticket_geolocation():
    # Checar que se proporciono el id del ticket
    if check_parameters(request.args.keys(), ['ticketId']):
        return make_response({'error': 'Bad request'}, 400)

    ticket_id = request.args.get('ticketId')

    response = controllers.get_ticket_geolocation(ticket_id, request.userJWT)

    return make_response(response)