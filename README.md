# Open Cosmos

Backend application built for Open Cosmos challenege project.

## Features

- Real-time snapshot ingestion and validation
- In-memory storage for both validated and discarded snapshots
- Exposes HTTP endpoints that returns validated or discarded snapshots
- Optional query parameters such as start/end times and reason for being discarded
- Structred logs

## API

### GET /snapshots

Returns valid satellite snapshots as json with optional start/end time filtering.

**Query Parameters**
`start`: ISO-8601 Format - Filter snapshots with start time - defaults to '0000-01-01T00:00:00' if omitted
`end`: ISO-8601 Format - Filter snapshots with end time - defaults to '9999-12-31T23:59:59' if omitted

**Response**
[
{
"tags":["sun-glint"],
"time":"2026-01-16T16:48:26",
"value":1.0122155
}
]

**Error Responses**
`400`: Invalid parameters, non ISO-8601 time formats or a start time in the future
`500`: Sever errors

### GET /discarded

Returns satellite snapshots that were discarded due to snapshots age being over 1 hour old, or having system/suspect tags. Response returned as json with optional parameters such as reason for being discarded or start/end time.

**Query Parameters**
`start`: ISO-8601 Format - Filter snapshots with start time - defaults to '0000-01-01T00:00:00' if omitted
`end`: ISO-8601 Format - Filter snapshots with end time - defaults to '9999-12-31T23:59:59' if omitted
`reason`: Accepts 'age', 'suspect' or 'system' - Filters based on reason for snapshot being discarded

**Response**
[
{
"reason":"age",
"tags":["sun-glint"],
"time":"2026-01-16T16:48:26",
"value":1.0122155
}
]

**Error Responses**
`400`: Invalid parameters, non ISO-8601 time formats or a start time in the future
`500`: Sever errors
