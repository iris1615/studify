from dotenv import load_dotenv
import os

load_dotenv() # vai dar load das variáveis de ambiente do arquivo .env

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")