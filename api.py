from flask import Flask, jsonify, request
from storage import get_valid_snapshots, get_discarded_snapshots
from datetime import datetime
import logging

app = Flask(__name__)

# Validates ISO format
def datetime_valid(dt_str):
    try:
        # Ensure arg is a string
        if not isinstance(dt_str, str):
            return False
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False
    
# Helper function to validate and set both start and end time
# takes ISO-8601 and returns datetime for database querying
def set_times(start_time, end_time):
    if start_time and not datetime_valid(start_time):
        logging.error(f'Invalid ISO start format: {start_time}')
        return jsonify({'error': 'Invalid ISO start format'}), 400
    
    # Ensure start date not in the future
    if start_time and start_time > datetime.now().isoformat():
        logging.error(f'Start value cannot be in the future: {start_time}')
        return jsonify({'error': 'Start value cannot be in the future'}), 400
    
    if end_time and not datetime_valid(end_time):
        logging.error(f'Invalid ISO end format: {end_time}')
        return jsonify({'error': 'Invalid ISO end format'}), 400
    
    # Set start and end times or assign extreme values
    start = (datetime.fromisoformat(start_time) if start_time 
            else datetime.min)
    end = (datetime.fromisoformat(end_time) if end_time 
            else datetime.max)

    if start > end:
        logging.error(f'Start time must be before End time: {start_time}, {end_time}')
        return jsonify({'error': 'Start time must be before End time'}), 400

    logging.debug(f'Start type: {type(start)}, End type: {type(end)}')
    return [start, end]

# GET/ Returns all valid snapshots, optional start and end time parameters
@app.route('/snapshots')
def get_snapshots():
    try:
        # First check start and end parameters, if they exist
        valid_params = {'start', 'end'}
        params = set(request.args.keys())
        unknown_params = params - valid_params

        if unknown_params:
            logging.error(f'Invalid parameters: {unknown_params}')
            return jsonify({'error': "Invalid parameters, only 'start' or 'end' accepted"}), 400

        start_time = request.args.get('start')
        end_time = request.args.get('end')

        # Validate and set start/end times
        times = set_times(start_time, end_time)
        # If times is not a list then return the error message
        if not isinstance(times, list):
            return times
        
        valid_snapshots = get_valid_snapshots(times[0], times[1])
        return jsonify(valid_snapshots)
    
    except Exception as e:
        logging.error(f'Server error: {e}')
        return jsonify({'error': f'Server error: {e}'}), 500

# GET/ Returns all discarded snapshots, optional start/end/reason parameters
@app.route('/discarded')
def get_discarded():
    try:
        # First check parameters are correct, if they exist
        valid_params = {'start', 'end', 'reason'}
        params = set(request.args.keys())
        unknown_params = params - valid_params

        if unknown_params:
            logging.error(f'Invalid parameters: {unknown_params}')
            return jsonify({'error': "Invalid parameters, only 'start', 'end' or 'reason' accepted"}), 400

        start_time = request.args.get('start')
        end_time = request.args.get('end')
        reason = request.args.get('reason')

        if reason and reason not in ['age', 'suspect', 'system']:
            logging.error(f'Invalid reason value: {reason}')
            return jsonify({'error': "Invalid 'reason' value. Only 'age', 'suspect' or 'system' accepted"}), 400
        
        # Validate and set start/end times
        times = set_times(start_time, end_time)

        # If not a list then return the error message
        if not isinstance(times, list):
            return times        
        
        discarded_snapshots = get_discarded_snapshots(times[0], times[1], reason)
        return jsonify(discarded_snapshots)
    
    except Exception as e:
        logging.error(f'Server error: {e}')
        return jsonify({'error': f'Server error: {e}'}), 500
    
def start_api():
    app.run(port=8080, use_reloader=False, threaded=True)