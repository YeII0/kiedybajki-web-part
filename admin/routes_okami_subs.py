from flask import abort, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from animechecker import db
from animechecker.models import Anime, Okami_subs
from animechecker.admin.forms import (
    AddOkamiSubsForm,
    EditOkamiSubsForm,
)
from animechecker.admin import admin_bp
from animechecker.admin.utils import split_by_seasons_list


@admin_bp.route("/okami_subs", methods=["GET"])
@login_required
def okami_subs():
    if current_user.admin is False:
        abort(403)

    okami_subs_list = Okami_subs.query.join(Okami_subs.anime).order_by(Anime.title)
    ordered_seasons = split_by_seasons_list(okami_subs_list)

    return render_template(
        "okami_subs.html",
        title="Kiedy Bajki | Admin okami-subs",
        edit_form=EditOkamiSubsForm(formdata=None),
        ordered_seasons=ordered_seasons,
    )


@admin_bp.route("/edit_okami_subs", methods=["POST"])
@login_required
def edit_okami_subs():
    if current_user.admin is False:
        abort(403)

    response = {"isSuccess": False}
    edit_form = EditOkamiSubsForm()

    if edit_form.validate_on_submit():
        okami_subs = Okami_subs.query.get(edit_form.anime_id.data)
        okami_subs.title_in_site = edit_form.title_in_site.data
        okami_subs.season_page_link = edit_form.season_page_link.data
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to edit Okami-subs record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas edycji rekordu. Spróbuj ponownie.", "type": "error"}            
        else:
            response["isSuccess"] = True            
    else:
        response["errors"] = edit_form.errors
    return jsonify(response)


@admin_bp.route("/<int:anime_id>/delete_okami_subs", methods=["POST"])
@login_required
def delete_okami_subs(anime_id):
    if current_user.admin is False:
        abort(403)

    response = {"isSuccess": False}
    okami_subs = Okami_subs.query.get(anime_id)

    if okami_subs is None:
        response["alert"] = {"msg": "Rekordu już nie ma w bazie.", "type": "error"}
    else:
        db.session.delete(okami_subs)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to delete Okami-subs record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas edycji rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
    return jsonify(response)


@admin_bp.route("/add_okami_subs", methods=["GET"])
@login_required
def add_okami_subs():
    if current_user.admin is False:
        abort(403)
    add_form = AddOkamiSubsForm()
    add_form.title.choices = [
        (a.anime_id, a.title)
        for a in Anime.query.order_by(Anime.title)
        if a.okami_subs is None
    ]

    add_form.title.choices.append((-1, "Wybierz anime"))

    return render_template(
        "add_okami_subs.html", title="Kiedy Bajki | Admin okami_subs", add_form=add_form
    )


@admin_bp.route("/add_okami_subs_submit", methods=["POST"])
@login_required
def add_okami_subs_submit():
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    add_form = AddOkamiSubsForm()
    add_form.title.choices = [
        (a.anime_id, a.title)
        for a in Anime.query.order_by(Anime.title)
        if a.okami_subs is None
    ]
    add_form.title.choices.append((-1, "Wybierz anime"))
    if add_form.validate_on_submit():
        okami_subs = Okami_subs(
            anime_id=add_form.title.data,
            title_in_site=add_form.title_in_site.data,
            season_page_link=add_form.season_page_link.data,
        )

        db.session.add(okami_subs)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error(
                "Tried to add new Okami_subs record to db.\n" + str(err)
            )
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas dodawania rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
            response["alert"] = {"msg": "Dodano nowy rekord.", "type": "info"}
            add_form.title.choices = [
                (a.anime_id, a.title)
                for a in Anime.query.order_by(Anime.title)
                if a.okami_subs is None
            ]
            add_form.title.choices.append((-1, "Wybierz anime"))
            add_form.title.data = -1    
            add_form.title_in_site.data = None
            add_form.season_page_link.data = None  
    else:
        response["errors"] = add_form.errors
    return jsonify(response)  