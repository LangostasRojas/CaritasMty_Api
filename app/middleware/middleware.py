from flask import request, make_response, g, Blueprint, jsonify
from flask_wtf.csrf import generate_csrf
import jwt
import time

from app import app, CNX, ACCESS_TOKEN_KEY
from app.middleware import controllers

controllers.cnx = CNX

middleware_bp = Blueprint('middleware', __name__)

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

    controllers.log_request(ip_address, user_agent, method, path, response_code, jwt)
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
    

@app.after_request
def add_header(r):
    import secure
    secure_headers = secure.Secure()
    secure_headers.framework.flask(r)
    #r.headers['X-Frame-Options'] = 'SAMEORIGIN' # ya lo llena 'secure'
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Content-Security-Policy"] = "default-src 'none'"
    r.headers['X-Content-Type-Options'] = "nosniff"
    return r

# @app.before_request
# def apply_csrf_to_get_requests():
#     csrf.protect()

@exclude_middleware
@app.route("/get-csrf-token", methods=['GET'])
def get_csrf_token():
    return make_response(jsonify(generate_csrf()))