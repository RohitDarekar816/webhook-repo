from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("MONGO_URL")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
mydb = client["github-webhook"]
mycol = mydb["webhook"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

for x in mycol.find():

    print(x)

