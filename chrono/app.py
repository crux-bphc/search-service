import os
from flask import Flask
from dotenv import load_dotenv

from course import course
from timetable import timetable

load_dotenv()

app = Flask(__name__)

app.register_blueprint(course, url_prefix="/course")
app.register_blueprint(timetable, url_prefix="/timetable")

if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("CHRONO_PORT"))
