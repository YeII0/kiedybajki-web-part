import json
from flask import abort, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from animechecker import db
from animechecker.models import Anime, Anime_odcinki
from animechecker.admin.forms import AddAoForm, EditAoForm
from animechecker.admin import admin_bp
from animechecker.admin.utils import split_by_seasons_list


@admin_bp.route("/anime_odcinki", methods=["GET"])
@login_required
def anime_odcinki():
    if current_user.admin is False:
        abort(403)

    anime_odcinki_list = Anime_odcinki.query.join(Anime_odcinki.anime).order_by(Anime.title)
    ordered_seasons = split_by_seasons_list(anime_odcinki_list)

    return render_template(
        "anime_odcinki.html",
        title="Kiedy Bajki | Admin anime_odcinki",
        anime_odcinki_list=anime_odcinki_list,
        edit_form=EditAoForm(formdata=None),
        ordered_seasons=ordered_seasons,
    )

@admin_bp.route("/edit_anime_odcinki", methods=["POST"])
@login_required
def edit_anime_odcinki():
    if current_user.admin is False:
        abort(403)

    response = {"isSuccess": False}
    edit_form = EditAoForm()
    if edit_form.validate_on_submit():
        anime_odcinki = Anime_odcinki.query.get(edit_form.anime_id.data)
        anime_odcinki.source_link = edit_form.source_link.data
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to edit Anime-odcinki record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas edycji rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
    else:
        response["errors"] = edit_form.errors
    return jsonify(response)


@admin_bp.route("/<int:anime_id>/delete_anime_odcinki", methods=["POST"])
@login_required
def delete_anime_odcinki(anime_id):
    if current_user.admin is False:
        abort(403)

    response = {"isSuccess": False}
    anime_odcinki = Anime_odcinki.query.get(anime_id)

    if anime_odcinki is None:
        response["alert"] = {"msg": "Rekordu już nie ma w bazie.", "type": "error"}
    else:
        db.session.delete(anime_odcinki)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to delete Anime-odcinki record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas usuwania rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
    return jsonify(response)


@admin_bp.route("/add_anime_odcinki", methods=["GET"])
@login_required
def add_anime_odcinki():
    if current_user.admin is False:
        abort(403)
    add_form = AddAoForm()
    add_form.title.choices = [(a.anime_id, a.title) for a in Anime.query.order_by(Anime.title) if a.anime_odcinki is None]
    add_form.title.choices.append((-1, "Wybierz anime"))
    return render_template("add_anime_odcinki.html", title="Kiedy Bajki | Admin anime_odcinki", add_form=add_form)


@admin_bp.route("/add_anime_odcinki_submit", methods=["POST"])
@login_required
def add_anime_odcinki_submit():
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    add_form = AddAoForm()

    add_form.title.choices = [(a.anime_id, a.title) for a in Anime.query.order_by(Anime.title) if a.anime_odcinki is None]
    add_form.title.choices.append((-1, "Wybierz anime"))
    if add_form.validate_on_submit():
        ao = Anime_odcinki(anime_id=add_form.title.data, source_link=add_form.source_link.data)
        # line with wrong id only for testing purposes
        #ao = Anime_odcinki(anime_id=2000, source_link=add_form.source_link.data)
        db.session.add(ao)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to add new Anime_odcinki record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas dodawania rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            add_form.title.choices = [(a.anime_id, a.title) for a in Anime.query.order_by(Anime.title) if a.anime_odcinki is None]
            add_form.title.choices.append((-1, "Wybierz anime"))
            add_form.title.data = -1
            add_form.source_link.data = None
            response["isSuccess"] = True
            response["alert"] = {"msg": "Dodano nowy rekord.", "type": "info"}
    else:
        response["errors"] = add_form.errors
    return jsonify(response)