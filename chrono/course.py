from elasticsearch import NotFoundError
from elasticsearch_setup import COURSE_INDEX, client, search_by_id
from flask import Blueprint, jsonify, request, current_app
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
    queries = {
        "query": request.args.get("query", type=str),
        "name": request.args.get("name", type=str),
        "code": request.args.get("code", type=str),
        "dept": request.args.get("dept", type=str),
        "instructors": request.args.getlist("instructor", type=str),
        "time": request.args.getlist("time", type=str),
    }

    if not any(queries.values()):
        return jsonify({"error": "At least one valid query parameter required"}), 400

    bool_must_queries = []

    for key, value in queries.items():
        if not value:
            continue
        if isinstance(value, list):
            value = [v for v in value if v]
            if not value:
                continue
        if key == "query":
            bool_must_queries.append(
                {
                    "bool": {
                        "should": [
                            {
                                "term": {
                                    "code": {
                                        "value": value.upper(),
                                        "boost": 2.0,
                                    }
                                }
                            },
                            {
                                "term": {
                                    "dept": {
                                        "value": value.upper(),
                                        "boost": 2.5,
                                    }
                                }
                            },
                            {
                                "match": {
                                    "name": {
                                        "query": value,
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
                                                "query": value,
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
            )
        elif key == "name":
            bool_must_queries.append(
                {
                    "match": {
                        "name": {
                            "query": value,
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    }
                }
            )
        elif key in ["code", "dept"]:
            bool_must_queries.append(
                {
                    "term": {
                        key: {
                            "value": value.upper(),
                        }
                    }
                }
            )
        elif key == "instructors":
            for instructor in value:
                bool_must_queries.append(
                    {
                        "nested": {
                            "path": "sections",
                            "query": {
                                "match": {
                                    "sections.instructors": {
                                        "query": instructor,
                                        "fuzziness": "AUTO",
                                        "lenient": True,
                                    }
                                }
                            },
                        }
                    }
                )
        elif key == "time":
            bool_must_queries.append(
                {
                    "nested": {
                        "path": "sections",
                        "query": {
                            "terms_set": {
                                "sections.time": {
                                    "terms": value,
                                    "minimum_should_match": len(value),
                                }
                            }
                        },
                    }
                }
            )
    if len(bool_must_queries) == 1:
        elastic_query = bool_must_queries[0]
    else:
        elastic_query = {"bool": {"must": bool_must_queries}}

    res = client.search(
        index=COURSE_INDEX,
        query=elastic_query,
        size=10,
    )
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
        return jsonify({"error": "Invalid course data: " + e.message}), 400

    if search_by_id(COURSE_INDEX, course_data["id"]):
        return jsonify({"error": "Course already exists"}), 400

    course_data["dept"] = course_data["code"].split()[0]

    # Format roomTime to time and only include the last two parts of the string
    for section in course_data["sections"]:
        time = []
        for roomTime in section.pop("roomTime", []):
            time.append(":".join(roomTime.split(":")[-2:]))
        section["time"] = time

    course_data = remove_newline_chars(course_data)
    client.index(index=COURSE_INDEX, body=course_data, refresh=current_app.config['REFRESH_SETTING'])

    return jsonify(course_data), 201


@course.route("/remove", methods=["DELETE"])
def remove_course():
    course_id = request.json.get("id")
    if not course_id or not isinstance(course_id, str):
        return jsonify({"error": "Invalid course id"}), 400

    search_res = search_by_id(COURSE_INDEX, course_id)
    if not search_res:
        return jsonify({"error": "Course not found"}), 404

    try:
        client.delete(index=COURSE_INDEX, id=search_res["_id"], refresh=current_app.config['REFRESH_SETTING'])
    except NotFoundError:
        return jsonify({"error": "Course not found"}), 404

    return jsonify(), 204
