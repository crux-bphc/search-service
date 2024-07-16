from elasticsearch_setup import COURSE_INDEX, TIMETABLE_INDEX, client, search_by_id
from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate
from utils import remove_newline_chars

timetable = Blueprint("timetable", __name__)

timetable_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "authorId": {"type": "string"},
        "name": {"type": "string"},
        "degrees": {"type": "array", "items": {"type": "string"}},
        "private": {"type": "boolean"},
        "draft": {"type": "boolean"},
        "archived": {"type": "boolean"},
        "year": {"type": "integer"},
        "acadYear": {"type": "integer"},
        "semester": {"type": "integer"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "courseId": {"type": "string"},
                    "type": {"type": "string"},
                    "number": {"type": "integer"},
                    "instructors": {"type": "array", "items": {"type": "string"}},
                    "roomTime": {"type": "array", "items": {"type": "string"}},
                    "createdAt": {"type": "string", "format": "date-time"},
                },
                "required": [
                    "id",
                    "courseId",
                    "type",
                    "number",
                    "instructors",
                    "roomTime",
                    "createdAt",
                ],
                "additionalProperties": False,
            },
        },
        "timings": {"type": "array", "items": {"type": "string"}},
        "examTimes": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}},
        "createdAt": {"type": "string", "format": "date-time"},
        "lastUpdated": {"type": "string", "format": "date-time"},
    },
    "required": [
        "id",
        "authorId",
        "name",
        "degrees",
        "private",
        "draft",
        "archived",
        "year",
        "acadYear",
        "semester",
        "sections",
        "timings",
        "examTimes",
        "warnings",
        "createdAt",
        "lastUpdated",
    ],
    "additionalProperties": False,
}


@timetable.route("/search", methods=["GET"])
def search_timetable():
    search_query = request.args.get("query")
    return jsonify(search_query), 200


@timetable.route("/add", methods=["POST"])
def add_timetable():
    timetable_data = request.json
    try:
        validate(instance=timetable_data, schema=timetable_schema)
    except ValidationError as e:
        return jsonify({"error": "Invalid timetable data", "message": e.message}), 400

    if search_by_id(TIMETABLE_INDEX, timetable_data["id"]):
        return jsonify({"error": "Timetable already exists"}), 400

    # Add course information to timetable_data
    timetable_data["courses"] = []
    course_ids = {section["courseId"] for section in timetable_data["sections"]}
    for course_id in course_ids:
        course = search_by_id(COURSE_INDEX, course_id)["_source"]
        timetable_data["courses"].append(
            {
                "code": course["code"],
                "name": course["name"],
            }
        )

    timetable_data = remove_newline_chars(timetable_data)
    client.index(index=TIMETABLE_INDEX, body=timetable_data)

    return jsonify(timetable_data), 201


@timetable.route("/remove", methods=["DELETE"])
def remove_timetable():
    timetable_id = request.json.get("id")
    if not timetable_id or not isinstance(timetable_id, str):
        return jsonify({"error": "Invalid timetable id"}), 400

    search_res = search_by_id(TIMETABLE_INDEX, timetable_id)
    if not search_res:
        return jsonify({"error": "Timetable not found"}), 404

    client.delete(index=TIMETABLE_INDEX, id=search_res["_id"])

    return "", 204
