from flask import Flask, jsonify, request
from storage import snapshot_storage

app = Flask(__name__)

@app.route('/snapshots')
def get_snapshots():
    return jsonify(snapshot_storage)

def start_api():
    app.run(port=8080)