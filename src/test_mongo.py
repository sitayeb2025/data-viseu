from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))


try:
    client.admin.command("ping")
    print("Connexion a MongoDB reussie")
except Exception as e:
    print("Erreur de connexion: ",e )    