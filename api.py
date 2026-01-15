from flask import Flask, jsonify, request
from storage import snapshot_storage
from datetime import datetime

app = Flask(__name__)

# Validates ISO format
def datetime_valid(dt_str):
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

@app.route('/snapshots')
def get_snapshots():

    # First validate start and end parameters if they exist
    start_time = request.args.get('start')
    end_time = request.args.get('end')

    if start_time and not datetime_valid(start_time):
        return jsonify({'error:', 'Invalid ISO start format'}), 400
    
    if end_time and not datetime_valid(end_time):
        return jsonify({'error:', 'Invalid ISO end format'}), 400
    
    # Set start and end times or assign extreme values
    start = start_time or '0000-01-01T00:00:00'
    end = end_time or'9999-12-31T23:59:59'

    valid_snapshots = []

    for snap in snapshot_storage:
        if start <= snap['time'] <= end:
            valid_snapshots.append(snap)
            
    return jsonify(valid_snapshots)

def start_api():
    app.run(port=8080)