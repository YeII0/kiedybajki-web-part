from flask import abort, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from animechecker import db
from animechecker.models import Anime, Animesub
from animechecker.admin.forms import AddAnimesubForm, EditAnimesubForm
from animechecker.admin import admin_bp
from animechecker.admin.utils import split_by_seasons_list


@admin_bp.route("/animesub", methods=["GET"])
@login_required
def animesub():
    if current_user.admin is False:
        abort(403)

    animesub_list = Animesub.query.join(Animesub.anime).order_by(Anime.title, Animesub.author)
    ordered_seasons = split_by_seasons_list(animesub_list)

    return render_template(
        "animesub.html",
        title="Kiedy Bajki | Admin animesub",
        edit_form=EditAnimesubForm(formdata=None),
        ordered_seasons=ordered_seasons,
    )

@admin_bp.route("/edit_animesub", methods=["POST"])
@login_required
def edit_animesub():
    if current_user.admin is False:
        abort(403)

    response = {"isSuccess": False}
    edit_form = EditAnimesubForm()
    if edit_form.validate_on_submit():
        animesub_old = Animesub.query.get(edit_form.animesub_id.data)
        # Checking if record with choosed author and title exist.
        animesub_new = Animesub.query.filter_by(
            anime_id=animesub_old.anime_id, author=edit_form.author.data
        ).first()
        if animesub_new and (animesub_old.animesub_id != animesub_new.animesub_id):
            response["errors"] = {"author": ["Wybrane anime z tym autorem jest już w bazie."]}
        else:
            animesub = Animesub.query.get(edit_form.animesub_id.data)
            animesub.author = edit_form.author.data
            animesub.ansi_title = edit_form.ansi_title.data
            animesub.cr_numbering_diff = edit_form.cr_numbering_diff.data
            if edit_form.cr_diff_title.data == "":
                animesub.cr_diff_title = None
            else:
                animesub.cr_diff_title = edit_form.cr_diff_title.data            
            try:
                db.session.commit()
            except Exception as err:
                current_app.logger.error(
                    "Tried to edit Animesub record to db.\n" + str(err)
                )
                db.session.rollback()
                response["alert"] = {"msg": "Wystąpił błąd podczas edycji rekordu. Spróbuj ponownie.", "type": "error"}
            else:
                response["isSuccess"] = True
    else:
        response["errors"] = edit_form.errors
    return jsonify(response)


@admin_bp.route("/<int:animesub_id>/delete_animesub", methods=["POST"])
@login_required
def delete_animesub(animesub_id):
    if current_user.admin is False:
        abort(403)

    response = {"isSuccess": False}
    animesub = Animesub.query.get(animesub_id)

    if animesub is None:
        response["alert"] = {"msg": "Rekordu już nie ma w bazie.", "type": "error"}
    else:
        db.session.delete(animesub)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to delete Animesub record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas usuwania rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
    return jsonify(response)


@admin_bp.route("/add_animesub", methods=["GET"])
@login_required
def add_animesub():
    if current_user.admin is False:
        abort(403)
    add_form = AddAnimesubForm()
    add_form.title.choices = [
        (a.anime_id, a.title) for a in Anime.query.order_by(Anime.title)
    ]
    add_form.title.choices.append((-1, "Wybierz anime"))
            
    return render_template(
        "add_animesub.html", title="Kiedy Bajki | Admin animesub", add_form=add_form
    )


@admin_bp.route("/add_animesub_submit", methods=["POST"])
@login_required
def add_animesub_submit():
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    add_form = AddAnimesubForm()
    add_form.title.choices = [
        (a.anime_id, a.title) for a in Anime.query.order_by(Anime.title)
    ]
    add_form.title.choices.append((-1, "Wybierz anime"))
    if add_form.validate_on_submit():
        animesub = Animesub.query.filter_by(
            anime_id=add_form.title.data, author=add_form.author.data
        ).first()
        if animesub:
            response["alert"] = {"msg": "Wybrane anime z tym autorem jest już w bazie.", "type": "error"}
        else:
            animesub = Animesub(
                anime_id=add_form.title.data,
                author=add_form.author.data,
                ansi_title=add_form.ansi_title.data,
                cr_numbering_diff=add_form.cr_numbering_diff.data,
            )

            if add_form.cr_diff_title.data == "":
                animesub.cr_diff_title = None
            else:
                animesub.cr_diff_title = add_form.cr_diff_title.data  

            db.session.add(animesub)
            try:
                db.session.commit()
            except Exception as err:
                current_app.logger.error(
                    "Tried to add new Animesub record to db.\n" + str(err)
                )
                db.session.rollback()
                response["alert"] = {"msg": "Wystąpił błąd podczas dodawania rekordu. Spróbuj ponownie.", "type": "error"}
            else:
                response["isSuccess"] = True
                response["alert"] = {"msg": "Dodano nowy rekord.", "type": "info"}

                add_form.title.choices = [
                    (a.anime_id, a.title) for a in Anime.query.order_by(Anime.title)
                ]
                add_form.title.choices.append((-1, "Wybierz anime"))
                add_form.title.data = -1
                add_form.author.data = None
                add_form.ansi_title.data = None
                add_form.cr_numbering_diff.data = None    
    else:
        response["errors"] = add_form.errors
    return jsonify(response)