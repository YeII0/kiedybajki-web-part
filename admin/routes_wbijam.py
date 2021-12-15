from flask import abort, render_template, current_app, jsonify
from flask_login import login_required, current_user
from animechecker import db
from animechecker.models import Anime, Wbijam
from animechecker.admin.forms import AddWbijamForm, EditWbijamForm
from animechecker.admin import admin_bp
from animechecker.admin.utils import split_by_seasons_list


@admin_bp.route("/wbijam", methods=["GET"])
@login_required
def wbijam():
    if current_user.admin is False:
        abort(403)

    wbijam_list = Wbijam.query.join(Wbijam.anime).order_by(Anime.title)
    ordered_seasons = split_by_seasons_list(wbijam_list)

    return render_template(
        "wbijam.html",
        title="Kiedy Bajki | Admin wbijam",
        edit_form=EditWbijamForm(formdata=None),
        ordered_seasons=ordered_seasons,
    )


@admin_bp.route("/edit_wbijam", methods=["POST"])
@login_required
def edit_wbijam():
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    edit_form = EditWbijamForm()

    if edit_form.validate_on_submit():
        wbijam = Wbijam.query.get(edit_form.anime_id.data)
        wbijam.source_link = edit_form.source_link.data
        wbijam.title_in_site = edit_form.title_in_site.data
        wbijam.cr_numbering_diff = edit_form.cr_numbering_diff.data
        if edit_form.cr_diff_title.data == "":
            wbijam.cr_diff_title = None
        else:
            wbijam.cr_diff_title = edit_form.cr_diff_title.data
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to edit Wbijam record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas edycji rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
    else:
        response["errors"] = edit_form.errors
    return jsonify(response)


@admin_bp.route("/<int:anime_id>/delete_wbijam", methods=["POST"])
@login_required
def delete_wbijam(anime_id):
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    wbijam = Wbijam.query.get(anime_id)

    if wbijam is None:
        response["alert"] = {"msg": "Rekordu już nie ma w bazie.", "type": "error"}
    else:
        db.session.delete(wbijam)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to delete Wbijam record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas usuwania rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
    return jsonify(response)


@admin_bp.route("/add_wbijam", methods=["GET"])
@login_required
def add_wbijam():
    if current_user.admin is False:
        abort(403)
    add_form = AddWbijamForm()
    add_form.title.choices = [(a.anime_id, a.title) for a in Anime.query.order_by(Anime.title) if a.wbijam is None]
    add_form.title.choices.append((-1, "Wybierz anime"))
    return render_template("add_wbijam.html", title="Kiedy Bajki | Admin wbijam", add_form=add_form)


@admin_bp.route("/add_wbijam_submit", methods=["POST"])
@login_required
def add_wbijam_submit():
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    add_form = AddWbijamForm()
    add_form.title.choices = [(a.anime_id, a.title) for a in Anime.query.order_by(Anime.title) if a.wbijam is None]
    add_form.title.choices.append((-1, "Wybierz anime"))
    if add_form.validate_on_submit():
        wbijam = Wbijam(
            anime_id=add_form.title.data, 
            source_link=add_form.source_link.data,
            title_in_site=add_form.title_in_site.data,
            cr_numbering_diff=add_form.cr_numbering_diff.data
        )
        if add_form.cr_diff_title.data == "":
            wbijam.cr_diff_title = None
        else:
            wbijam.cr_diff_title = add_form.cr_diff_title.data        

        # line with wrong id only for testing purposes
        # wbijam = Wbijam(anime_id=2000, source_link=add_form.source_link.data)
        db.session.add(wbijam)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to add new Wbijam record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas dodawania rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
            response["alert"] = {"msg": "Dodano nowy rekord.", "type": "info"}
            add_form.title.choices = [(a.anime_id, a.title) for a in Anime.query.order_by(Anime.title) if a.wbijam is None]
            add_form.title.choices.append((-1, "Wybierz anime"))
            add_form.title.data = -1
            add_form.source_link.data = None  
    else:
        response["errors"] = add_form.errors
    return jsonify(response)  