# API de Caritas

Esta es una API construida con Flask que se conecta a una base de datos SQL Server.

## Requisitos

- Python 3.x
- Paquetes Python: Flask, python-dotenv, pyjwt, pymssql, bcrypt

## Configuración

1. Clona o descarga el repositorio.

2. Instala las dependencias usando pip:

```bash
pip install flask
pip install python-dotenv
pip install pyjwt
pip install pymssql
pip install bcrypt
```


3. Configura la conexión a la base de datos en el archivo `.env`. Reemplaza los valores con tus  datos
```env
DB_HOST=SERVER
DB_NAME=DB_NAME
DB_USER=DB_USER
DB_PASSWORD=DB_PASSWORD
ACCESS_TOKEN_KEY=ACCESS_TOKEN_KEY
REFRESH_TOKEN_KEY=REFRESH_TOKEN_KEY
```

## Ejecución

Para iniciar la API, ejecuta el siguiente comando:

```bash
python api_mssql.py
```

