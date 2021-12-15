import requests
from flask import current_app
from urllib.parse import urlparse
from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField, URLField
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    URL,
    Optional,
)
from flask_login import current_user
from animechecker.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Użytkownik",
        validators=[
            DataRequired(),
            Length(min=2, max=20, message="Pole musi zawierać od 2 do 20 znaków."),
        ],
    )
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
        ],
    )
    password = PasswordField(
        "Hasło",
        validators=[
            DataRequired(),
            Length(min=5, message="Pole musi zawierać co najmniej 5 znaków."),
        ],
    )
    confirm_password = PasswordField(
        "Potwierdź hasło",
        validators=[
            DataRequired(),
            EqualTo("password", message="Hasła się nie zgadzają."),
        ],
    )
    submit = SubmitField("Zarejestruj")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Ta nazwa użytkownika jest już zajęta.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError("Ten email jest już zajęty.")


class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
        ],
    )
    password = PasswordField(
        "Hasło", validators=[DataRequired()]
    )
    remember = BooleanField("Zapamiętaj mnie")
    submit = SubmitField("Zaloguj")


class UpdateAccountInfoForm(FlaskForm):
    username = StringField(
        "Użytkownik",
        validators=[
            DataRequired(),
            Length(min=2, max=20, message="Pole musi zawierać od 2 do 20 znaków."),
        ],
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
        ],
    )

    submit = SubmitField("Zaktualizuj")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Ta nazwa użytkownika jest już zajęta.")

    def validate_email(self, email):
        if email.data.lower() != current_user.email:
            user = User.query.filter_by(email=email.data.lower()).first()
            if user:
                raise ValidationError("Ten email jest już zajęty.")


class UpdateAccountSettingsForm(FlaskForm):
    webhook = URLField(
        "Discord webhook",
        validators=[
            DataRequired(),
            URL(),
        ],
    )
    are_modules_independent = BooleanField(
        "Niezależne powiadomienia dla każdej strony z anime"
    )
    is_db_entry_notification = BooleanField("Powiadomienia o nowych tytułach dodanych do bazy")
    extra_webhook = URLField("Dodatkowy discord webhook (opcjonalnie)", validators=[Optional(), URL()])
    submit = SubmitField("Zaktualizuj")


    def validate_webhook(self, webhook):
        if webhook.data and webhook.data == self.extra_webhook.data:
            raise ValidationError("Główny i dodatkowy webhook nie mogą być takie same.")  

        # Checks if webhook is not used already by other user
        if webhook.data != current_user.webhook:
            user = User.query.filter((User.webhook == webhook.data) | (User.extra_webhook == webhook.data)).first()
            if user and user != current_user:
                raise ValidationError(
                    "Ten webhook jest już w użyciu. Wybierz inny lub wygeneruj nowy."
                )

        # Out of the box validator are executed first. There is no reason in this case to process validation further
        # if DataREquired() or URL() validator raise error.
        if webhook.errors:
            return
        authorize_webhook(webhook, True)


    def validate_extra_webhook(self, extra_webhook):

        if extra_webhook.data and extra_webhook.data == self.webhook.data:
            raise ValidationError("Główny i dodatkowy webhook nie mogą być takie same.")  

        # Checks if webhook is not used already by other user
        if extra_webhook.data != current_user.extra_webhook:
            user = User.query.filter((User.webhook == extra_webhook.data) | (User.extra_webhook == extra_webhook.data)).first()
            if user and user != current_user:
                raise ValidationError(
                    "Ten webhook jest już w użyciu. Wybierz inny lub wygeneruj nowy."
                )

        # Out of the box validator are executed first. There is no reason in this case to process validation further
        # if DataREquired() or URL() validator raise error.
        if extra_webhook.errors:
            return
        
        authorize_webhook(extra_webhook, False)        


def authorize_webhook(webhook, is_main_webhook):
    """
    Authorize given webhook through discord server. 
    Raise ValidationError if something will goes wrong through this process otherwise no output is provided.
    Used in validation webhook custom validators
    param1 webhook: input field which contains webhook.
    """
    # There is a possibility that webhook will be removed by user in discord. So 404 NOT FOUND code will be send in response.
    # In that case we want to inform user that provided webhook don't exist anymore.

    if is_main_webhook:
        if current_user.webhook and webhook.data == current_user.webhook:
            check_if_webhook_not_removed(webhook)
            return
    else:
        if current_user.extra_webhook and webhook.data == current_user.extra_webhook:
            check_if_webhook_not_removed(webhook)
            return

    # Validation which takes place when new webhook is provided by user.
    ############################################################################

    val_error_msg = "Nieprawidłowy URL."
    try:
        parsed_webhook = urlparse(webhook.data)
    except:
        raise ValidationError(val_error_msg)

    # Webhook should start like here in startswith method and shouldn't contain URL params to prevent abuse
    # by using wait=true param
    if not webhook.data.startswith("https://discord.com/api/webhooks/") or parsed_webhook.query:
        raise ValidationError(val_error_msg)

    # We adding here query param ?wait=true to validate webhook by checking response json provided by this param.
    try:
        r = requests.post(webhook.data + '?wait=true', json={"embeds": [{"description": "Wprowadzony w formularzu webhook jest poprawny. Jeżeli formularz zmiany ustawień został wypełniony prawidłowo webhook zostanie dodany do aplikacji."}]})
    except (requests.ConnectionError, requests.HTTPError, requests.Timeout):
        raise ValidationError("Wystąpił problem połączenia się z serwerem discord w celu weryfikacji webhooka. Spróbuj później.")
    except Exception as err:
        current_app.logger.error("Error occurs while webhook autorization. Error throwed by requests.post() method.\n" + str(err))
        raise ValidationError("Wystąpił błąd podczas próby autoryzacji webhooka, spróbuj później." + 
        " Jeżeli błąd będzie się powtarzał skontaktuj się z administratorem.")
    try:
        r.raise_for_status()
    except:
        raise ValidationError(val_error_msg)

    # Checking response json which contain information about webhook and sended message.
    # If data in json response is correct it means that webhook is okey.
    try:
        json_response = r.json()
    except Exception:
        raise ValidationError(val_error_msg)
    if "webhook_id" not in json_response:
        raise ValidationError(val_error_msg)
    if json_response["webhook_id"] not in parsed_webhook.path:
        raise ValidationError(val_error_msg)

def check_if_webhook_not_removed(webhook):
    try:
        r = requests.get(webhook.data)
    except (requests.ConnectionError, requests.HTTPError, requests.Timeout):
        raise ValidationError("Wystąpił problem połączenia się z serwerem discord w celu weryfikacji webhooka. Spróbuj później.")
    except Exception as err:
        current_app.logger.error("Error occurs while webhook autorization. Error throwed by requests.post() method.\n" + str(err))
        raise ValidationError("Wystąpił błąd podczas próby autoryzacji webhooka, spróbuj później." + 
        " Jeżeli błąd będzie się powtarzał skontaktuj się z administratorem.")
    # This code means that resource location doesn't exist.
    if r.status_code == 404:
        raise ValidationError("Webhook już nie istnieje. Należy podać nowego webhooka.")          


class RequestResetForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
        ],
    )
    submit = SubmitField("Wyślij link do zmiany hasła")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Konto z podanym emailem nie istnieje.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Hasło",
        validators=[
            DataRequired(),
            Length(min=5, message="Pole musi zawierać co najmniej 5 znaków."),
        ],
    )
    confirm_password = PasswordField(
        "Potwierdź hasło",
        validators=[
            DataRequired(),
            EqualTo("password", message="Hasła się nie zgadzają."),
        ],
    )
    submit = SubmitField("Zmień hasło")


class RequestActivationForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
        ],
    )
    submit = SubmitField("Wyślij link aktywacyjny")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("Konto z podanym emailem nie istnieje.")
