FROM python:3.12.4

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY chrono/ chrono/
COPY .env .env

WORKDIR /app/chrono
CMD python3 elasticsearch_setup.py && python3 app.py
