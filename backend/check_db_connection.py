import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

# Load env variables
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

# uri = os.getenv("MONGO_URI")
# Configuring manual URI based on nslookup results to bypass Python DNS/SRV issues
uri = "mongodb://rag_db_admin:rag_admin@ac-qaxgbvj-shard-00-00.v3a8tsj.mongodb.net:27017,ac-qaxgbvj-shard-00-01.v3a8tsj.mongodb.net:27017,ac-qaxgbvj-shard-00-02.v3a8tsj.mongodb.net:27017/?ssl=true&authSource=admin&retryWrites=true&w=majority"
print(f"Testing connection to: {uri}")

if not uri:
    print("ERROR: MONGO_URI not found in .env")
    sys.exit(1)

try:
    # Try connecting with short timeout
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # Trigger a server check
    info = client.server_info()
    print("SUCCESS: Connected to MongoDB successfully!")
    print(f"Server version: {info.get('version')}")
except ConfigurationError as ce:
    print(f"\nCONFIGURATION ERROR (DNS/URI Issue): {ce}")
    print("\nPossible causes:")
    print("1. The URI is incorrect (check for typos in 'rag-impli-cluster.v3a8tsj.mongodb.net').")
    print("2. Your network/firewall is blocking DNS resolution for MongoDB Atlas.")
    print("3. You are using a VPN that doesn't resolve external SRV records.")
except ConnectionFailure as cf:
    print(f"\nCONNECTION FAILURE (Network/IP Issue): {cf}")
    print("\nPossible causes:")
    print("1. Your IP address is not whitelisted in MongoDB Atlas.")
    print("2. Internet connection is unstable.")
except Exception as e:
    print(f"\nUNEXPECTED ERROR: {e}")
