import pytest
import os 
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import logging

from api import datetime_valid, set_times

def test_valid_iso_datetime():
    """Tests ISO-8601 validation"""
    assert datetime_valid("2026-01-01T00:00:00") == True
    assert datetime_valid(1712751031) == False
    assert datetime_valid("invalid-iso") == False
    assert datetime_valid(None) == False
    assert datetime_valid("") == False

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