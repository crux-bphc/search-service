# Search Service

Currently being implemented for ChronoFactorem. May be expanded to other projects (Lex?) as well.

Uses Elasticsearch to index and search timetables and courses.

## Setting up Elasticsearch

### Development

```bash
docker run -p 127.0.0.1:9200:9200 -d --name elasticsearch --network elastic-net \
  -e ELASTIC_PASSWORD=$ELASTIC_PASSWORD \
  -e "discovery.type=single-node" \
  -e "xpack.security.http.ssl.enabled=false" \
  -e "xpack.license.self_generated.type=trial" \
  docker.elastic.co/elasticsearch/elasticsearch:8.14.3
```

### Production

[Link to Tutorial](https://www.elastic.co/guide/en/elasticsearch/reference/8.14/docker.html)

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
