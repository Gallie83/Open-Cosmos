import pytest
import os 
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import logging

from satellite import get_snapshots

def test_valid_snapshots_are_logged(mocker, caplog):
    """Test snapshots passing validation are logged as valid"""

    # Ensure all log level are being monitored
    caplog.set_level(logging.DEBUG)

    # Mock get request
    mock_get = mocker.patch("satellite.requests.get")

    # Set return values
    mock_get.return_value.status_code = 200
    time_now = time.time()
    mock_get.return_value.json.return_value = {
        "time": time_now,
        "value": 12.37,
        "tags": ["night"]
    }

    # Mock database so it doesnt actually store snapshot
    mocker.patch("satellite.add_valid_snapshot")

    get_snapshots()
    print("CAPLOG!:",caplog.text)
    # Check expected log appears
    assert "Valid " in caplog.text

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

def test_404_response_from_request(mocker, caplog):
    """Testing log for 404 response from the data server"""
    # Ensure all log level are being monitored
    caplog.set_level(logging.DEBUG)

    # Mock get request
    mock_get = mocker.patch("satellite.requests.get")

    # Set return values
    mock_get.return_value.status_code = 404

    get_snapshots()

    # Check expected log appears
    assert "No data currently available from satellite: 404" in caplog.text

def test_non_200_response_from_request(mocker, caplog):
    """Testing log for non-200 level response from the data server"""
    # Ensure all log level are being monitored
    caplog.set_level(logging.DEBUG)

    # Mock get request
    mock_get = mocker.patch("satellite.requests.get")

    # Set return values
    mock_get.return_value.status_code = 500

    get_snapshots()

    # Check expected log appears
    assert "Unexpected status code: 500" in caplog.text