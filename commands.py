import datetime
import json
import hashlib
import shutil
from os import path
from flask import Blueprint, current_app
from animechecker.tasks.new_records_notification.run import run as send_notifications_task
import animechecker.main.utils as utils

commands_bp = Blueprint("commands_bp", __name__)

@commands_bp.cli.command("send_new_records_notification")
def send_new_records_notification():
    """Run task which notify users about new titles added to db through discord"""
    send_notifications_task()

@commands_bp.cli.command("make_versioned_cache_manifest")
def make_versioned_cache_manifest():
    # Create manifest file hash. Thing to notice is after every creating new manifest file
    # hash will be different even if data will be the same cuz even if output will be the same
    # on bit levels there will be differences. 
    # Better than nothing. Manifest will be cached as long as new one will be not created.
    try:
        with open(path.join(current_app.static_folder, "cache_manifest.json"), "rb") as binary:
            file_hash = hashlib.md5(binary.read()).hexdigest()
    except Exception:
        print("Manifest doesn't exist")
        return
    
    # Load data from manifest file.
    with open(path.join(current_app.static_folder, "cache_manifest.json"), "r") as json_file:
        data = json.load(json_file)
        data["cache_manifest.json"] = f"cache_manifest-{file_hash}.json"
    
    # Write data updated data with manifest pair itself into manisest file.
    with open(path.join(current_app.static_folder, "cache_manifest.json"), "w") as json_file:
        json.dump(data, json_file)

    # Create new versioned manifest
    shutil.copy(path.join(current_app.static_folder, "cache_manifest.json"), path.join(current_app.static_folder, f"cache_manifest-{file_hash}.json"))
    print("Versioned cache manifest created.")


@commands_bp.cli.command("update_service_worker")
def update_service_worker():
    utils.update_service_worker()



    
        


    

    
