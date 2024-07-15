from elasticsearch_setup import COURSE_INDEX, client
from flask import Blueprint, jsonify, request
from utils import remove_newline_chars

timetable = Blueprint("timetable", __name__)


@timetable.route("/search", methods=["GET"])
def search_timetable():
    search_query = request.args.get("query")
    return jsonify(search_query), 200


@timetable.route("/add", methods=["POST"])
def add_timetable():
    timetable_data = request.json

    # Add course information to timetable_data
    timetable_data["courses"] = []
    course_ids = {section["courseId"] for section in timetable_data["sections"]}
    for course_id in course_ids:
        course = client.search(
            index=COURSE_INDEX,
            body={"query": {"term": {"id": course_id}}},
            size=1,
        )["hits"]["hits"][0]["_source"]
        timetable_data["courses"].append(
            {
                "code": course["code"],
                "name": course["name"],
            }
        )

    timetable_data = remove_newline_chars(timetable_data)
    return jsonify(timetable_data), 201


@timetable.route("/remove", methods=["DELETE"])
def remove_timetable():
    timetable_id = request.json.get("id")
    return "", 204
