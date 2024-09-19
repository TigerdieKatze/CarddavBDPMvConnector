import schedule
import time
from threading import Thread
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import CONFIG, logger, save_config
from carddav_sync import sync_contacts
from notifications import send_email

app = Flask(__name__)
CORS(app)

# Global variable to store the last sync status
last_sync_status = {"status": "Not started", "last_run": None, "details": None}

def run_sync():
    global last_sync_status
    try:
        logger.info("Starting synchronization")
        last_sync_status["status"] = "In progress"
        last_sync_status["last_run"] = datetime.now().isoformat()

        sync_contacts()

        last_sync_status["status"] = "Completed"
        last_sync_status["details"] = "Synchronization completed successfully"
        logger.info("Synchronization completed successfully")
    except Exception as e:
        last_sync_status["status"] = "Failed"
        last_sync_status["details"] = str(e)
        logger.error(f"Synchronization failed: {e}")
        send_email("Synchronization Failed", f"Synchronization failed with error: {e}")

def run_scheduled_sync():
    while True:
        schedule.run_pending()
        time.sleep(60)

@app.route('/sync', methods=['POST'])
def trigger_sync():
    thread = Thread(target=run_sync)
    thread.start()
    return jsonify({"message": "Synchronization started"}), 202

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(last_sync_status)

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    configurable_fields = [
        "GROUP_MAPPING",
        "DEFAULT_GROUP",
        "APPLY_GROUP_MAPPING_TO_PARENTS",
        "APPLY_DEFAULT_GROUP_TO_PARENTS",
        "RUN_SCHEDULE",
        "NOTIFICATION_EMAIL",
        "DRY_RUN"
    ]
    
    if request.method == 'GET':
        return jsonify({field: CONFIG[field] for field in configurable_fields})
    
    elif request.method == 'POST':
        new_config = request.json
        for key, value in new_config.items():
            if key in configurable_fields:
                CONFIG[key] = value
        
        save_config(CONFIG)
        
        # If RUN_SCHEDULE has changed, update the schedule
        if "RUN_SCHEDULE" in new_config:
            schedule.clear()
            if CONFIG["RUN_SCHEDULE"] == "daily":
                schedule.every().day.at("04:00").do(run_sync)
        
        return jsonify({
            "message": "Configuration updated",
            "new_config": {field: CONFIG[field] for field in configurable_fields}
        }), 200

if __name__ == "__main__":
    if CONFIG["RUN_SCHEDULE"] == "daily":
        schedule.every().day.at("04:00").do(run_sync)
        sync_thread = Thread(target=run_scheduled_sync)
        sync_thread.start()
    
    app.run(host='0.0.0.0', port=5000)