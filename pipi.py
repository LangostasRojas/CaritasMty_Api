import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')

print(ACCESS_TOKEN_KEY)