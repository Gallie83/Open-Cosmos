# Open Cosmos

Backend application built for Open Cosmos challenge project.

## Features

- Real-time snapshot ingestion and validation
- In-memory storage for both validated and discarded snapshots
- Exposes HTTP endpoints that returns validated or discarded snapshots
- Optional query parameters such as start/end times and reason for being discarded
- Structured logs

## Prerequisites

- Python 3.10 or higher

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

API is on `http://localhost:8080`

### GET /snapshots

Returns valid satellite snapshots as json with optional start/end time filtering.

**Query Parameters**

- `start`: ISO-8601 Format - Filter snapshots with start time - defaults to '0000-01-01T00:00:00' if omitted
- `end`: ISO-8601 Format - Filter snapshots with end time - defaults to '9999-12-31T23:59:59' if omitted

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
- `500`: Sever errors

### GET /discarded

Returns satellite snapshots that were discarded due to snapshots age being over 1 hour old, or having system/suspect tags. Response returned as json with optional parameters such as reason for being discarded or start/end time.

**Query Parameters**

- `start`: ISO-8601 Format - Filter snapshots with start time - defaults to '0000-01-01T00:00:00' if omitted
- `end`: ISO-8601 Format - Filter snapshots with end time - defaults to '9999-12-31T23:59:59' if omitted
- `reason`: Accepts 'age', 'suspect' or 'system' - Filters based on reason for snapshot being discarded

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
- `500`: Sever errors

## Approach and Trade-offs

This backend application was built with simplicity and functionality in mind. I chose to build the API endpoints with Flask as it is an effective lightweight solution for writing REST api's with straight forward setup. I initially considered using dictionaries with timestamps as keys for in-memory storage, but opted for lists to avoid overwriting snapshots with identical timestamps. Snapshot's time values are stored as ISO-8601 as that is the format for query parameter start/end times.

Threading is used in main.py to allow the Flask server to run in the background and accept GET requests while satellite.py polls the mock server, and they can share in-memory storage naturally. Python's built in logging system is used to log valid and discarded snapshots being stored, as well as successful and non-successful api calls.

Validation was a top priority at every step. The responses returned by the mock server are validated for both the age and tags. In the API, validation checks are carried out on the start/end time parameters to check if they exist, are in the correct ISO-8601 format, and to ensure the start date is not a future date. To follow DRY principles I extracted re-occuring validation logic into a helper function get_valid_snapshots().

## Project Architecture

```
Open-Cosmos/
├── main.py # Calls satellite data every second with background API threading
├── satellite.py # Fetches satellite data and sorts into valid and discarded snapshots
├── storage.py # In-memory data storage for valid and discarded snapshots
├── api.py # Flask REST endpoints
└── data-server/ # Mock satellite server
```
