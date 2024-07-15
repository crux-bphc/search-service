from course import course
from flask import Flask
from timetable import timetable

app = Flask(__name__)

app.register_blueprint(course, url_prefix="/course")
app.register_blueprint(timetable, url_prefix="/timetable")

if __name__ == "__main__":
    app.run(debug=True)
