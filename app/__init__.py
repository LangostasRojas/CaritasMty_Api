from flask import Flask, make_response, request, g
import sys
from app.config.mssql import mssql_connect
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
# Connect to mssql dB from start
mssql_params = {}
mssql_params['DB_HOST'] = os.getenv('DB_HOST')
mssql_params['DB_NAME'] = os.getenv('DB_NAME')
mssql_params['DB_USER'] = os.getenv('DB_USER')
mssql_params['DB_PASSWORD'] = os.getenv('DB_PASSWORD')
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')
REFRESH_TOKEN_KEY = os.getenv('REFRESH_TOKEN_KEY')

try:
    CNX = mssql_connect(mssql_params)
except Exception as e:
    print("Cannot connect to mssql server!: {}".format(e))
    sys.exit()

# Start Flask app
app = Flask(__name__)

# Import blueprints
from app.auth.routes import auth_bp
from app.middleware.middleware import middleware_bp
from app.collector.routes import collector_bp
from app.manager.routes import manager_bp

app.register_blueprint(auth_bp)
app.register_blueprint(middleware_bp)
app.register_blueprint(collector_bp)
app.register_blueprint(manager_bp)