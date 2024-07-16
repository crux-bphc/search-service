# Search Service

Currently being implemented for ChronoFactorem. May be expanded to other projects (Lex?) as well.

Uses Elasticsearch to index and search timetables and courses.

## Setup

### Development

It uses a Docker build system with an Elasticsearch container and a container for the Flask backend that will be called by ChronoFactorem.

```
docker compose up --build -d
```

`elasticsearch_setup.py` creates indices for courses and timetables and `app.py` starts the Flask server.

Courses and timetables can be added to the index using the API endpoints. A simple script to add all courses through these endpoints is in `utils.py`, which should be run locally.

### Production

TODO: [Run Elasticsearch in Docker](https://www.elastic.co/guide/en/elasticsearch/reference/8.14/docker.html)

## API Endpoints

| **Endpoint**     | **URL**             | **Method** | **Parameters**                 | **Request Body**                             | **Response**                                              |
| ---------------- | ------------------- | ---------- | ------------------------------ | -------------------------------------------- | --------------------------------------------------------- |
| **Courses**      |                     |            |                                |                                              |                                                           |
| Search Course    | `/course/search`    | `GET`      | `query` (string): Search query |                                              | **200 OK**: List of courses matching the query            |
| Add Course       | `/course/add`       | `POST`     |                                | JSON object containing the course details    | **201 Created**: JSON object containing course details    |
| Remove Course    | `/course/remove`    | `DELETE`   |                                | JSON object containing the course ID         | **204 No Content**                                        |
| **Timetables**   |                     |            |                                |                                              |                                                           |
| Search Timetable | `/timetable/search` | `GET`      | `query` (string): Search query |                                              | **200 OK**: List of timetables matching the query         |
| Add Timetable    | `/timetable/add`    | `POST`     |                                | JSON object containing the timetable details | **201 Created**: JSON object containing timetable details |
| Remove Timetable | `/timetable/remove` | `DELETE`   |                                | JSON object containing the timetable ID      | **204 No Content**                                        |
