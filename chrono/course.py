from elasticsearch_setup import COURSE_INDEX, client, search_by_id
from flask import Blueprint, jsonify, request
from jsonschema import ValidationError, validate
from utils import remove_newline_chars

course = Blueprint("course", __name__)

course_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "code": {"type": "string"},
        "name": {"type": "string"},
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
        "midsemStartTime": {"type": ["string", "null"], "format": "date-time"},
        "midsemEndTime": {"type": ["string", "null"], "format": "date-time"},
        "compreStartTime": {"type": ["string", "null"], "format": "date-time"},
        "compreEndTime": {"type": ["string", "null"], "format": "date-time"},
        "archived": {"type": "boolean"},
        "acadYear": {"type": "integer"},
        "semester": {"type": "integer"},
        "createdAt": {"type": "string", "format": "date-time"},
    },
    "required": [
        "id",
        "code",
        "name",
        "sections",
        "midsemStartTime",
        "midsemEndTime",
        "compreStartTime",
        "compreEndTime",
        "archived",
        "acadYear",
        "semester",
        "createdAt",
    ],
    "additionalProperties": False,
}


@course.route("/search", methods=["GET"])
def search_course():
    search_query = request.args.get("query")
    if not search_query or not isinstance(search_query, str):
        return jsonify({"error": "Invalid search query"}), 400

    query = {
        "bool": {
            "should": [
                {
                    "match": {
                        "code": {
                            "query": search_query,
                            "fuzziness": "AUTO",
                            "boost": 2.0,
                            "lenient": True,
                        }
                    }
                },
                {
                    "match": {
                        "name": {
                            "query": search_query,
                            "fuzziness": "AUTO",
                            "boost": 2.0,
                            "lenient": True,
                        }
                    }
                },
                {
                    "nested": {
                        "path": "sections",
                        "query": {
                            "match": {
                                "sections.instructors": {
                                    "query": search_query,
                                    "fuzziness": "AUTO",
                                    "lenient": True,
                                }
                            }
                        },
                    }
                },
            ]
        }
    }

    res = client.search(index=COURSE_INDEX, query=query)
    search_results = []
    for hit in res["hits"].get("hits", []):
        search_results.append({"course": hit["_source"], "score": hit["_score"]})

    return jsonify(search_results), 200


@course.route("/add", methods=["POST"])
def add_course():
    course_data = request.json
    try:
        validate(instance=course_data, schema=course_schema)
    except ValidationError as e:
        return jsonify({"error": "Invalid course data", "message": e.message}), 400

    if search_by_id(COURSE_INDEX, course_data["id"]):
        return jsonify({"error": "Course already exists"}), 400

    course_data = remove_newline_chars(course_data)
    client.index(index=COURSE_INDEX, body=course_data, refresh="wait_for")

    return jsonify(course_data), 201


@course.route("/remove", methods=["DELETE"])
def remove_course():
    course_id = request.json.get("id")
    if not course_id or not isinstance(course_id, str):
        return jsonify({"error": "Invalid course id"}), 400

    search_res = search_by_id(COURSE_INDEX, course_id)
    if not search_res:
        return jsonify({"error": "Course not found"}), 404

    client.delete(index=COURSE_INDEX, id=search_res["_id"], refresh="wait_for")

    return "", 204
