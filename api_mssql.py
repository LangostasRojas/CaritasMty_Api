from flask import Flask, make_response, request, jsonify
import json
import sys
import mssql_functions as MSSql

# Connect to mssql dB from start
mssql_params = {}
# mssql_params['DB_HOST'] = '100.80.80.7'
mssql_params['DB_HOST'] = '10.14.255.66'
mssql_params['DB_NAME'] = 'Caritas'
mssql_params['DB_USER'] = 'SA'
mssql_params['DB_PASSWORD'] = 'Shakira123.'

try:
    MSSql.cnx = MSSql.mssql_connect(mssql_params)
except Exception as e:
    print("Cannot connect to mssql server!: {}".format(e))
    sys.exit()

app = Flask(__name__)

@app.route("/hello")
def hello():
    return "Las langostas rojas de Xalapa te saludan de vuelta!\n"

@app.route("/sign-in", methods=['POST'])
def sign_id():
    req = request.json
    username = {'username': req['username']}
    password = {'password': req['password']}

    response = MSSql.sign_in(username, password)

    return make_response(jsonify(response))

if __name__ == '__main__':
    print ("Running API...")
    app.run(host='0.0.0.0', port=10201, debug=True)