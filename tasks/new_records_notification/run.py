from time import sleep, time
import logging
import logging.config
import os
import requests
from os import path
from urllib.parse import urljoin
from flask import request
from animechecker import db
from animechecker.models import (
    User,
    Anime,
    Wbijam,
    Okami_subs,
    Anime_odcinki,
    Animesub,
    Animesub_forum,
)


def run():
    """Background task which sends notification about new titles added to db to users which select to be notified."""
    wbijam_records = Wbijam.query.filter_by(is_notification_sended=False).join(Wbijam.anime).order_by(Anime.title).all()
    okami_subs_records = Okami_subs.query.filter_by(is_notification_sended=False).join(Okami_subs.anime).order_by(Anime.title).all()
    anime_odcinki_records = Anime_odcinki.query.filter_by(is_notification_sended=False).join(Anime_odcinki.anime).order_by(Anime.title).all()
    animesub_records = Animesub.query.filter_by(is_notification_sended=False).join(Animesub.anime).order_by(Anime.title).all()
    animesub_forum_records = Animesub_forum.query.filter_by(is_notification_sended=False).join(Animesub_forum.anime).order_by(Anime.title).all()

    for user in User.query.filter_by(is_db_entry_notification=True):
        # Wbijam
        state = send_notifications(
            user,            
            wbijam_records,
            WBIJAM_SITE_NAME,
            WBIJAM_EMBED_COLOR,
        )
        if state == "stop_task":
            break
        if state == "skip_user":
            continue        

        # Okami_subs
        state = send_notifications(
            user,          
            okami_subs_records,
            OKAMI_SUBS_SITE_NAME,
            OKAMI_SUBS_EMBED_COLOR,
        )   
        if state == "stop_task":
            break
        if state == "skip_user":
            continue              
       
        # Anime_odcinki
        state = send_notifications(
            user,          
            anime_odcinki_records,
            AO_SITE_NAME,
            AO_EMBED_COLOR,
        )
        if state == "stop_task":
            break
        if state == "skip_user":
            continue

        # Animesub
        state = send_notifications(
            user,
            animesub_records,
            ANSI_SITE_NAME,
            ANSI_EMBED_COLOR,
            showAuthor=True,
            )
        if state == "stop_task":
            break
        if state == "skip_user":
            continue     

        # Animesub_forum
        state = send_notifications(
            user,            
            animesub_forum_records,
            ANSI_FORUM_SITE_NAME,
            ANSI_FORUM_EMBED_COLOR,
            showAuthor=True,
        ) 
        if state == "stop_task":
            break
        if state == "skip_user":
            continue        
    
    # Settings module records to sended state.
    for record in wbijam_records:
        record.is_notification_sended = True
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            logger.error("Tried update state module records state is_notification_sended to True\n%s", str(err))        
    for record in anime_odcinki_records:
        record.is_notification_sended = True
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            logger.error("Tried update state module records state is_notification_sended to True\n%s", str(err))         
    for record in okami_subs_records:
        record.is_notification_sended = True
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            logger.error("Tried update state module records state is_notification_sended to True\n%s", str(err))         
    for record in animesub_records:
        record.is_notification_sended = True
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            logger.error("Tried update state module records state is_notification_sended to True\n%s", str(err))         
    for record in animesub_forum_records:
        record.is_notification_sended = True
        try:
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            logger.error("Tried update state module records state is_notification_sended to True\n%s", str(err))
    


def send_notifications(user, records, site_name, embed_color, showAuthor=False):
    """
    Method handle sending notifications through discord and updating db accordingly. It sends given records from one module
    to given in params user.

    Arguments
    ---------
    user : animechecker.models.User
        User to which notification will be sended. 
        It should be user which have value of is_db_entry_notification is True.
    records : flask_sqlalchemy.BaseQuery
        Records from one module about which user should be notified.
        Should contain only records which value of is_notification_sended is False.
    site_name : str
        Site name which will be visible in discord message.
    embed_color : str
        Color of discord embed. Every module should have different embed color.
    show_author : bool, optional
        Set to True for module which contain author name. 
        With that discord notificatian will contain author name.

    Returns
    -------
    "continue_task" : str
        Indicates that task should be continued.
    "stop_task" : str
        Indicates that task should be stopped.
    "skip_user" : str
        Indicates that task should skip current user to the next one. 
    """

    if not records:
        return "continue_task"

    embeds = []
    # When embeds array contain embed objects with same url (mal link), only one from them is sended.
    # For example when we have few authors for one title. 
    # To prevent this behaviour we add query param to url.
    query_param_value = 0
    for record in records:
        query_param_value += 1
        embed = {
            "author": {"name": site_name},
            "title": record.anime.title,
            "color": embed_color,
            "url": record.anime.mal_link + "?kiedybajki=" + str(query_param_value),
        }
        if record.anime.cover_rel_url:
            embed["thumbnail"] = {"url": urljoin("https://kiedybajki.moe/static/", record.anime.cover_rel_url)}
        if showAuthor:
            author = record.author.replace("_", r"\_")
            embed["description"] = "Autor: " + author
        embeds.append(embed)
        
    # Split embeds list when is higher than 10, cuz 10 embeds is max limit for webhooks.
    if len(embeds) > 10:
        loopTimes = len(embeds) // 10
        endRange = loopTimes * 10
        for i in range(0, endRange, 10):
            state = send_embeds(user, embeds[i: i + 10])
            if state == "skip_user":
                return "skip_user"
            if state == "stop_task":
                return "stop_task"
                
        remainsNumber = len(embeds) % 10
        if remainsNumber != 0:
            startRange = (len(embeds) // 10) * 10
            state = send_embeds(user, embeds[startRange:])
            if state == "skip_user":
                return "skip_user"
            if state == "stop_task":
                return "stop_task"     
    else:
        state = send_embeds(user, embeds)
        if state == "skip_user":
            return "skip_user"
        if state == "stop_task":
            return "stop_task"
    return "continue_task"


def send_embeds(user, embeds):
    """
    Helper function used in send_notifications function. 
    Send chunk of embeds (10 is max) in one request through given webhook and update user when needed. 
    It also handle all errors related to sending request.

    Arguments
    ---------
    user: animechecker.models.User
        When user webhook used to send notification will be invalid it will be removed from user.
        extra_webhook have precedence, if not exist webhook will be used.
    embeds: List
        Embeds which will be sended through HTTP POST request to discord webhook.

    Returns
    -------
    "continue_task" : str
        Indicates that task should be continued.
    "stop_task" : str
        Indicates that task should be stopped.
    "skip_user" : str
        Indicates that task should skip current user to the next one.     
    """

    if user.extra_webhook:
        isMainWebhook = False
        webhook = user.extra_webhook
    elif user.webhook:
        isMainWebhook = True
        webhook = user.webhook
    else:
        return "skip_user"   

    while True:                              
        payload = {"embeds": embeds}
        try:
            r = requests.post(webhook, json=payload)
        except (requests.ConnectionError, requests.HTTPError, requests.Timeout):
            sleep(4)
            continue
        except Exception as err:
            logger.error("Serious problem occurs while trying to send webhook message. Need to investigate!\n%s", str(err))
            return "stop_task"

        # Settings rate limits from headers
        if r.headers.get("X-RateLimit-Remaining"):
            rate_limit_remaining = int(r.headers.get("X-RateLimit-Remaining"))
        else:
            rate_limit_remaining = None
        # This don't work when 429 occurs. Use it only for success responses.
        if r.headers.get("X-RateLimit-Reset"):
            limit_reset_after = int(r.headers.get("X-RateLimit-Reset")) - time()
            if limit_reset_after < 0:
                limit_reset_after = 0
        else:
            limit_reset_after = None

        # Checking status code and take actions which depends on which code occurs.
        try:
            r.raise_for_status()
        except Exception as err:
            if r.status_code == 429:
                # 429 response contains json with retry_after value which can be different (longer)
                # than time to wait from X-RateLimit-Reset header.
                # This is propably a discord bug and X-RateLimit-Reset should also have proper value.      
                sleep(int(r.json()["retry_after"]) / 1000)
                continue
            # When any from this code range occurs webhook will be deleted from db cuz
            # it will means that is invalid due from removing or other reasons
            if r.status_code >= 401 and r.status_code <= 404:
                if isMainWebhook:
                    user.webhook = None
                else:
                    user.extra_webhook = None
                try:
                    db.session.commit()
                except Exception as err:
                    db.session.rollback()
                    logger.error("Tried to delete Anime record to db.\n%s", str(err))
                return "skip_user"
            # If other error status_code occurs we want save it in logs.
            logger.error(
                "Http status code different that 429 and 401-404 occurs."
                " In that case task will be stopped. If problem occurs continually investigation will be needed.\n%s"
                , str(err)
            )
            return "stop_task"

        if rate_limit_remaining == 0:
            sleep(limit_reset_after) 
        break
    return "continue_task"


def init_logger():
    if not path.isdir(path.join(path.dirname(path.realpath(__file__)), "logs")):
        os.mkdir(path.join(path.dirname(path.realpath(__file__)), "logs"))
    return logging.getLogger("new_records_notification_task")


logger = init_logger()   

# Modules constants 
############################################################################

WBIJAM_SITE_NAME = "Wbijam.pl"
WBIJAM_EMBED_COLOR = "14408667"

OKAMI_SUBS_SITE_NAME = "Okami-subs.pl"
OKAMI_SUBS_EMBED_COLOR = "16720161"

AO_SITE_NAME = "Anime-odcinki.pl"
AO_EMBED_COLOR = "4364533"

ANSI_SITE_NAME = "Animesub.info"
ANSI_EMBED_COLOR = "10027008"

ANSI_FORUM_SITE_NAME = "Forum animesub.info"
ANSI_FORUM_EMBED_COLOR = "8896300"

