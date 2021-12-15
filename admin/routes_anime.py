import os
from os import path
import requests
from flask import abort, render_template, current_app, jsonify
from flask_login import login_required, current_user
from animechecker import db
from animechecker.models import Anime, Season, User
from animechecker.admin.forms import AddAnimeForm, EditAnimeTitleForm
from animechecker.admin import admin_bp
from animechecker.admin.utils import _add_new_cover, _back_old_cover, _hash_cover
from animechecker.main.utils import split_by_seasons_list, update_service_worker

@admin_bp.route("/menu")
@login_required
def menu():
    if current_user.admin is False:
        abort(403)
    return render_template("menu.html", title="Kiedy Bajki | Admin menu")

@admin_bp.route("/indicate_news", methods=["POST"])
@login_required
def indicate_news():
    if current_user.admin is False:
        abort(403)
    response = {"isSuccess": False}
    
    users = User.query.all()
    for user in users:
        user.is_saw_news = False

    try:
        db.session.commit()
    except Exception as err:
        current_app.logger.error("Tried to set is_saw_news to False to all users in db.\n" + str(err))
        db.session.rollback()    
        response["alert"] = {"msg": "Wystąpił podczas próby aktualizacji bazy. Spróbuj ponownie.", "type": "error"}
    else:
        response["isSuccess"] = True
    return jsonify(response)




@admin_bp.route("/anime", methods=["GET"])
@login_required
def anime():
    if current_user.admin is False:
        abort(403)

    edit_form = EditAnimeTitleForm(formdata=None)
    edit_form.season.choices = [(s.season_id, s.season) for s in Season.query.order_by(Season.season)]
    edit_form.season.choices.append((-1, "Wybierz"))

    anime_list = Anime.query.order_by(Anime.title)
    ordered_seasons = split_by_seasons_list(anime_list)

    return render_template(
        "anime.html",
        title="Kiedy Bajki | Admin anime",
        ordered_seasons=ordered_seasons,
        edit_form=edit_form,
    )


@admin_bp.route("/edit_anime", methods=["POST"])
@login_required
def edit_anime():
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    edit_form = EditAnimeTitleForm()
    edit_form.season.choices = [(s.season_id, s.season) for s in Season.query.order_by(Season.season)]
    edit_form.season.choices.append((-1, "Wybierz"))

    if edit_form.validate_on_submit():
        add_new_cover_data = None
        anime = Anime.query.get(edit_form.anime_id.data)
        anime.title = edit_form.title.data
        anime.mal_link = edit_form.mal_link.data
        if edit_form.season.data != -1:
            anime.season_id = edit_form.season.data

        if edit_form.cover_link.data:
            add_new_cover_data = _add_new_cover(response, edit_form, anime)
            response = add_new_cover_data["response"]
            if not add_new_cover_data["is_success"]:
                return jsonify(response)
        try:
            db.session.commit()
        except Exception as err:
            if add_new_cover_data:
                _back_old_cover(add_new_cover_data)
            current_app.logger.error("Tried to edit Anime record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas edycji rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            # Remove old cover from filesystem.
            if (
                add_new_cover_data and 
                add_new_cover_data["old_cover_temp_path"] and 
                path.isfile(add_new_cover_data["old_cover_temp_path"])
            ):
                os.remove(add_new_cover_data["old_cover_temp_path"])       
            response["isSuccess"] = True
    else:
        response["errors"] = edit_form.errors
    return jsonify(response)

@admin_bp.route("/<int:anime_id>/delete_anime", methods=["POST"])
@login_required
def delete_anime(anime_id):
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    anime = Anime.query.get(anime_id)

    if anime is None:
        response["alert"] = {"msg": "Rekordu już nie ma w bazie.", "type": "error"}
    else:
        db.session.delete(anime)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to delete Anime record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas usuwania rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            cover_rel_path = anime.cover_rel_url.replace("/", os.sep)
            cover_path = path.join(current_app.static_folder, cover_rel_path)
            if path.isfile(cover_path):
                os.remove(cover_path)
            response["isSuccess"] = True
    return jsonify(response)


@admin_bp.route("/add_anime", methods=["GET"])
@login_required
def add_anime():
    if current_user.admin is False:
        abort(403)

    add_form = AddAnimeForm()
    add_form.season.choices = [(s.season_id, s.season) for s in Season.query.order_by(Season.season)]
    add_form.season.choices.append((-1, "Wybierz"))

    return render_template("add_anime.html", title="Kiedy Bajki | Admin anime", add_form=add_form)


@admin_bp.route("/add_anime_submit", methods=["POST"])
@login_required
def add_anime_submit():
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    add_form = AddAnimeForm()
    add_form.season.choices = [(s.season_id, s.season) for s in Season.query.order_by(Season.season)]
    add_form.season.choices.append((-1, "Wybierz"))

    if add_form.validate_on_submit():

        # Download cover from url provided in form.
        ############################################################################
        try:
            cover_response = requests.get(add_form.cover_link.data)
        except Exception as err:
            current_app.logger.error(str(err))
            response["errors"] = {"cover_link": ["Błąd podczas próby wykonanywania żądania HTTP."]}
            return jsonify(response)
        try:
            cover_response.raise_for_status()
        except Exception as err:
            current_app.logger.error(str(err))
            response["errors"] = {"cover_link": ["Wystąpił błędny kod odpowiedzi HTTP."]}
            return jsonify(response)
        if (
            cover_response.headers.get('Content-Type') and 
            not cover_response.headers.get('Content-Type').startswith("image/")
        ):
            response["errors"] = {"cover_link": ["To nie jest link do obrazka."]}            
            return jsonify(response) 
        if (
            cover_response.headers.get('Content-Type') and 
            cover_response.headers.get('Content-Type') == "image/webp"
        ):
            response["errors"] = {"cover_link": ["Format webp jest nieobsługiwany."]}
            return jsonify(response)        
        ############################################################################
        
        # Create and add new record to db.
        ############################################################################
        anime = Anime(
            title=add_form.title.data, 
            season_id=add_form.season.data, 
            mal_link=add_form.mal_link.data, 
            cover_rel_url=""
        )
        db.session.add(anime)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to add new Anime record to db.\n" + str(err))        
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas dodawania rekordu. Spróbuj ponownie.", "type": "error"}
        ##################################################################################
        else:
            # Save cover into filesystem
            ##################################################################################
            filename = anime.anime_id
            file_extension = path.splitext(add_form.cover_link.data.rsplit("/", 1)[1])[1]
            cover_path = path.join(
                current_app.static_folder, 
                "general", "media", "anime_covers", 
                f"{filename}{file_extension}"
            )
            try:
                with open(cover_path, 'wb') as f:
                    for chunk in cover_response.iter_content(100000):
                        f.write(chunk)
            ##################################################################################
            except Exception as err:
                current_app.logger.error(str(err))
                response["errors"] = {"cover_link": ["Wystąpił błąd podczas próby zapisu okładki w systemie plików."]}

                # Delete file and record
                ############################################################################
                if path.isfile(cover_path):
                    os.remove(cover_path)
                db.session.delete(anime)
                try:
                    db.session.commit()
                except Exception as err:
                    db.session.rollback()
                    current_app.logger.error(
                        "Tried to delete anime because error occurs while saving cover into filesystem.\n%s", 
                        str(err)
                        )
                    response["errors"] = {"cover_link": [
                        "Wystąpił błąd podczas próby zapisu okładki w systemie plików.", 
                        "Wystąpił błąd podczas próby usunięcia rekordy z bazy."
                        ]}
                return jsonify(response) 
                ############################################################################
            
            # Add hash to filename
            ############################################################################
            hash_cover_data = _hash_cover(cover_path, file_extension, anime, response)
            if not hash_cover_data["is_success"]:
                response = hash_cover_data["response"]
                # Delete file and record
                ############################################################################
                if path.isfile(cover_path):
                    os.remove(cover_path)
                db.session.delete(anime)
                try:
                    db.session.commit()
                except Exception as err:
                    db.session.rollback()
                    current_app.logger.error(
                        "Tried to delete anime because error occurs while saving cover into filesystem.\n%s", 
                        str(err)
                        )
                    response["errors"]["cover_link"].append( 
                        "Wystąpił błąd podczas próby usunięcia rekordy z bazy. Dodany rekord nie posiada okładki."
                    )            
                return jsonify(response)
            filename = hash_cover_data["hashed_filename"]
            cover_path = hash_cover_data["hashed_cover_path"]

            # Save cover path into db
            ############################################################################
            cover_rel_url = f"general/media/anime_covers/{filename}{file_extension}"
            anime.cover_rel_url = cover_rel_url
            try:
                db.session.commit()
            except Exception as err:
                current_app.logger.error("Tried add cover path to anime record in db.\n%s", str(err))
                db.session.rollback()  
                response["errors"] = {"cover_link": ["Wystąpił błąd podczas próby dodania ścieżki do okładki do bazy."]}
                if path.isfile(cover_path):
                    os.remove(cover_path) 
                db.session.delete(anime)
                try:
                    db.session.commit()
                except Exception as err:
                    db.session.rollback()
                    current_app.logger.error(
                        "Error occurs while trying to delete record." + 
                        "Attempt to remove was taken because problem occurs while trying to add cover path to db.\n%s", 
                        str(err)
                        )
                return jsonify(response)                             
            ############################################################################

            response["isSuccess"] = True
            response["alert"] = {"msg": "Dodano nowy rekord.", "type": "info"}
            add_form.title.data = None
            add_form.mal_link.data = None
            add_form.season.data = -1
            # Update service worker to force cache new cover during precache.
            update_service_worker()
    else:
        response["errors"] = add_form.errors
    return jsonify(response)