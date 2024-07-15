from pprint import pprint

import requests
from elasticsearch_setup import COURSE_INDEX, client


def insert_courses():
    courses = requests.get(f"https://www.chrono.crux-bphc.com/api/course").json()
    for course in courses:
        course_id = course["id"]
        print(course_id)
        course = requests.get(
            f"https://www.chrono.crux-bphc.com/api/course/{course_id}"
        ).json()
        course = remove_newline_chars(course)
        course_inserted = client.index(index=COURSE_INDEX, body=course)
        pprint(course_inserted.body)


def remove_newline_chars(object):
    if isinstance(object, dict):
        for key, value in object.items():
            object[key] = remove_newline_chars(value)
    elif isinstance(object, list):
        for index, value in enumerate(object):
            object[index] = remove_newline_chars(value)
    elif isinstance(object, str):
        object = object.replace("\n", " ")
    return object


if __name__ == "__main__":
    insert_courses()
