from flask import Blueprint, jsonify, request

timetable = Blueprint("timetable", __name__)


@timetable.route("/search", methods=["GET"])
def search_timetable():
    search_query = request.args.get("query")
    return jsonify(search_query), 200


@timetable.route("/add", methods=["POST"])
def add_timetable():
    timetable_data = request.json
    return jsonify(timetable_data), 201


@timetable.route("/remove", methods=["DELETE"])
def remove_timetable():
    timetable_id = request.json.get("id")
    return "", 204
