import os
from pprint import pprint

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

username = os.getenv("ELASTIC_USERNAME")
password = os.getenv("ELASTIC_PASSWORD")

client = Elasticsearch(
    "http://localhost:9200",
    basic_auth=(username, password),
)

COURSE_INDEX = "courses"
TIMETABLE_INDEX = "timetables"


def create_course_index():
    body = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "code": {"type": "keyword"},
                "name": {"type": "search_as_you_type"},
                "sections": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "keyword"},
                        "courseId": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "number": {"type": "integer"},
                        "instructors": {"type": "search_as_you_type"},
                        "roomTime": {"type": "text"},
                        "createdAt": {"type": "date"},
                    },
                },
                "midsemStartTime": {"type": "date"},
                "midsemEndTime": {"type": "date"},
                "compreStartTime": {"type": "date"},
                "compreEndTime": {"type": "date"},
                "archived": {"type": "boolean"},
                "acadYear": {"type": "integer"},
                "semester": {"type": "integer"},
                "createdAt": {"type": "date"},
            }
        },
    }

    if not client.indices.exists(index=COURSE_INDEX):
        client.indices.create(index=COURSE_INDEX, body=body)
    else:
        print(f"Index `{COURSE_INDEX}` already exists")


def create_timetable_index():
    body = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "authorId": {"type": "keyword"},
                "name": {"type": "text"},
                "degrees": {"type": "keyword"},
                "private": {"type": "boolean"},
                "draft": {"type": "boolean"},
                "archived": {"type": "boolean"},
                "year": {"type": "integer"},
                "acadYear": {"type": "integer"},
                "semester": {"type": "integer"},
                "sections": {
                    "type": "nested",
                    "properties": {
                        "id": {"type": "keyword"},
                        "courseId": {"type": "keyword"},
                        "type": {"type": "keyword"},
                        "number": {"type": "integer"},
                        "instructors": {"type": "search_as_you_type"},
                        "roomTime": {"type": "text"},
                        "createdAt": {"type": "date"},
                    },
                },
                "timings": {"type": "text"},
                "examTimes": {"type": "text"},
                "warnings": {"type": "text"},
                "createdAt": {"type": "date"},
                "lastUpdated": {"type": "date"},
                "courses": {  # Added by search service when a timetable is added
                    "type": "nested",
                    "properties": {
                        "code": {"type": "keyword"},
                        "name": {"type": "search_as_you_type"},
                    },
                },
            },
        }
    }

    if not client.indices.exists(index=TIMETABLE_INDEX):
        client.indices.create(index=TIMETABLE_INDEX, body=body)
    else:
        print(f"Index `{TIMETABLE_INDEX}` already exists")


def delete_index(index_name):
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)
    else:
        print(f"Index `{index_name}` does not exist")


if __name__ == "__main__":
    pprint(client.info().body)
    create_course_index()
    create_timetable_index()
    # delete_index(COURSE_INDEX)
    # delete_index(TIMETABLE_INDEX)
