from flask import Flask, make_response, request, g
import sys
import mssql_functions as MSSql
from dotenv import load_dotenv
import os
import jwt
import time

# Cargar variables de entorno
load_dotenv()
# Connect to mssql dB from start
mssql_params = {}
# mssql_params['DB_HOST'] = '100.80.80.7'
mssql_params['DB_HOST'] = os.getenv('DB_HOST')
mssql_params['DB_NAME'] = os.getenv('DB_NAME')
mssql_params['DB_USER'] = os.getenv('DB_USER')
mssql_params['DB_PASSWORD'] = os.getenv('DB_PASSWORD')
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')

try:
    MSSql.cnx = MSSql.mssql_connect(mssql_params)
except Exception as e:
    print("Cannot connect to mssql server!: {}".format(e))
    sys.exit()

app = Flask(__name__)


# Excluir middleware
def exclude_middleware(func):
    func._exclude_middleware = True
    return func

# Middlweware
@app.after_request
def log_request(response):
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    method = request.method
    path = request.path
    response_code = response.status_code
    jwt = g.get('userJWT', None)

    MSSql.log_request(ip_address, user_agent, method, path, response_code, jwt)
    return response


@app.before_request
def verify_jwt():
    # No verificar token de acceso si el endpoint esta excluido
    verify_jwt_middleware = True
    if request.endpoint in app.view_functions:
        view_func = app.view_functions[request.endpoint]
        verify_jwt_middleware = not hasattr(view_func, '_exclude_middleware')
    # Si el endpoint esta excluido, no verificar token de acceso
    if not verify_jwt_middleware: return

    
    global ACCESS_TOKEN_KEY
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return make_response({'error': 'No se proporciono token de acceso'}, 401)
    
    # Extraer token de acceso sin el prefijo 'Bearer '
    access_token = auth_header.replace('Bearer ', '')

    try:
        payload = jwt.decode(access_token, ACCESS_TOKEN_KEY, algorithms=['HS256'])

        # Verificar si el token esta caducado
        if 'exp' in payload and payload['exp'] < int(time.time()):
            return {'error': 'Token de acceso caducado'}, 401
        request.userJWT = payload
        g.userJWT = access_token
    
    except jwt.ExpiredSignatureError:
        return {'error': 'Token de acceso caducado'}, 401
    except jwt.DecodeError:
        return {'error': 'Token de acceso invalido'}, 401
    except Exception as e:
        return {'error': "Error al verificar token de acceso"}, 401


@app.route("/hello")
@exclude_middleware
def hello():
    return "Las langostas rojas de Xalapa te saludan de vuelta!\n"


@app.route("/sign-in", methods=['POST'])
@exclude_middleware
def sign_in():
    req = request.json
    
    # Checar que se proporcionaron los datos necesarios
    if req['username'] is None or req['password'] is None:
        return make_response({'error': 'Bad request'}, 400)
    
    username = req['username']
    password = req['password']

    response = MSSql.sign_in(username, password)

    return make_response(response)


# TODO - Change route in frontend to /get-collector-tickets
@app.route("/get-recolector-tickets", methods=['GET'])
# @app.route("/get-collector-tickets", methods=['GET'])
def get_recolector_tickets():
    # Checar que se proporciono el id del recolector
    if 'userId' not in request.args:
        return make_response({'error': 'Bad request'}, 400)
    
    user_id = request.args.get('userId')

    response = MSSql.get_collector_tickets(user_id, request.userJWT)

    return make_response(response)


@app.route("/get-ticket-information", methods=['GET'])
def get_ticket_information():
    # Checar que se proporciono el id del ticket
    if 'ticketId' not in request.args:
        return make_response({'error': 'Bad request'}, 400)

    ticket_id = request.args.get('ticketId')

    response = MSSql.get_ticket_information(ticket_id, request.userJWT)

    return make_response(response)


@app.route("/mark-completed", methods=['POST'])
def complete_ticket():
    # Mark a ticket as collected
    # TODO - Select whether the ticket was collected or not
    req = request.json

    # Checar que se proporciono el id del ticket
    if 'ticketId' not in req:
        return make_response({'error': 'Bad request'}, 400)

    ticket_id = req['ticketId']

    response = MSSql.complete_ticket(ticket_id, request.userJWT)

    return make_response(response)


@app.route("/get-list-collectors", methods=['GET'])
def get_list_collectors():
    # Return list of collectors
    response = MSSql.get_list_collectors(request.userJWT)

    return make_response(response)


@app.route("/get-collector-daily-information", methods=['GET'])
def get_collector_daily_information():
    # Return the daily information of a collector: total collected, estimated collected, estatus. Has to be related to a manager
    # Check if collectorId is provided in request
    if 'collectorId' not in request.args:
        return make_response({'error': 'Bad request'}, 400)

    collector_id = request.args.get('collectorId')

    response = MSSql.get_collector_daily_information(collector_id, request.userJWT)

    return make_response(response)


@app.route("/get-manager-collectors", methods=['GET'])
def get_manager_collectors():
    # Return list of collectors and their tickets: 
    #  (Collectors have to be related to a manager)
    response = MSSql.get_manager_collectors(request.userJWT)

    return make_response(response)


# TODO
@app.route("/change-ticket-collector", methods=['PUT'])
def change_ticket_collector():
    # Change the collector of a ticket
    # Checar que se proporciono el id del ticket
    req = request.json

    if 'ticketId' not in req or 'collectorId' not in req:
        return make_response({'error': 'Bad request'}, 400)
    
    response = MSSql.change_ticket_collector(req['ticketId'], req['collectorId'], request.userJWT)
    
    return make_response(response)


# TODO
@app.route("/get-user-information", methods=['GET'])
def get_user_information():
    # Return name, lastname and image of user
    pass


if __name__ == '__main__':
    print ("Running API...")
    app.run(host='0.0.0.0', port=10201, debug=True)