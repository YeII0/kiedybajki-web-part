from datetime import datetime
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from animechecker import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    registered_on = db.Column(db.Date, nullable=True, default=datetime.now())
    last_login_on = db.Column(db.Date, nullable=True)
    webhook = db.Column(db.String(200), unique=True)
    extra_webhook = db.Column(db.String(200), unique=True)
    is_db_entry_notification = db.Column(db.Boolean, nullable=False, default=False)
    is_saw_news = db.Column(db.Boolean, nullable=False, default=False)
    are_modules_independent = db.Column(db.Boolean, nullable=False, default=False)

    def get_token(self, expires_sec=1800):
        s = Serializer(current_app.config["SECRET_KEY"], expires_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Anime(db.Model):
    anime_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    mal_link = db.Column(db.Text, unique=True, nullable=False)
    cover_rel_url = db.Column(db.Text, nullable=True)

    season_id = db.Column(db.Integer, db.ForeignKey("season.season_id", ondelete="CASCADE"), nullable=False)

    season = db.relationship(
        "Season",
        backref=db.backref("anime", passive_deletes=True, uselist=False),
        lazy=True)


    def __repr__(self):
        return f"Anime('{self.title}')"


class Season(db.Model):
    season_id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.String(150), unique=True, nullable=False)
    order = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f"Season('Title: {self.title}, Order: {self.order}')"    


class Wbijam(db.Model):
    anime_id = db.Column(
        db.Integer,
        db.ForeignKey("anime.anime_id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_link = db.Column(db.Text, nullable=False)
    title_in_site = db.Column(db.String(150), unique=True, nullable=False)    
    cr_numbering_diff = db.Column(db.Integer(), nullable=False, default=0)
    cr_diff_title = db.Column(db.String(150), nullable=True)
    
    is_notification_sended = db.Column(db.Boolean, nullable=False, default=False)

    anime = db.relationship(
        "Anime",
        backref=db.backref("wbijam", passive_deletes=True, uselist=False),
        lazy=True,
    )

    def __repr__(self):
        return f"Wbijam('{self.anime_id}, {self.source_link}')"


class Wbijam_sub(db.Model):
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    anime_id = db.Column(
        db.Integer,
        db.ForeignKey("wbijam.anime_id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_ep_num = db.Column(db.Integer, nullable=True)

    user = db.relationship(
        "User", backref=db.backref("wbijam_sub", passive_deletes=True), lazy=True
    )
    wbijam = db.relationship(
        "Wbijam", backref=db.backref("wbijam_sub", passive_deletes=True), lazy=True
    )

    def __repr__(self):
        return f"Wbijam_sub('{self.user_id}, {self.anime_id}')"


class Anime_odcinki(db.Model):
    anime_id = db.Column(
        db.Integer,
        db.ForeignKey("anime.anime_id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_link = db.Column(db.Text, unique=True, nullable=False)
    is_notification_sended = db.Column(db.Boolean, nullable=False, default=False)

    anime = db.relationship(
        "Anime",
        backref=db.backref("anime_odcinki", passive_deletes=True, uselist=False),
        lazy=True,
    )

    def __repr__(self):
        return f"Anime_odcinki('{self.anime_id}, {self.source_link}')"


class Anime_odcinki_sub(db.Model):
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    anime_id = db.Column(
        db.Integer,
        db.ForeignKey("anime_odcinki.anime_id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_ep_num = db.Column(db.Integer, nullable=True)

    user = db.relationship(
        "User", backref=db.backref("anime_odcinki_sub", passive_deletes=True), lazy=True
    )
    anime_odcinki = db.relationship(
        "Anime_odcinki",
        backref=db.backref("anime_odcinki_sub", passive_deletes=True),
        lazy=True,
    )

    def __repr__(self):
        return f"Wbijam_sub('{self.user_id}, {self.anime_id}')"


class Okami_subs(db.Model):
    anime_id = db.Column(
        db.Integer,
        db.ForeignKey("anime.anime_id", ondelete="CASCADE"),
        primary_key=True,
    )
    title_in_site = db.Column(db.String(150), unique=True, nullable=False)
    season_page_link = db.Column(db.Text, nullable=False)
    is_notification_sended = db.Column(db.Boolean, nullable=False, default=False)

    anime = db.relationship(
        "Anime",
        backref=db.backref("okami_subs", passive_deletes=True, uselist=False),
        lazy=True,
    )

    def __repr__(self):
        return f"Okami_subs('{self.anime_id}, {self.title_in_site}')"


class Okami_subs_sub(db.Model):
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    anime_id = db.Column(
        db.Integer,
        db.ForeignKey("okami_subs.anime_id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_ep_num = db.Column(db.Integer, nullable=True)

    user = db.relationship(
        "User", backref=db.backref("okami_subs_sub", passive_deletes=True), lazy=True
    )
    okami_subs = db.relationship(
        "Okami_subs",
        backref=db.backref("okami_subs_sub", passive_deletes=True),
        lazy=True,
    )

    def __repr__(self):
        return f"Okami_subs_sub('{self.user_id}, {self.anime_id}')"


class Animesub(db.Model):
    animesub_id = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(
        db.Integer, db.ForeignKey("anime.anime_id", ondelete="CASCADE"), nullable=False
    )
    author = db.Column(db.String(50), nullable=False)
    ansi_title = db.Column(db.String(150), nullable=False)
    cr_numbering_diff = db.Column(db.Integer(), nullable=False, default=0)
    cr_diff_title = db.Column(db.String(150), nullable=True)
    is_notification_sended = db.Column(db.Boolean, nullable=False, default=False)
    __table_args__ = (db.UniqueConstraint("anime_id", "author"),)

    anime = db.relationship(
        "Anime", backref=db.backref("animesub", passive_deletes=True), lazy=True
    )

    def __repr__(self):
        return f"Animesub('{self.author}', '{self.ansi_title}')"


class Animesub_sub(db.Model):
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    animesub_id = db.Column(
        db.Integer,
        db.ForeignKey("animesub.animesub_id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_ep_num = db.Column(db.Integer, nullable=True)
    user = db.relationship(
        "User", backref=db.backref("animesub_sub", passive_deletes=True), lazy=True
    )
    animesub = db.relationship(
        "Animesub", backref=db.backref("animesub_sub", passive_deletes=True), lazy=True
    )

    def __repr__(self):
        return f"Animesub_sub('{self.user_id}, {self.anime_id}')"


class Animesub_forum(db.Model):
    animesub_forum_id = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(
        db.Integer, db.ForeignKey("anime.anime_id", ondelete="CASCADE"), nullable=False
    )
    author = db.Column(db.String(50), nullable=False)
    source_link = db.Column(db.Text, unique=True, nullable=False)
    cr_numbering_diff = db.Column(db.Integer(), nullable=False, default=0)
    cr_diff_title = db.Column(db.String(150), nullable=True)
    is_notification_sended = db.Column(db.Boolean, nullable=False, default=False)
    __table_args__ = (db.UniqueConstraint("anime_id", "author"),)

    anime = db.relationship(
        "Anime", backref=db.backref("animesub_forum", passive_deletes=True), lazy=True
    )

    def __repr__(self):
        return f"Animesub_forum('{self.author}', '{self.anime_id}')"


class Animesub_forum_sub(db.Model):
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    animesub_forum_id = db.Column(
        db.Integer,
        db.ForeignKey("animesub_forum.animesub_forum_id", ondelete="CASCADE"),
        primary_key=True,
    )
    last_ep_num = db.Column(db.Integer, nullable=True)

    user = db.relationship(
        "User",
        backref=db.backref("animesub_forum_sub", passive_deletes=True),
        lazy=True,
    )
    animesub_forum = db.relationship(
        "Animesub_forum",
        backref=db.backref("animesub_forum_sub", passive_deletes=True),
        lazy=True,
    )

    def __repr__(self):
        return f"Animesub_forum_sub('{self.user_id}, {self.anime_id}')"


class Global_anime_ep(db.Model):
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    anime_id = db.Column(
        db.Integer,
        db.ForeignKey("anime.anime_id", ondelete="CASCADE"),
        primary_key=True,
    )
    global_last_ep_num = db.Column(db.Integer, nullable=True)

    user = db.relationship(
        "User", backref=db.backref("global_anime_ep", passive_deletes=True), lazy=True
    )
    anime = db.relationship(
        "Anime", backref=db.backref("global_anime_ep", passive_deletes=True), lazy=True
    )

    def __repr__(self):
        return f"Global_anime_ep('{self.user_id}, {self.anime_id}')"
