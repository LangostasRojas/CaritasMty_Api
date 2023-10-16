from flask import make_response, request, Blueprint

from app import app, CNX
from app.auth import controllers
from app.middleware.middleware import exclude_middleware
from app.helpers.check_requests import check_parameters

controllers.cnx = CNX

auth_bp = Blueprint('auth', __name__)

@app.route("/sign-in", methods=['POST'])
@exclude_middleware
def sign_in():
    req = request.json
    
    # Checar que se proporcionaron los datos necesarios
    if check_parameters(req.keys(), ['username', 'password']):
        return make_response({'error': 'Bad request'}, 400)
    
    username = req['username']
    password = req['password']

    response = controllers.sign_in(username, password)

    return make_response(response)