import os
from flask import Flask
from dotenv import load_dotenv

from course import course
from timetable import timetable

load_dotenv()

app = Flask(__name__)

app.config['REFRESH_SETTING'] = os.getenv('REFRESH_SETTING', 'wait_for')

app.register_blueprint(course, url_prefix="/course")
app.register_blueprint(timetable, url_prefix="/timetable")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("CHRONO_PORT"), debug=True)
