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

### Courses

#### Search Course

- **URL**: `/course/search`
- **Method**: `GET`
- **Parameters**:
  - `query` (string): The search query to find courses.
- **Response**:
  - **Success**: `200 OK`
    - **Body**: List of courses matching the search query.

#### Add Course

- **URL**: `/course/add`
- **Method**: `POST`
- **Body**: JSON object containing the course details.
- **Response**:
  - **Success**: `201 Created`
    - **Body**: JSON object containing the course details.

#### Remove Course

- **URL**: `/course/remove`
- **Method**: `DELETE`
- **Body**: JSON object containing the course ID.
- **Response**:
  - **Success**: `204 No Content`

### Timetables

#### Search Timetable

- **URL**: `/timetable/search`
- **Method**: `GET`
- **Parameters**:
  - `query` (string): The search query to find timetables.
- **Response**:
  - **Success**: `200 OK`
    - **Body**: List of timetables matching the search query.

#### Add Timetable

- **URL**: `/timetable/add`
- **Method**: `POST`
- **Body**: JSON object containing the timetable details.
- **Response**:
  - **Success**: `201 Created`
    - **Body**: JSON object containing the timetable details.

#### Remove Timetable

- **URL**: `/timetable/remove`
- **Method**: `DELETE`
- **Body**: JSON object containing the timetable ID.
- **Response**:
  - **Success**: `204 No Content`
