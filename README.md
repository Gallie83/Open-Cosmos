# Open Cosmos

Backend application built for Open Cosmos challenge project.
Aim High Go Beyond!

## Features

- Real-time snapshot ingestion and validation
- Database storage for both validated and discarded snapshots
- Exposes HTTP endpoints that returns validated or discarded snapshots
- Optional query parameters such as start/end times and reason for being discarded
- Structured logs

## Prerequisites

- Python 3.10 or higher
- PostgreSQL
- pgAdmin 4 or command-line access to create database

## Setup

1. Clone the repository

```bash
git clone https://github.com/Gallie83/Open-Cosmos.git
cd Open-Cosmos
```

2. Create virtual environment with

```bash
python -m venv .venv
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Setup database ( See [**Database Setup**](#database-setup) for more details)

## Running Application

1. Run data-server to fetch satellite data

```bash
cd data-server
./data-server --port 28462
```

2. Run application to start parsing and validating satellite data

```bash
python main.py
```

## API

Flask API is on `http://localhost:8080`

### GET /snapshots

Returns valid satellite snapshots as json with optional start/end time filtering.

**Query Parameters**

- `start`: ISO-8601 Format - Filter snapshots with start time - defaults to '0000-01-01T00:00:00' if omitted
- `end`: ISO-8601 Format - Filter snapshots with end time - defaults to '9999-12-31T23:59:59' if omitted

**Example**

```bash
curl "http://localhost:8080/snapshots?start=2026-01-18T14:00:00&end=2026-01-18T15:00:00"
```

**Response**

```json
[
  {
    "tags": ["sun-glint"],
    "time": "2026-01-16T16:48:26",
    "value": 1.0122155
  }
]
```

**Error Responses**

- `400`: Invalid parameters, non ISO-8601 time formats or a start time in the future
- `500`: Server errors

### GET /discarded

Returns satellite snapshots that were discarded due to snapshots age being over 1 hour old, or having system/suspect tags. Response returned as json with optional parameters such as reason for being discarded or start/end time.

**Query Parameters**

- `start`: ISO-8601 Format - Filter snapshots with start time - defaults to '0000-01-01T00:00:00' if omitted
- `end`: ISO-8601 Format - Filter snapshots with end time - defaults to '9999-12-31T23:59:59' if omitted
- `reason`: Accepts 'age', 'suspect' or 'system' - Filters based on reason for snapshot being discarded

**Example Use**

```bash
curl "http://localhost:8080/discarded?start=2026-01-18T14:00:00&end=2026-01-18T15:00:00&reason=age"
```

**Response**

```json
[
  {
    "reason": "age",
    "tags": ["sun-glint"],
    "time": "2026-01-16T16:48:26",
    "value": 1.0122155
  }
]
```

**Error Responses**

- `400`: Invalid parameters, non ISO-8601 time formats or a start time in the future
- `500`: Server errors

## Database

### Database Setup

This application uses PostgreSQL as a database.

1. To set up and connect the database, first create a new database with pgAdmin4 or through the command-line with:

```sql
CREATE DATABASE opencosmos;
```

2. Update your .env file in the root directory with the database information.

```
# .env example
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

3. When the project is run, 2 tables will be initialized in the database following the below schemas.

### Database Schemas

**valid_snapshots**

- `id` (SERIAL PRIMARY KEY)
- `time` (TIMESTAMP) - When the snapshot was captured
- `value` (REAL) - Ground temperature of snapshot in °C
- `tags` (TEXT[]) - List of snapshot tags

**discarded_snapshots**

- `id` (SERIAL PRIMARY KEY)
- `time` (TIMESTAMP) - When the snapshot was captured
- `value` (REAL) - Ground temperature of snapshot in °C
- `tags` (TEXT[]) - List of snapshot tags
- `reason` (TEXT) - Reason snapshot failed validation ('age', 'system', 'suspect')
- `discarded_at` (TIMESTAMP) - The time the snapshot failed validation

## Approach and Trade-offs

This backend application was built with simplicity and functionality in mind. I chose to build the API endpoints with Flask as it is an effective lightweight solution for writing REST api's with straight forward setup. Threading is used in main.py to allow the Flask server to run in the background and accept GET requests while satellite.py polls the mock server. Python's built in logging system is used to log valid and discarded snapshots being stored, as well as successful and non-successful api calls.

Initially I was storing data in-memory but later refactored to include a PostgreSQL database to allow the data to persist server shutdowns. I separated this logic across multiple files: database.py handles database initialization and connection pooling, while storage.py inserts and reads data using those connections.

Validation was a top priority at every step. The responses returned by the mock server are validated for both the age and tags. In the API, validation checks are carried out on the start/end time parameters to check if they exist, are in the correct ISO-8601 format, and to ensure the start date is not a future date. To follow DRY principles I extracted re-occuring validation logic into a helper function set_times().

## Project Architecture

```
Open-Cosmos/
├── main.py      # Calls satellite data every second with background API threading
├── satellite.py # Fetches satellite data and sorts into valid and discarded snapshots
├── database.py  # Database initialization and functions to connect/disconnect from connection pool
├── storage.py   # Takes validated API parameters and uses database.py connection to interact with database
├── api.py       # Flask REST endpoints
└── data-server/ # Mock satellite server
```
