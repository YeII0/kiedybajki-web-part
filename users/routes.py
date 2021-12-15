from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    request,
    Blueprint,
    current_app,
    jsonify,
)
from flask_login import login_user, current_user, logout_user, login_required
from animechecker import db, bcrypt
from animechecker.models import User
from animechecker.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountInfoForm,
    UpdateAccountSettingsForm,
    RequestResetForm,
    ResetPasswordForm,
    RequestActivationForm,
)
from animechecker.users.utils import send_reset_email, send_activation_email

users_bp = Blueprint(
    "users_bp",
    __name__,
    template_folder="templates",
)

# Function for testing headers
# @users_bp.after_request
# def add_header(response):
#     response.headers["Content-Security-Policy-Report-Only"] = (
#         "default-src 'self';" +
#         "style-src 'self' fonts.googleapis.com 'sha256-pmA5UyNQbnAh5Vx3qzNijUiGOrraeNaSqMCetBZx9So=';" +
#         "font-src fonts.gstatic.com"
#         )
#     return response

@users_bp.route("/register", methods=["GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.subscriptions"))
    return render_template(
        "register.html", title="Kiedy Bajki | Rejestracja", form=RegistrationForm()
    )


@users_bp.route("/register_submit", methods=["POST"])
def register_submit():
    response = {"isSuccess": False}
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            password=hashed_password,
        )
        db.session.add(user)
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to add new User record to db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {
                "msg": "Wystąpił błąd podczas rejestracji. Spróbuj ponownie.",
                "type": "error",
            }
        else:
            flash(
                "Twoje konto zostało utworzono. Link aktywacyjny został wysłany na podanego emaila.",
                "info",
            )
            db.session.refresh(user)
            send_activation_email(user)

            response["isSuccess"] = True
            response["redirectUrl"] = url_for("users_bp.login")
    else:
        response["errors"] = form.errors
    return jsonify(response)


@users_bp.route("/", methods=["GET"])
@users_bp.route("/login", methods=["GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.subscriptions"))
    return render_template(
        "login.html", title="Kiedy Bajki | Logowanie", form=LoginForm()
    )


@users_bp.route("/login_submit", methods=["POST"])
def login_submit():
    response = {"isSuccess": False}
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.confirmed is False:
                alert_msg = f"""Przed zalogowaniem należy aktywować konto korzystając z linku aktywacyjnego wysłanego na emaila. 
                            Jeżeli go nie otrzymałeś kliknij <a href="{url_for("users_bp.activation_request")}">tutaj</a> aby wysłać go ponownie."""
                response["alert"] = {"msg": alert_msg, "type": "warning"}
            else:
                response["isSuccess"] = True
                login_user(user, remember=form.remember.data)
                next_page = request.args.get("next")
                if next_page:
                    response["redirectUrl"] = next_page
                else:
                    response["redirectUrl"] = url_for("main_bp.subscriptions")
        else:
            alert_msg = ("Logowanie nie powiodło się. Sprawdź czy podane hasło i email są prawidłowe.")
            response["alert"] = {"msg": alert_msg, "type": "error"}
    else:
        response["errors"] = form.errors
    return jsonify(response)


@users_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("users_bp.login"))


@users_bp.route("/account", methods=["GET"])
@login_required
def account():
    form_account_info = UpdateAccountInfoForm()
    form_account_settings = UpdateAccountSettingsForm()

    form_account_info.username.data = current_user.username
    form_account_info.email.data = current_user.email
    form_account_settings.webhook.data = current_user.webhook
    form_account_settings.are_modules_independent.data = (
        current_user.are_modules_independent
    )
    form_account_settings.is_db_entry_notification.data = current_user.is_db_entry_notification
    form_account_settings.extra_webhook.data = current_user.extra_webhook

    return render_template(
        "account.html",
        title="Kiedy Bajki | Konto",
        form_account_info=form_account_info,
        form_account_settings=form_account_settings,
    )


@users_bp.route("/account_info_submit", methods=["POST"])
@login_required
def account_info_submit():
    response = {"isSuccess": False}
    form_account_info = UpdateAccountInfoForm()
    if form_account_info.validate_on_submit():
        current_user.username = form_account_info.username.data
        current_user.email = form_account_info.email.data.lower()
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error("Tried to update User record in db.\n" + str(err))
            db.session.rollback()
            response["alert"] = {
                "msg": "Wystąpił błąd podczas aktualizacji informacji o koncie. Spróbuj ponownie.",
                "type": "error",
            }
        else:
            response["alert"] = {
                "msg": "Zaktualizowano dane.",
                "type": "info",
            }
            response["isSuccess"] = True
    else:
        response["errors"] = form_account_info.errors
    return jsonify(response)


@users_bp.route("/account_settings_submit", methods=["POST"])
@login_required
def account_settings_submit():
    response = {"isSuccess": False}
    form_account_settings = UpdateAccountSettingsForm()
    if form_account_settings.validate_on_submit():
        current_user.webhook = form_account_settings.webhook.data
        current_user.are_modules_independent = (
            form_account_settings.are_modules_independent.data
        )
        current_user.is_db_entry_notification = form_account_settings.is_db_entry_notification.data
        # We don't want save empty strings because it can violate unique constraint.
        if form_account_settings.extra_webhook.data:
            current_user.extra_webhook = form_account_settings.extra_webhook.data
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error(
                "Tried to update User record in db.\n" + str(err)
            )
            db.session.rollback()
            response["alert"] = {
                "msg": "Wystąpił błąd podczas aktualizacji ustawień konta. Spróbuj ponownie.",
                "type": "error",
            }            
        else:
            response["isSuccess"] = True
            response["alert"] = {
                "msg": "Zaktualizowano ustawienia.",
                "type": "info",
            }
    else:
        response["errors"] = form_account_settings.errors
    return jsonify(response)


@users_bp.route("/reset_password", methods=["GET"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.subscriptions"))
    return render_template(
        "reset_request.html", title="Kiedy Bajki | Resetowanie hasła", form=RequestResetForm()
    )


@users_bp.route("/reset_password_submit", methods=["POST"])
def reset_request_submit():
    response = {"isSuccess": False}
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("Link do zresetowania hasła został wysłany na emaila.", "info")
        response["isSuccess"] = True
        response["redirectUrl"] = url_for("users_bp.login")
    else:
        response["errors"] = form.errors
    return jsonify(response) 


@users_bp.route("/reset_password/<token>", methods=["GET"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.subscriptions"))
    user = User.verify_token(token)
    if user is None:
        flash(
            "Link do resetowania hasła jest nieprawidłowy lub stracił ważność.", "error"
        )
        return redirect(url_for("users_bp.reset_request"))
    return render_template(
        "reset_token.html", title="Kiedy Bajki | Resetowanie hasła", form=ResetPasswordForm(), token=token
    )


@users_bp.route("/new_password/<token>", methods=["POST"])
def new_password_submit(token):
    response = {"isSuccess": False}
    form = ResetPasswordForm()
    user = User.verify_token(token)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user.password = hashed_password
        try:
            db.session.commit()
        except Exception as err:
            current_app.logger.error(
                "Tried to update User password in db.\n" + str(err)
            )
            db.session.rollback()
            response["alert"] = {"msg": "Wystąpił błąd podczas próby aktualizacji hasła. Spróbuj ponownie.", "type": "error"}
        else:
            response["isSuccess"] = True
            response["redirectUrl"] = url_for("users_bp.login")
            flash(
                "Twoje hasło zostało zaktualizowane. Teraz możesz się zalogować.",
                "info",
            )
    else:
        response["errors"] = form.errors
    return jsonify(response)



@users_bp.route("/activate_account/<token>", methods=["GET", "POST"])
def confirm_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.subscriptions"))
    user = User.verify_token(token)
    if user is None:
        flash("Link do aktywacji konta jest nieprawidłowy lub stracił ważność.", "info")
        return redirect(url_for("users_bp.activation_request"))
    user.confirmed = True
    try:
        db.session.commit()
    except Exception as err:
        current_app.logger.error(
            "Tried to change User status to confirmed in db.\n" + str(err)
        )
        db.session.rollback()
        flash(
            "Wystąpił błąd podczas aktywacji konta. Użyj linku aktywacyjnego ponownie.",
            "error",
        )
    else:
        flash("Twoje konto jest już aktywne. Teraz możesz się zalogować.", "info")
    return redirect(url_for("users_bp.login"))


@users_bp.route("/activate_account", methods=["GET"])
def activation_request():
    if current_user.is_authenticated:
        return redirect(url_for("main_bp.subscriptions"))
    return render_template(
        "activation_request.html", title="Kiedy Bajki | Resetowanie hasła", form=RequestActivationForm()
    )


@users_bp.route("/activation_request_submit", methods=["POST"])
def activation_request_submit():
    form = RequestActivationForm()
    response = {"isSuccess": False}
    if form.validate_on_submit():
        response["isSuccess"] = True
        user = User.query.filter_by(email=form.email.data).first()
        if user.confirmed is True:
            flash("Konto z podanym emailem jest już aktywne.", "info")
        else:
            send_activation_email(user)
            flash("Link aktywacyjny został wysłany na emaila.", "info")
        response["redirectUrl"] = url_for("users_bp.login")
    else:
        response["errors"] = form.errors
    return jsonify(response)
