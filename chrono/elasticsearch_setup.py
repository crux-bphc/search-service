import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

username = os.getenv("ELASTIC_USERNAME")
password = os.getenv("ELASTIC_PASSWORD")

client = Elasticsearch(
    "http://localhost:9200",
    basic_auth=(username, password),
)
print(client.info())
