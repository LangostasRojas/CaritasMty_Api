from flask import Flask, make_response, request, jsonify
import json
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
REFRESH_TOKEN_KEY = os.getenv('REFRESH_TOKEN_KEY')

try:
    MSSql.cnx = MSSql.mssql_connect(mssql_params)
except Exception as e:
    print("Cannot connect to mssql server!: {}".format(e))
    sys.exit()

app = Flask(__name__)


# MIddlweware
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
        return make_response(jsonify({'error': 'No se proporciono token de acceso'}), 401)
    
    # Extraer token de acceso sin el prefijo 'Bearer '
    access_token = auth_header.replace('Bearer ', '')

    try:
        payload = jwt.decode(access_token, ACCESS_TOKEN_KEY, algorithms=['HS256'])

        # Verificar si el token esta caducado
        if 'exp' in payload and payload['exp'] < int(time.time()):
            return {'error': 'Token de acceso caducado'}, 401
        request.userJWT = payload
    
    except jwt.ExpiredSignatureError:
        return {'error': 'Token de acceso caducado'}, 401
    except jwt.DecodeError:
        return {'error': 'Token de acceso invalido'}, 401
    except Exception as e:
        raise TypeError("Error al verificar token de acceso: %s" % e)


def exclude_middleware(func):
    func._exclude_middleware = True
    return func


@app.route("/hello")
def hello():
    return "Las langostas rojas de Xalapa te saludan de vuelta!\n"


@app.route("/sign-in", methods=['POST'])
@exclude_middleware
def sign_in():
    req = request.json
    username = {'username': req['username']}
    password = {'password': req['password']}

    response = MSSql.sign_in(username, password)

    return make_response(response)


@app.route("/get-recolector-tickets", methods=['GET'])
def get_recolector_tickets():
    userId = request.args.get('userId')

    response = MSSql.get_recolector_tickets(userId, request.userJWT)

    return make_response(response)


@app.route("/get-ticket", methods=['GET'])
def get_recolector_tickets():
    ticketId = request.args.get('ticketId')

    response = MSSql.get_ticket_information(userId, request.userJWT)

    return make_response(response)


if __name__ == '__main__':
    print ("Running API...")
    app.run(host='0.0.0.0', port=10201, debug=True)