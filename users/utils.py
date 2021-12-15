from os import environ
from flask import url_for
from flask_mail import Message
from animechecker import mail


def send_reset_email(user):
    token = user.get_token()
    msg = Message(
        "Resetowanie hasła", sender=("Kiedy Bajki", environ.get("GMAIL_USER")),
        recipients=[user.email]
    )

    message_body = f"""
<h2 style="
    padding: 16px 32px;
    margin: 0 0 16px 0;
    background: #272b2e; 
    font-size: 24px;">
    Resetowanie hasła
</h2>
<p style="margin: 0 0 16px 0; padding: 0 32px"> 
    Aby zresetować hasło kliknij
    <a style="color:#7cb9ff; text-decoration: none;" href="{url_for('users_bp.reset_token', token=token, _external=True)}">
    tutaj</a>.
    Jeżeli to nie ty wysłałeś żądanie zmiany hasła to zignoruj tę wiadomość.        
</p>
"""
    msg.html = mail_template(message_body)
    mail.send(msg)


def send_activation_email(user):
    token = user.get_token()
    msg = Message(
        "Aktywacja konta", sender=("Kiedy Bajki", environ.get("GMAIL_USER")),
        recipients=[user.email]
    )

    message_body = f"""
<h2 style="
    padding: 16px 32px;
    margin: 0 0 16px 0;
    background: #272b2e; 
    font-size: 24px;">
    Aktywacja konta
</h2>
<p style="margin: 0 0 16px 0; padding: 0 32px"> 
    Aby aktywować konto kliknij 
    <a style="color:#7cb9ff; text-decoration: none;" href="{url_for('users_bp.confirm_token', token=token, _external=True)}">
    tutaj</a>. 
    Jeżeli to nie ty wysłałeś żądanie zmiany hasła to zignoruj tę wiadomość.
</p>
<h2 style="
    padding: 16px 32px;
    margin: 0 0 16px 0;
    background: #272b2e; 
    font-size: 24px;">
    Pierwsze kroki
</h2>
<p style="margin: 0 0 16px 0; padding: 0 32px"> 
    O tym jak skonfigurować aplikację, jak z niej korzystać oraz o najczęstszych problemach
    możesz poczytać 
    <a style="color:#7cb9ff; text-decoration: none;" href="{url_for('main_bp.about', _external=True)}">
    tutaj</a>.
</p>
"""

    msg.html = mail_template(message_body)
    mail.send(msg)


def mail_template(message_body):
    message = f"""
<table style="font-size: 16px; color: #cfcfcf; max-width: 600px; border-collapse: collapse; background-color: #2f3437;"
    cellspacing="0" cellpadding="0" width="100%" bgcolor="#2f3437" border="0">
    <tbody>

    <tr>
        <td style="padding: 32px; background-color: #272b2e;">
            <img alt="Kiedy Bajki" src="https://images2.imgbox.com/09/f9/40ey9tGp_o.png"/>
        </td>
    </tr>

    <tr>
        <td style="padding: 32px 0">
            {message_body}
            <h2 style="
                padding: 16px 32px;
                margin: 0 0 16px 0;
                background: #272b2e; 
                font-size: 24px;">
                Kontakt
            </h2>
            <p style="margin: 0 0 16px 0; padding: 0 32px"> 
                Masz pytania związane z aplikacją? 
                <a style="color:#7cb9ff; text-decoration: none;" href="https://discord.gg/7QFMp44">Dołącz</a> 
                do mojego discorda i napisz na kanale <em>#pytańska</em> lub
                w prywatnej wiadomości, nick Yello#8637.  
                Na discordzie będę zamieszczał informacje o znanych mi problemach, 
                błędach aplikacji i przerwach technicznych.
                Jeżeli coś będzie nie halo, zajrzyj na <em>#problemy-techniczne</em>, 
                <em>#znane-błędy</em>, <em>#zgłoś-błąd</em>.
                Zapraszam też osoby, które chcą po prostu sobie pobajdzurzyć o ryżowych opowieściach. 
            </p>        
        </td>
    </tr>                                       

    </tbody>
</table>
"""

    return message