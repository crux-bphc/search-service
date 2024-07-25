FROM python:3.12.4

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY chrono/ chrono/
COPY .env .env

CMD python3 chrono/elasticsearch_setup.py && python3 chrono/app.py
