from elasticsearch import NotFoundError
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
    if not search_query or not isinstance(search_query, str):
        return jsonify({"error": "Invalid search query"}), 400

    query = {
        "dis_max": {
            "queries": [
                {  # Degrees and Year
                    "bool": {
                        "should": [
                            {
                                "terms_set": {
                                    "degrees": {
                                        "terms": [
                                            code[i : i + 2].upper()
                                            for code in search_query.split()
                                            if len(code) == 4
                                            for i in range(0, 4, 2)
                                        ],
                                        "boost": 2.0,
                                        "minimum_should_match": 1,
                                    }
                                }
                            },
                            {
                                "terms_set": {
                                    "degrees": {
                                        "terms": search_query.upper().split(),
                                        "boost": 1.0,
                                        "minimum_should_match": 1,
                                    }
                                }
                            },
                            {
                                "terms_set": {
                                    "year": {
                                        "terms": [
                                            int(s)
                                            for s in search_query.split()
                                            if s.isdigit()
                                        ],
                                        "boost": 4.0,
                                        "minimum_should_match": 1,
                                    }
                                }
                            },
                        ],
                        "boost": 1.5,
                    }
                },
                {  # Courses
                    "nested": {
                        "path": "courses",
                        "query": {
                            "bool": {
                                "should": [
                                    {
                                        "match": {
                                            "courses.code": {
                                                "query": search_query,
                                                "fuzziness": "AUTO",
                                                "boost": 2.0,
                                                "lenient": True,
                                            }
                                        }
                                    },
                                    {
                                        "match": {
                                            "courses.name": {
                                                "query": search_query,
                                                "fuzziness": "AUTO",
                                                "boost": 2.0,
                                                "lenient": True,
                                            }
                                        }
                                    },
                                ],
                                "boost": 2.0,
                            }
                        },
                    }
                },
                {  # Instructors
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
                        "boost": 1.5,
                    }
                },
                {  # TimeTable Name
                    "match": {
                        "name": {
                            "query": search_query,
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    }
                },
            ],
            "tie_breaker": 0.7,
        }
    }
    res = client.search(index=TIMETABLE_INDEX, query=query)
    search_results = []
    for hit in res["hits"].get("hits", []):
        search_results.append({"timetable": hit["_source"], "score": hit["_score"]})
    return jsonify(search_results), 200


@timetable.route("/add", methods=["POST"])
def add_timetable():
    timetable_data = request.json
    try:
        validate(instance=timetable_data, schema=timetable_schema)
    except ValidationError as e:
        return jsonify({"error": "Invalid timetable data: " + e.message}), 400

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
    client.index(index=TIMETABLE_INDEX, body=timetable_data, refresh="wait_for")

    return jsonify(timetable_data), 201


@timetable.route("/remove", methods=["DELETE"])
def remove_timetable():
    timetable_id = request.json.get("id")
    if not timetable_id or not isinstance(timetable_id, str):
        return jsonify({"error": "Invalid timetable id"}), 400

    search_res = search_by_id(TIMETABLE_INDEX, timetable_id)
    if not search_res:
        return jsonify({"error": "Timetable not found"}), 404

    try:
        client.delete(index=TIMETABLE_INDEX, id=search_res["_id"], refresh="wait_for")
    except NotFoundError:
        return jsonify({"error": "Timetable not found"}), 404

    return jsonify(), 204
