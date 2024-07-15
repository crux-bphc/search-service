from flask import Blueprint, jsonify, request

course = Blueprint("course", __name__)


@course.route("/search", methods=["GET"])
def search_course():
    search_query = request.args.get("query")
    return jsonify(search_query), 200


@course.route("/add", methods=["POST"])
def add_course():
    course_data = request.json
    return jsonify(course_data), 201


@course.route("/remove", methods=["DELETE"])
def remove_course():
    course_id = request.json.get("id")
    return "", 204
