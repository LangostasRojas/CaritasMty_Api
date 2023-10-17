from flask import Flask, make_response, request, g
from flask_wtf.csrf import CSRFProtect
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
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
TIMEOUT = 10 # Timeout for requests to external APIs

try:
    CNX = mssql_connect(mssql_params)
except Exception as e:
    print("Cannot connect to mssql server!: {}".format(e))
    sys.exit()

# Remove 'Server' from header
from gunicorn.http import wsgi
class Response(wsgi.Response):
    def default_headers(self, *args, **kwargs):
        headers = super(Response, self).default_headers(*args, **kwargs)
        return [h for h in headers if not h.startswith('Server:')]
wsgi.Response = Response


# Start Flask app
app = Flask(__name__)
# csrf = CSRFProtect()
# csrf.init_app(app)

# Import blueprints
from app.auth.routes import auth_bp
from app.middleware.middleware import middleware_bp
from app.collector.routes import collector_bp
from app.manager.routes import manager_bp

app.register_blueprint(auth_bp)
app.register_blueprint(middleware_bp)
app.register_blueprint(collector_bp)
app.register_blueprint(manager_bp)


# Añadir CSRF token a todas las respuestas
app.secret_key = SECRET_KEY
app.config['WTF_CSRF_TIME_LIMIT'] = 600 # Expiracion de 10 minutos