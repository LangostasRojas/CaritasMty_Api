from flask import make_response, request, Blueprint
import sys

from app import app, CNX
from app.auth import controllers
from app.middleware.middleware import exclude_middleware

controllers.cnx = CNX
# try:
#     controllers.cnx = controllers.mssql_connect(mssql_params)
#     print("Connected to mssql server!")
# except Exception as e:
#     print("Cannot connect to mssql server!: {}".format(e))
#     sys.exit()

auth_bp = Blueprint('auth', __name__)

@app.route("/sign-in", methods=['POST'])
@exclude_middleware
def sign_in():
    req = request.json
    
    # Checar que se proporcionaron los datos necesarios
    if req['username'] is None or req['password'] is None:
        return make_response({'error': 'Bad request'}, 400)
    
    username = req['username']
    password = req['password']

    response = controllers.sign_in(username, password)

    return make_response(response)