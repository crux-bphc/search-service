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
    start = request.args.get("from", type=int)
    if start == None:
        start = 0

    queries = {
        "query": request.args.get("query", type=str),
        "year": request.args.get("year", type=int),
        "name": request.args.get("name", type=str),
        "authorId": request.args.get("authorId", type=str),
        "acadYear": request.args.get("acadYear", type=int),
        "semester": request.args.get("semester", type=int),
        "degrees": [code.upper() for code in request.args.getlist("degree", type=str)],
        "courses": request.args.getlist("course", type=str),
        "instructors": request.args.getlist("instructor", type=str),
    }

    # if not any(queries.values()):
    #     return jsonify({"error": "At least one valid query parameter required"}), 400

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
                                                        for code in value.split()
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
                                                    "terms": value.upper().split(),
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
                                                        for s in value.split()
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
                                                    "term": {
                                                        "courses.code": {
                                                            "value": value.upper(),
                                                            "boost": 2.0,
                                                        }
                                                    }
                                                },
                                                {
                                                    "match": {
                                                        "courses.name": {
                                                            "query": value,
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
                                                "query": value,
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
                                        "query": value,
                                        "fuzziness": "AUTO",
                                        "lenient": True,
                                    }
                                }
                            },
                            {  # Author ID
                                "term": {
                                    "authorId": {
                                        "value": value.lower(),
                                        "boost": 2.0,
                                    }
                                },
                            },
                        ],
                        "tie_breaker": 0.7,
                    }
                }
            )
        elif key == "degrees":
            bool_must_queries.append(
                {
                    "terms_set": {
                        "degrees": {
                            "terms": value,
                            "minimum_should_match": len(value),
                        }
                    }
                }
            )
        elif key == "courses":
            for course in value:
                bool_must_queries.append(
                    {
                        "nested": {
                            "path": "courses",
                            "query": {
                                "bool": {
                                    "should": [
                                        {
                                            "term": {
                                                "courses.code": {
                                                    "value": course.upper(),
                                                    "boost": 2.0,
                                                }
                                            }
                                        },
                                        {
                                            "match": {
                                                "courses.name": {
                                                    "query": course,
                                                    "fuzziness": "AUTO",
                                                    "lenient": True,
                                                }
                                            }
                                        },
                                    ],
                                }
                            },
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
        elif key == "name":
            bool_must_queries.append(
                {
                    "match": {
                        key: {
                            "query": value,
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    }
                }
            )
        elif key in [
            "year",
            "acadYear",
            "semester",
            "authorId",
        ]:
            if key == "authorId":
                value = value.lower()
            bool_must_queries.append(
                {
                    "term": {
                        key: {
                            "value": value,
                        }
                    }
                }
            )

    if len(bool_must_queries) == 0:
        elastic_query = {"match_all": {}}
    elif len(bool_must_queries) == 1:
        elastic_query = bool_must_queries[0]
    else:
        elastic_query = {"bool": {"must": bool_must_queries}}

    res = client.search(
        index=TIMETABLE_INDEX,
        query=elastic_query,
        from_=start,
        size=10,
    )
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
        course = search_by_id(COURSE_INDEX, course_id)
        if not course:
            return jsonify({"error": f"Course with id {course_id} not found"}), 404
        course = course["_source"]
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
