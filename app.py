import flask
from flask import Flask, request, render_template, redirect, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global list to store recent reports (in-memory solution)
csp_reports = []
button_events = {}


@app.route("/report", methods=["POST"])
def handle_csp_report():
    try:
        # Parse the incoming report, regardless of content type
        report_data = request.get_json(force=True)

        # Store the full report as-is
        csp_reports.append(report_data)

        # Emit the new report via WebSocket to connected clients
        socketio.emit("new_report", report_data)

        return "", 204  # Always return 204 No Content

    except Exception as e:
        # Log the error if parsing fails
        print(f"Error processing report: {str(e)}")
        return "", 204  # Still return 204 even if parsing fails


@app.route("/show")
def show_reports():
    return render_template("reports.html")


@app.route("/clear")
def clear_violations():
    global csp_reports
    csp_reports.clear()
    return redirect("/show")


@app.route("/button-webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        button_events[len(button_events) + 1] = request.json
        return "", 204

    else:
        return button_events


@socketio.on("connect")
def handle_connect():
    # Send existing reports to newly connected client
    emit("initial_reports", csp_reports)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
