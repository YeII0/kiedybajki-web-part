import json
import datetime
from os import path
from collections import OrderedDict
from flask import current_app
from flask_login import current_user
from sqlalchemy import and_
from sqlalchemy.orm import contains_eager
from animechecker import db, create_app
from animechecker.models import (
    Anime,
    Animesub,
    Animesub_sub,
    Animesub_forum,
    Animesub_forum_sub,
    Wbijam,
    Wbijam_sub,
    Anime_odcinki,
    Anime_odcinki_sub,
    Okami_subs,
    Okami_subs_sub,
    Global_anime_ep,
    User,
    Season
)


def update_service_worker():
    """
    Replace first line of file to comment which contain current date.
    By doing that file will got new hash while digest and service worker will be updated
    cuz is updated when he got new url.
    """
    file_path = path.join(current_app.static_folder, "general", "scripts", "service_worker.js")
    all_lines = None

    try:
        with open(file_path, "r") as textFile:
            all_lines = textFile.readlines()
    except Exception as err:
        print(str(err))
        return

    try:
        with open(file_path, "w") as textFile:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")           
            all_lines[0] = f"// Last update_service_worker command use: {now}. DON'T REMOVE THIS LINE.\n"
            textFile.writelines(all_lines)
    except Exception as err:
        print(str(err))
        return
    print("Service worker file updated.")


# Return url to versioned url of service worker is exist.
# Otherwise return url to not versioned file.
def sw_url():
    try:
        app = create_app()
        with app.app_context():
            with open(path.join(current_app.static_folder, "cache_manifest.json"), "r") as json_file:
                data = json.load(json_file)
                versioned_rel_url = data.get("general/scripts/service_worker.js")
                if versioned_rel_url:
                    return "/" + path.basename(versioned_rel_url)
                return "/service_worker.js"
    except Exception:
        return "/service_worker.js"


def fetch_subscribed():
    anime_dic = {}

    # Wbijam
    for sub in current_user.wbijam_sub:
        if sub.wbijam.anime.title not in anime_dic:
            anime_dic[sub.wbijam.anime.title] = {"anime_content": sub.wbijam.anime}

        title_dic = anime_dic[sub.wbijam.anime.title]

        if "is_wbijam_sub" not in title_dic:
            title_dic["is_wbijam_sub"] = True
        
    # Anime-odcinki
    for sub in current_user.anime_odcinki_sub:
        if sub.anime_odcinki.anime.title not in anime_dic:
            anime_dic[sub.anime_odcinki.anime.title] = {"anime_content": sub.anime_odcinki.anime}

        title_dic = anime_dic[sub.anime_odcinki.anime.title]

        if "is_anime_odcinki_sub" not in title_dic:
            title_dic["is_anime_odcinki_sub"] = True
 
    # Okami-subs
    for sub in current_user.okami_subs_sub:
        if sub.okami_subs.anime.title not in anime_dic:
            anime_dic[sub.okami_subs.anime.title] = {"anime_content": sub.okami_subs.anime}

        title_dic = anime_dic[sub.okami_subs.anime.title]

        if "is_okami_subs_sub" not in title_dic:
            title_dic["is_okami_subs_sub"] = True

    # Animesub
    for sub in current_user.animesub_sub:
        if sub.animesub.anime.title not in anime_dic:
            anime_dic[sub.animesub.anime.title] = {"anime_content": sub.animesub.anime}

        title_dic = anime_dic[sub.animesub.anime.title]

        if "animesub" not in title_dic:
            title_dic["animesub"] = {"subscribed_authors": [], "not_subscribed_authors": []}
        subscribed_authors = title_dic["animesub"]["subscribed_authors"]
        subscribed_authors.append(sub.animesub)

    # Animesub forum
    for sub in current_user.animesub_forum_sub:
        if sub.animesub_forum.anime.title not in anime_dic:
            anime_dic[sub.animesub_forum.anime.title] = {"anime_content": sub.animesub_forum.anime}

        title_dic = anime_dic[sub.animesub_forum.anime.title]

        if "animesub_forum" not in title_dic:
            title_dic["animesub_forum"] = {"subscribed_authors": [], "not_subscribed_authors": []}
        subscribed_authors = title_dic["animesub_forum"]["subscribed_authors"]
        subscribed_authors.append(sub.animesub_forum)


    # Not subscribed things added to dic only if title_dic for title exist.
    # Wbijam
    wbijam_list = Wbijam.query.all()
    for wbijam in wbijam_list:
        if wbijam.anime.title in anime_dic:
            title_dic = anime_dic[wbijam.anime.title]

            if "is_wbijam_sub" not in title_dic:
                title_dic["is_wbijam_sub"] = False

    # Anime-odcinki
    anime_odcinki_list = Anime_odcinki.query.all()
    for anime_odcinki in anime_odcinki_list:
        if anime_odcinki.anime.title in anime_dic:
            title_dic = anime_dic[anime_odcinki.anime.title]

            if "is_anime_odcinki_sub" not in title_dic:
                title_dic["is_anime_odcinki_sub"] = False


    # Okami-subs
    okami_subs_list = Okami_subs.query.all()
    for okami_subs in okami_subs_list:
        if okami_subs.anime.title in anime_dic:
            title_dic = anime_dic[okami_subs.anime.title]

            if "is_okami_subs_sub" not in title_dic:
                title_dic["is_okami_subs_sub"] = False

    # Animesub
    animesub_list = Animesub.query.all()
    for animesub in animesub_list:
        if animesub.anime.title in anime_dic:
            title_dic = anime_dic[animesub.anime.title]

            if "animesub" not in title_dic:
                title_dic["animesub"] = {"subscribed_authors": [], "not_subscribed_authors": []}

            subscribed_authors = anime_dic[animesub.anime.title]["animesub"]["subscribed_authors"]
            not_subscribed_authors = anime_dic[animesub.anime.title]["animesub"]["not_subscribed_authors"]

            if animesub not in subscribed_authors:
                not_subscribed_authors.append(animesub)

    # Animesub forum
    animesub_forum_list = Animesub_forum.query.all()
    for animesub_forum in animesub_forum_list:
        if animesub_forum.anime.title in anime_dic:
            title_dic = anime_dic[animesub_forum.anime.title]

            if "animesub_forum" not in title_dic:
                title_dic["animesub_forum"] = {"subscribed_authors": [], "not_subscribed_authors": []}

            subscribed_authors = anime_dic[animesub_forum.anime.title]["animesub_forum"]["subscribed_authors"]
            not_subscribed_authors = anime_dic[animesub_forum.anime.title]["animesub_forum"]["not_subscribed_authors"]

            if animesub_forum not in subscribed_authors:
                not_subscribed_authors.append(animesub_forum)

    anime_dic = OrderedDict(sorted(anime_dic.items()))

    return anime_dic  


def fetch_not_subscribed():
    subscribed = []
    not_subscribed = []
    all_anime = Anime.query.order_by(Anime.title)


    for sub in current_user.wbijam_sub:
        if sub.wbijam.anime not in subscribed:
            subscribed.append(sub.wbijam.anime)

    for sub in current_user.anime_odcinki_sub:
        if sub.anime_odcinki.anime not in subscribed:
            subscribed.append(sub.anime_odcinki.anime)

    for sub in current_user.okami_subs_sub:
        if sub.okami_subs.anime not in subscribed:
            subscribed.append(sub.okami_subs.anime)

    for sub in current_user.animesub_sub:
        if sub.animesub.anime not in subscribed:
            subscribed.append(sub.animesub.anime)

    for sub in current_user.animesub_forum_sub:
        if sub.animesub_forum.anime not in subscribed:
            subscribed.append(sub.animesub_forum.anime)

    for anime in all_anime:
        if anime not in subscribed:
            not_subscribed.append(anime)

    not_subscribed.sort(key=lambda a: a.title)

    return not_subscribed

# Used in subscribed page
def split_by_seasons_dic(anime_dic):
    ordered_seasons = {}

    for season in Season.query.order_by(Season.order):
        ordered_seasons[(season.season_id, season.season)] = {}
    
    for title, title_dic in anime_dic.items():
        ordered_seasons[(title_dic["anime_content"].season.season_id, title_dic["anime_content"].season.season)][title] = title_dic

    return ordered_seasons


# Used in add subscription page and page for editing anime
def split_by_seasons_list(anime_list):

    ordered_seasons = {}

    for season in Season.query.order_by(Season.order):
        ordered_seasons[(season.season_id, season.season)] = []
    
    for anime in anime_list:
        ordered_seasons[(anime.season.season_id, anime.season.season)].append(anime)

    return ordered_seasons


def save_subs(edit_form, request_form):
    # Global_anime_ep
    global_ep = Global_anime_ep.query.filter_by(
        user=current_user, anime_id=edit_form.anime_id.data
    ).first()
    # Animesub
    ansi_checked_authors = request_form.getlist("animesub_authors")
    title_ansi_records = (
        Animesub.query.outerjoin(
            Animesub_sub,
            and_(
                Animesub.animesub_id == Animesub_sub.animesub_id,
                Animesub_sub.user_id == current_user.id,
            ),
        )
        .options(contains_eager(Animesub.animesub_sub))
        .filter(Animesub.anime_id == edit_form.anime_id.data)
        .all()
    )

    for animesub in title_ansi_records:
        if (
            animesub.animesub_sub
            and str(animesub.animesub_id) not in ansi_checked_authors
        ):
            db.session.delete(animesub.animesub_sub[0])

        elif (
            animesub.animesub_sub == []
            and str(animesub.animesub_id) in ansi_checked_authors
        ):
            animesub_sub = Animesub_sub(
                user=current_user, animesub_id=animesub.animesub_id
            )
            db.session.add(animesub_sub)       

    # Animesub forum
    ansiforum_checked_authors = request_form.getlist("animesub_forum_authors")
    title_ansiforum_records = (
        Animesub_forum.query.outerjoin(
            Animesub_forum_sub,
            and_(
                Animesub_forum.animesub_forum_id
                == Animesub_forum_sub.animesub_forum_id,
                Animesub_forum_sub.user_id == current_user.id,
            ),
        )
        .options(contains_eager(Animesub_forum.animesub_forum_sub))
        .filter(Animesub_forum.anime_id == edit_form.anime_id.data)
        .all()
    )

    for animesub_forum in title_ansiforum_records:
        if (
            animesub_forum.animesub_forum_sub
            and str(animesub_forum.animesub_forum_id) not in ansiforum_checked_authors
        ):
            db.session.delete(animesub_forum.animesub_forum_sub[0])  

        elif (
            animesub_forum.animesub_forum_sub == []
            and str(animesub_forum.animesub_forum_id) in ansiforum_checked_authors
        ):
            animesub_forum_sub = Animesub_forum_sub(
                user=current_user, animesub_forum_id=animesub_forum.animesub_forum_id
            )
            db.session.add(animesub_forum_sub)

    # Wbijam
    wbijam_sub = Wbijam_sub.query.filter_by(
        user=current_user, anime_id=edit_form.anime_id.data
    ).first()
    if wbijam_sub and edit_form.wbijam_sub.data is False:
        db.session.delete(wbijam_sub)

    elif wbijam_sub is None and edit_form.wbijam_sub.data:
        wbijam_sub = Wbijam_sub(user=current_user, anime_id=edit_form.anime_id.data)
        db.session.add(wbijam_sub)

    # Anime-odcinki
    anime_odcinki_sub = Anime_odcinki_sub.query.filter_by(
        user=current_user, anime_id=edit_form.anime_id.data
    ).first()
    if anime_odcinki_sub and edit_form.anime_odcinki_sub.data is False:
        db.session.delete(anime_odcinki_sub)

    elif anime_odcinki_sub is None and edit_form.anime_odcinki_sub.data:
        anime_odcinki_sub = Anime_odcinki_sub(
            user=current_user, anime_id=edit_form.anime_id.data
        )
        db.session.add(anime_odcinki_sub)

    # Okami-subs
    okami_subs_sub = Okami_subs_sub.query.filter_by(
        user=current_user, anime_id=edit_form.anime_id.data
    ).first()
    if okami_subs_sub and edit_form.okami_subs_sub.data is False:
        db.session.delete(okami_subs_sub)

    elif okami_subs_sub is None and edit_form.okami_subs_sub.data:
        okami_subs_sub = Okami_subs_sub(
            user=current_user, anime_id=edit_form.anime_id.data
        )
        db.session.add(okami_subs_sub)

    # Adding global_ep
    if not global_ep and (
        ansi_checked_authors
        or ansiforum_checked_authors
        or edit_form.wbijam_sub.data
        or edit_form.anime_odcinki_sub.data
        or edit_form.okami_subs_sub.data
    ):
        new_global_ep = Global_anime_ep(
            user=current_user, anime_id=edit_form.anime_id.data
        )
        db.session.add(new_global_ep)
    # Deleting global_ep
    if (
        global_ep
        and not ansi_checked_authors
        and not ansiforum_checked_authors
        and not edit_form.wbijam_sub.data
        and not edit_form.anime_odcinki_sub.data
        and not edit_form.okami_subs_sub.data
    ):
        db.session.delete(global_ep)
    try:
        db.session.commit()
    except Exception as err:
        current_app.logger.error(
            "Tried to update subscription state in db.\n" + str(err)
        )
        db.session.rollback()
        return {"isSuccess": False, "errorMsg": "Wystąpił błąd podczas aktualizacji subskrypcji. Spróbuj ponownie."}

    return {"isSuccess": True}
    #return {"isSuccess": False, "errorMsg": "Wystąpił błąd podczas aktualizacji subskrypcji. Spróbuj ponownie."}