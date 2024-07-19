from pprint import pprint

import requests


def insert_courses():
    courses = requests.get(f"https://www.chrono.crux-bphc.com/api/course").json()
    for course in courses:
        course_id = course["id"]
        print(course_id)
        course = requests.get(
            f"https://www.chrono.crux-bphc.com/api/course/{course_id}"
        ).json()
        res = requests.post(f"http://localhost:5000/course/add", json=course)
        pprint(res.json())


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
