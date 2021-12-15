import os
import shutil
import hashlib
from os import path
import requests
from flask import current_app
from animechecker.models import Season

# Function for splitting records from wbijam, okami-subs, a-o, animesub, animesub forum by seasons.
# Take one parameter which is a list with records.
def split_by_seasons_list(records):
    ordered_seasons = {}

    for season in Season.query.order_by(Season.order):
        ordered_seasons[(season.season_id, season.season)] = []
    
    for record in records:
        ordered_seasons[(record.anime.season.season_id, record.anime.season.season)].append(record)

    return ordered_seasons


# Helper function for edit_anime route.
def _add_new_cover(response, form, anime):
    cover_data = {
        "is_success": False, 
        "response": response, 
        "old_cover_orig_path": None,
        "old_cover_temp_path": None, 
        "new_cover_path": None,
    }

    # Download cover from url provided in form.
    ############################################################################
    try:
        cover_response = requests.get(form.cover_link.data)
    except Exception as err:
        current_app.logger.error(str(err))
        response["errors"] = {"cover_link": ["Błąd podczas próby wykonanywania żądania HTTP."]}
        return cover_data
    try:
        cover_response.raise_for_status()
    except Exception as err:
        current_app.logger.error(str(err))
        response["errors"] = {"cover_link": ["Wystąpił błędny kod odpowiedzi HTTP."]}
        return cover_data
    if (
        cover_response.headers.get('Content-Type') and 
        not cover_response.headers.get('Content-Type').startswith("image/")
    ):
        response["errors"] = {"cover_link": ["To nie jest link do obrazka."]}
        return cover_data 
    if (
        cover_response.headers.get('Content-Type') and 
        cover_response.headers.get('Content-Type') == "image/webp"
    ):
        response["errors"] = {"cover_link": ["Format webp jest nieobsługiwany."]}
        return cover_data    
    ############################################################################

    # Rename old cover. Needed as backup if something fail while creating new one.
    old_cover_temp_path = None
    if anime.cover_rel_url:
        cover_rel_path = anime.cover_rel_url.replace("/", path.sep)
        old_cover_path = path.join(current_app.static_folder, cover_rel_path)
        if path.isfile(old_cover_path):
            old_cover_temp_path = old_cover_path + "_temp"
            shutil.move(old_cover_path, old_cover_temp_path) 
        else:
            old_cover_path = None
    else:
        old_cover_path = None

    # Save cover into filesystem
    ############################################################################
    filename = anime.anime_id
    file_extension = path.splitext(form.cover_link.data.rsplit("/", 1)[1])[1]
    new_cover_path = path.join(
        current_app.static_folder, 
        "general", "media", "anime_covers", 
        f"{filename}{file_extension}"
    )
    try:
        with open(new_cover_path, "wb") as f:
            for chunk in cover_response.iter_content(100000):
                f.write(chunk)
    except Exception as err:
        current_app.logger.error(str(err))
        response["errors"] = {"cover_link": [
            "Wystąpił błąd podczas próby zapisu okładki w systemie plików."
            ]}
        # Remove new cover and bring back original name of old one.
        if path.isfile(new_cover_path):
            os.remove(new_cover_path)
        if old_cover_path:
            shutil.move(old_cover_temp_path, old_cover_path)

        return cover_data
    ############################################################################

    # Add hash to filename
    ############################################################################
    hash_cover_data = _hash_cover(new_cover_path, file_extension, anime, response)
    if not hash_cover_data["is_success"]:
        response = hash_cover_data["response"]
        # Remove new cover and bring back original name of old one.
        if path.isfile(new_cover_path):
            os.remove(new_cover_path)
        if old_cover_path:
            shutil.move(old_cover_temp_path, old_cover_path)
        return cover_data
    new_cover_path = hash_cover_data["hashed_cover_path"]
    filename = hash_cover_data["hashed_filename"]

    # Add new cover into anime record without commiting
    ############################################################################
    cover_rel_url = f"general/media/anime_covers/{filename}{file_extension}"
    anime.cover_rel_url = cover_rel_url

    cover_data["is_success"] = True
    cover_data["old_cover_orig_path"] = old_cover_path
    cover_data["old_cover_temp_path"] = old_cover_temp_path
    cover_data["new_cover_path"] = new_cover_path
    return cover_data


# Helper function for edit_anime route.
def _back_old_cover(add_new_cover_data):
    new_cover_path = add_new_cover_data["new_cover_path"]
    old_cover_temp_path = add_new_cover_data["old_cover_temp_path"]
    old_cover_orig_path = add_new_cover_data["old_cover_orig_path"]

    # Remove new cover and bring back original name of old one.
    if path.isfile(new_cover_path):
        os.remove(new_cover_path)
    if old_cover_temp_path:
        shutil.move(old_cover_temp_path, old_cover_orig_path)

# Helper function for add_anime and edit_anime route.
def _hash_cover(cover_path, file_extension, anime, response):
    cover_data = {
        "is_success": False,
        "hashed_cover_path": None,
        "hashed_filename": None,
        "response": response
    }
    try:
        with open(cover_path, "rb") as binary:
            file_hash = hashlib.md5(binary.read()).hexdigest()
    except Exception as err:
        current_app.logger.error(str(err))
        response["errors"] = {"cover_link": [
            "Wystąpił błąd podczas wygenerowania hasha do okładki."
            ]}
        return cover_data
    filename = f"{anime.anime_id}-{file_hash}"
    updated_cover_path = path.join(
        current_app.static_folder, 
        "general", "media", "anime_covers", 
        f"{filename}{file_extension}"
    )
    shutil.move(cover_path, updated_cover_path)
    cover_path = updated_cover_path

    cover_data["is_success"] = True
    cover_data["hashed_cover_path"] = cover_path
    cover_data["hashed_filename"] = filename
    return cover_data