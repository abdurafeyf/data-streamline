import requests
from dotenv import load_dotenv
import os
import warnings


warnings.filterwarnings("ignore")

load_dotenv()
authkey = os.getenv('MORNGINGSTAR_AUTHORIZATION')

def get_access_token():
  url = "https://www.emea-api.morningstar.com/token/oauth"

  payload = {}
  headers = {
    'Authorization': f'Basic {authkey}'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  return response.json()['access_token']

def get_mongodb_password(clustername="mongostar"):
  if clustername == "mongostar":
    return os.getenv('MONGODB_PASSWORD_MORNINGSTAR')