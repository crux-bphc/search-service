from pprint import pprint

import requests
from elasticsearch_setup import COURSE_INDEX, client


def insert_courses():
    courses = requests.get(f"https://www.chrono.crux-bphc.com/api/course").json()
    for course in courses:
        course_id = course["id"]
        print(course_id)
        course_with_sections = requests.get(
            f"https://www.chrono.crux-bphc.com/api/course/{course_id}"
        ).json()
        course_inserted = client.index(index=COURSE_INDEX, body=course_with_sections)
        pprint(course_inserted.body)


if __name__ == "__main__":
    insert_courses()
