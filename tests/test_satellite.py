import pytest
import os 
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time

from satellite import get_snapshots

def test_old_snapshots_are_logged(mocker, caplog):
    """Test old snapshots are logged as discarded"""
    # Mock get request
    mock_get = mocker.patch("satellite.requests.get")

    # Set return values
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "time": 1712751031,
        "value": 12.37,
        "tags": ["night"]
    }

    # Mock database so it doesnt actually store snapshot
    mocker.patch("satellite.add_discarded_snapshot")

    get_snapshots()

    # Check expected log appears
    assert "Snapshot over 1hr old" in caplog.text

def test_suspect_snapshots_are_logged(mocker, caplog):
    """Test snapshots with suspect tag are logged as discarded"""
    # Mock get request
    mock_get = mocker.patch("satellite.requests.get")

    # Set return values
    mock_get.return_value.status_code = 200
    time_now = time.time()
    mock_get.return_value.json.return_value = {
        "time": time_now,
        "value": 12.37,
        "tags": ["suspect"]
    }

    # Mock database so it doesnt actually store snapshot
    mocker.patch("satellite.add_discarded_snapshot")

    get_snapshots()
    
    # Check expected log appears
    assert "Invalid suspect tag:" in caplog.text

def test_system_snapshots_are_logged(mocker, caplog):
    """Test snapshots with system tag are logged as discarded"""
    # Mock get request
    mock_get = mocker.patch("satellite.requests.get")

    # Set return values
    mock_get.return_value.status_code = 200
    time_now = time.time()
    mock_get.return_value.json.return_value = {
        "time": time_now,
        "value": 12.37,
        "tags": ["system"]
    }

    # Mock database so it doesnt actually store snapshot
    mocker.patch("satellite.add_discarded_snapshot")

    get_snapshots()
    
    # Check expected log appears
    assert "Invalid system tag:" in caplog.text