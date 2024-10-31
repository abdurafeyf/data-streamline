import logging
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from auth import get_mongodb_password
import certifi


ca = certifi.where()
logging.basicConfig(filename='fund_data_log.txt',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

uri = f"mongodb+srv://sarmaaya:{get_mongodb_password()}@mongostar.yasmc.mongodb.net/?retryWrites=true&w=majority&appName=mongostar"
client = MongoClient(uri, tlsCAFile=ca)


try:
    client.admin.command('ping')
    logging.info("Pinged your deployment. Successfully connected to MongoDB!")
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {e}")
    exit(1)

# Select the database and collection
db = client['FactSet2']
collection = db['saudiETFs']

# Fetch all documents from the collection
try:
    documents = list(collection.find({}))
    logging.info(f"Fetched {len(documents)} documents from the collection.")
except Exception as e:
    logging.error(f"Error fetching documents: {e}")
    exit(1)

# Convert the documents to a pandas DataFrame
df = pd.DataFrame(documents)

# Save DataFrame to a CSV file locally
output_csv = "saudi_etfs.csv"
try:
    df.to_csv(output_csv, index=False)
    logging.info(f"Data saved to {output_csv} successfully!")
except Exception as e:
    logging.error(f"Error saving to CSV: {e}")
