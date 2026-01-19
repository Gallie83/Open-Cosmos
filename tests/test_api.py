import pytest
import os 
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime

from api import datetime_valid, set_times, app

@pytest.fixture
# Mock Flask server
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# datetime_valid test
def test_valid_iso_datetime():
    """Tests ISO-8601 validation"""
    assert datetime_valid("2026-01-01T00:00:00") == True
    assert datetime_valid(1712751031) == False
    assert datetime_valid("invalid-iso") == False
    assert datetime_valid(None) == False
    assert datetime_valid("") == False

# set_times test
def test_valid_set_times():
    """Test valid inputs for start/end times"""

    assert set_times("2026-01-01T00:00:00", "2026-01-01T01:00:00") == [
        datetime.fromisoformat("2026-01-01T00:00:00"), 
        datetime.fromisoformat("2026-01-01T01:00:00")
        ]
    
    # No start time
    assert set_times("", "2026-01-01T01:00:00") == [
    datetime.min, 
    datetime.fromisoformat("2026-01-01T01:00:00")
    ]

    # No end time
    assert set_times("2026-01-01T00:00:00", "") == [
    datetime.fromisoformat("2026-01-01T00:00:00"), 
    datetime.max
    ]
    
    # Empty strings are set to default values 
    assert set_times("", "") == [datetime.min, datetime.max]

# GET /snapshots tests
def test_valid_snapshots_request(mocker, client):
    """Test that valid requests return query list"""
    
    # Mock the database query
    mocker.patch('api.get_valid_snapshots', return_value=[{
        "time": "2026-01-01T01:30:00",
        "value": 12.37,
        "tags": ["night"]
    }])
    
    response = client.get('/snapshots?start=2026-01-01T01:00:00&end=2026-01-01T02:00:00')
    
    # Check response
    assert response.status_code == 200
    
    # Get JSON data
    data = response.get_json()
    
    # Check structure
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["time"] == "2026-01-01T01:30:00"
    assert data[0]["value"] == 12.37
    assert data[0]["tags"] == ["night"]

def test_invalid_start_time(client, caplog):
    """Test that invalid start time returns 400 error"""
    response = client.get('/snapshots?start=invalid&end=2026-01-01T01:00:00')
    
    # Check response and log are correct
    assert response.status_code == 400
    assert 'Invalid ISO start format' in caplog.text
    assert b'Invalid ISO start format' in response.data

def test_invalid_end_time(client, caplog):
    """Test that invalid start time returns 400 error"""
    response = client.get('/snapshots?start=2026-01-01T01:00:00&end=invalid')

    # Check response and log are correct
    assert response.status_code == 400
    assert 'Invalid ISO end format' in caplog.text
    assert b'Invalid ISO end format' in response.data

def test_end_time_before_start_time(client, caplog):
    """Test that end time before start time returns error"""
    
    response = client.get('/snapshots?start=2026-01-01T01:00:00&end=2025-01-01T01:00:00')

    # Check response and log are correct
    assert response.status_code == 400
    assert 'Start time must be before End time:' in caplog.text
    assert b'Start time must be before End time' in response.data

def test_start_time_is_in_future(client, caplog):
    """Test start date being in the future returns error"""
    
    response = client.get('/snapshots?start=2027-01-01T01:00:00')

    # Check response and log are correct
    assert response.status_code == 400
    assert 'Start value cannot be in the future:' in caplog.text
    assert b'Start value cannot be in the future' in response.data

# GET /discarded_snapshots tests
def test_discarded_snapshots_request(mocker, client):
    """Test that valid requests for discarded snapshots return query list"""
    
    # Mock the database query
    mocker.patch('api.get_discarded_snapshots', return_value=[{
        "time": "2026-01-01T01:00:00",
        "value": 12.37,
        "tags": ["night"],
        "reason": "age",
        "discarded_at": "2026-01-01T02:30:00"
    }])
    
    response = client.get('/discarded?start=2026-01-01T01:00:00&end=2026-01-01T02:00:00')
    
    # Check response
    assert response.status_code == 200
    
    # Get JSON data
    data = response.get_json()
    
    # Check structure
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["time"] == "2026-01-01T01:00:00"
    assert data[0]["value"] == 12.37
    assert data[0]["tags"] == ["night"]
    assert data[0]["reason"] == "age"
    assert data[0]["discarded_at"] == "2026-01-01T02:30:00"

def test_invalid_reason_parameter(client, caplog):
    """Test that invalid reason parameters return 400 errors"""
    response = client.get('/discarded?reason=invalid')
    
    # Check response and log are correct
    assert response.status_code == 400
    assert 'Invalid reason value:' in caplog.text
    assert b"Invalid 'reason' value. Only 'age', 'suspect' or 'system' accepted" in response.data