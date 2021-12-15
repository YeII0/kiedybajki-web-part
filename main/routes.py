from os import path
from flask import (
    render_template,
    Blueprint,
    redirect,
    flash,
    url_for,
    request,
    current_app,
    send_from_directory,
    jsonify,
)
from flask_login import login_required, current_user
from animechecker import db
from animechecker.main.forms import EditSubscriptions
from animechecker.main.utils import (
    save_subs,
    fetch_subscribed,
    fetch_not_subscribed,
    split_by_seasons_dic,
    split_by_seasons_list,
)
from animechecker.models import Anime


main_bp = Blueprint(
    "main_bp", 
    __name__, 
    template_folder="templates"
    ) 


# Used in javascript in "x" button of news belt notification.
# Set is_saw_news of current user to True.
@main_bp.route("/set_saw_news", methods=["POST"])
def set_saw_news():
    if current_user.is_authenticated and not current_user.is_saw_news:
        current_user.is_saw_news = True
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            current_app.logger.error("Tried to change user value is_saw_news to True.\n%s", str(err))
    return "", 204


# Cover urls
@main_bp.route("/cover_urls", methods=["GET"])
def cover_urls():
    cover_urls = []
    for anime in Anime.query.all():
        if anime.cover_rel_url:
            cover_urls.append("/static/" + anime.cover_rel_url)
    return jsonify(cover_urls)


# Service worker
@main_bp.route("/service_worker.js", methods=["GET"])
def service_worker():
    return current_app.send_static_file("general/scripts/service_worker.js")


# Offline page
@main_bp.route('/offline', methods=["GET"])
def offline():
    return render_template("offline.html", title="Kiedy Bajki | Offline")


# Subscriptions route
@main_bp.route("/subscriptions", methods=["GET"])
@login_required
def subscriptions():
    if current_user.webhook is None:
        flash(
            "Przed korzystaniem z listy subskrypcji należy podać discord webhooka w poniższym formularzu.",
            "info",
        )

        return redirect(url_for("users_bp.account"))

    anime_dic = fetch_subscribed()
    ordered_seasons = split_by_seasons_dic(anime_dic)

    return render_template(
        "subscriptions.html",
        anime_dic=anime_dic,
        ordered_seasons=ordered_seasons,
        edit_form=EditSubscriptions(),
        title="Kiedy Bajki | Moje subskrypcje",
    )


# Not subscribed route
@main_bp.route("/subscribe", methods=["GET"])
@login_required
def subscribe():
    if current_user.webhook is None:
        flash(
            "Przed korzystaniem z listy subskrypcji należy podać discord webhooka w poniższym formularzu.",
            "info",
        )
        return redirect(url_for("users_bp.account"))

    anime_list = fetch_not_subscribed()
    ordered_seasons = split_by_seasons_list(anime_list)

    return render_template(
        "add_subscription.html",
        edit_form=EditSubscriptions(),
        anime_list=anime_list,
        ordered_seasons=ordered_seasons,
        title="Kiedy Bajki | Subskrybuj",
    )


# Route for updating subscriptions and add_subscribe pages. 
# Response is proccessed by javascript and with ajax technique UI is updated
# accordingly to response.
@main_bp.route("/update_subscription", methods=["POST"])
@login_required
def update_subscription():
    edit_form = EditSubscriptions()
    if edit_form.validate_on_submit():
        responseData = save_subs(edit_form, request.form)
        return jsonify(responseData)


# Rest of routes
@main_bp.route("/anime_list", methods=["GET"])
def anime_list():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.subscriptions"))  

    anime_list = Anime.query.order_by(Anime.title)
    ordered_seasons = split_by_seasons_list(anime_list)

    return render_template(
        "anime_list.html",
        ordered_seasons=ordered_seasons,
        title="Kiedy Bajki | Rozpiska anime",
    )


@main_bp.route("/about", methods=["GET"])
def about():
    return render_template("about.html", title="Kiedy Bajki | O aplikacji")


@main_bp.route("/news", methods=["GET"])
def news():
    if current_user.is_authenticated and not current_user.is_saw_news:
        current_user.is_saw_news = True
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            current_app.logger.error("Tried to change user value is_saw_news to True.\n%s", str(err))
    return render_template("news.html", title="Kiedy Bajki | Nowości i zmiany")    


@main_bp.route("/sitemap")
def sitemap():
    return send_from_directory(
        path.join(current_app.root_path, "static"),
        "sitemap.xml",
        mimetype="text/xml",
    )


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Task testing COMMENT LATER!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# from animechecker.tasks.new_records_notification.run import run as run_task
# @main_bp.route("/task", methods=["GET"])
# def task():
#     run_task()
#     return "Task is done"