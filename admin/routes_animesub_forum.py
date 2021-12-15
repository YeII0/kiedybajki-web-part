from flask import abort, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from animechecker import db
from animechecker.models import Anime, Animesub_forum
from animechecker.admin.forms import AddAnimesubForumForm, EditAnimesubForumForm
from animechecker.admin import admin_bp
from animechecker.admin.utils import split_by_seasons_list


@admin_bp.route("/animesub_forum", methods=["GET"])
@login_required
def animesub_forum():
    if current_user.admin is False:
        abort(403)

    animesub_forum_list = Animesub_forum.query.join(Animesub_forum.anime).order_by(Anime.title, Animesub_forum.author)
    ordered_seasons = split_by_seasons_list(animesub_forum_list)

    return render_template(
        "animesub_forum.html",
        title="Kiedy Bajki | Admin forum Animesub",
        edit_form=EditAnimesubForumForm(formdata=None),
        ordered_seasons=ordered_seasons,  
    )


@admin_bp.route("/edit_animesub_forum", methods=["POST"])
@login_required
def edit_animesub_forum():
    if current_user.admin is False:
        abort(403)

    response = {"isSuccess": False}
    edit_form = EditAnimesubForumForm()

    if edit_form.validate_on_submit():
        animesub_forum_old = Animesub_forum.query.get(edit_form.animesub_forum_id.data)
        # Checking if record with choosed author and title exist.
        animesub_forum_new = Animesub_forum.query.filter_by(
            anime_id=animesub_forum_old.anime_id, author=edit_form.author.data
        ).first()
        if animesub_forum_new and (animesub_forum_old.animesub_forum_id != animesub_forum_new.animesub_forum_id):
            response["errors"] = {"author": ["Wybrane anime z tym autorem jest już w bazie."]}
        else:
            animesub_forum = Animesub_forum.query.get(edit_form.animesub_forum_id.data)
            animesub_forum.author = edit_form.author.data
            animesub_forum.source_link = edit_form.source_link.data
            animesub_forum.cr_numbering_diff = edit_form.cr_numbering_diff.data
            if edit_form.cr_diff_title.data == "":
                animesub_forum.cr_diff_title = None
            else:
                animesub_forum.cr_diff_title = edit_form.cr_diff_title.data            
            try:
                db.session.commit()
            except Exception as err:
                current_app.logger.error(
                    "Tried to edit Animesub_forum record in db.\n" + str(err)
                )
                db.session.rollback()
                response["alert"] = {"msg": "Wystąpił błąd podczas edycji rekordu. Spróbuj ponownie.", "type": "error"}
            else:
                response["isSuccess"] = True
    else:
        response["errors"] = edit_form.errors
    return jsonify(response)


@admin_bp.route("/<int:animesub_forum_id>/delete_animesub_forum", methods=["POST"])
@login_required
def delete_animesub_forum(animesub_forum_id):
    if current_user.admin is False:
        abort(403)

    response = {"isSuccess": False}
    animesub_forum = Animesub_forum.query.get(animesub_forum_id)

    if animesub_forum is None:
        response["alert"] = {"msg": "Rekordu już nie ma w bazie.", "type": "error"}
    else:
        db.session.delete(animesub_forum)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to delete Animesub_forum record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas usuwania rekordu. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
    return jsonify(response)

@admin_bp.route("/add_animesub_forum", methods=["GET"])
@login_required
def add_animesub_forum():
    if current_user.admin is False:
        abort(403)
    add_form = AddAnimesubForumForm()
    add_form.title.choices = [
        (a.anime_id, a.title) for a in Anime.query.order_by(Anime.title)
    ]
    add_form.title.choices.append((-1, "Wybierz anime"))

    return render_template(
        "add_animesub_forum.html", title="Kiedy Bajki | Admin animesub_forum", add_form=add_form
    )


@admin_bp.route("/add_animesub_forum_submit", methods=["POST"])
@login_required
def add_animesub_forum_submit():
    if current_user.admin is False:
        abort(403)    
    response = {"isSuccess": False}
    add_form = AddAnimesubForumForm()
    add_form.title.choices = [
        (a.anime_id, a.title) for a in Anime.query.order_by(Anime.title)
    ]
    add_form.title.choices.append((-1, "Wybierz anime"))
    if add_form.validate_on_submit():
        animesub_forum = Animesub_forum.query.filter_by(
            anime_id=add_form.title.data, author=add_form.author.data
        ).first()
        if animesub_forum:
            response["alert"] = {"msg": "Wybrane anime z tym autorem jest już w bazie.", "type": "error"}
        else:
            animesub_forum = Animesub_forum(
                anime_id=add_form.title.data,
                author=add_form.author.data,
                source_link=add_form.source_link.data,
                cr_numbering_diff=add_form.cr_numbering_diff.data,
            )

            if add_form.cr_diff_title.data == "":
                animesub_forum.cr_diff_title = None
            else:
                animesub_forum.cr_diff_title = add_form.cr_diff_title.data     

            db.session.add(animesub_forum)
            try:
                db.session.commit()
            except Exception as err:
                current_app.logger.error(
                    "Tried to add new Animesub_forum record to db.\n" + str(err)
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
                add_form.source_link.data = None
                add_form.cr_numbering_diff.data = None
    else:
        response["errors"] = add_form.errors
    return jsonify(response)