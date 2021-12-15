from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.html5 import URLField, IntegerField
from wtforms.validators import DataRequired, ValidationError, URL, InputRequired, Optional
from animechecker.models import Anime, Wbijam, Anime_odcinki, Okami_subs, Animesub_forum


class AddAnimeForm(FlaskForm):
    title = StringField("Tytuł", validators=[DataRequired()])
    season = SelectField("Sezon", choices=[], coerce=int, default=-1)
    mal_link = URLField("Mal URL", validators=[DataRequired(), URL()])
    cover_link = URLField("Okładka URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Dodaj")

    def validate_title(self, title):
        anime = Anime.query.filter_by(title=title.data).first()
        if anime:
            raise ValidationError("Ten tytuł jest już w bazie.")

    def validate_mal_link(self, mal_link):
        anime = Anime.query.filter_by(mal_link=mal_link.data).first()
        if anime:
            raise ValidationError("Ten link jest już w bazie.")    

    def validate_season(self, season):
        if season.data == -1:
            raise ValidationError("Nie wybrałeś sezonu.")


class EditAnimeTitleForm(FlaskForm):
    title = StringField("Tytuł", validators=[DataRequired()])
    season = SelectField("Sezon", choices=[], coerce=int, default=-1)
    mal_link = URLField("Mal URL", validators=[DataRequired(), URL()])
    cover_link = URLField("Okładka URL", validators=[URL(), Optional()])
    anime_id = IntegerField("Id")
    submit = SubmitField("Zatwierdź")

    def validate_title(self, new_title):
        anime = Anime.query.filter_by(title=new_title.data).first()
        if anime:
            if anime.anime_id != self.anime_id.data:
                raise ValidationError("Ten tytuł jest już w bazie.")

    def validate_mal_link(self, new_mal_link):
        anime = Anime.query.filter_by(mal_link=new_mal_link.data).first()
        if anime:
            if anime.anime_id != self.anime_id.data:
                raise ValidationError("Ten link jest już w bazie.")


class AnimeSearchForm(FlaskForm):
    search = StringField("Wyszukiwanie", validators=[DataRequired()])
    submitsearch = SubmitField("Szukaj")


class AddWbijamForm(FlaskForm):
    title = SelectField("Tytuł", choices=[], coerce=int, default=-1)
    title_in_site = StringField("Tytuł na stronie", validators=[DataRequired()])
    source_link = URLField("URL", validators=[DataRequired(), URL()])
    cr_numbering_diff = IntegerField("Różnica w numerowaniu CR", default=0, validators=[InputRequired()])
    cr_diff_title = StringField("Tytuł bez podziału (opcjonalne)")
    submit = SubmitField("Dodaj")

    def validate_title_in_site(self, title_in_site):
        wbijam = Wbijam.query.filter_by(title_in_site=title_in_site.data).first()
        if wbijam:
            raise ValidationError("Ten tytuł jest już w bazie.")    

    def validate_title(self, title):
        if title.data == -1:
            raise ValidationError("Nie wybrałeś anime.")

    def validate_cr_diff_title(self, cr_diff_title):
        if cr_diff_title.data and self.cr_numbering_diff.data == 0:
            raise ValidationError('Wypełnij tylko w wypadku różnicy w numeracji.')
        if not cr_diff_title.data and self.cr_numbering_diff.data != 0:
            raise ValidationError('Należy wypełnić jeśli wybrałeś inna numerację.')


class EditWbijamForm(FlaskForm):
    source_link = URLField("URL", validators=[DataRequired(), URL()])
    title_in_site = StringField("Tytuł na stronie", validators=[DataRequired()])
    cr_numbering_diff = IntegerField("Cr diff", default=0, validators=[InputRequired()])
    cr_diff_title = StringField("Tytuł bez podziału (opcjonalne)")
    anime_id = IntegerField("Id")
    submit = SubmitField("Zatwierdź")

    def validate_title_in_site(self, new_title_in_site):
        wbijam = Wbijam.query.filter_by(title_in_site=new_title_in_site.data).first()
        if wbijam:
            if wbijam.anime_id != self.anime_id.data:
                raise ValidationError("Ten tytuł jest już w bazie.")    

    def validate_cr_diff_title(self, cr_diff_title):
        if cr_diff_title.data and self.cr_numbering_diff.data == 0:
            raise ValidationError('Wypełnij tylko w wypadku różnicy w numeracji.')
        if not cr_diff_title.data and self.cr_numbering_diff.data != 0:
            raise ValidationError('Należy wypełnić jeśli wybrałeś inna numerację.')                


class AddAoForm(FlaskForm):
    title = SelectField("Tytuł", choices=[], coerce=int, default=-1)
    source_link = URLField("URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Dodaj")

    def validate_source_link(self, source_link):
        anime_odcinki = Anime_odcinki.query.filter_by(source_link=source_link.data).first()
        if anime_odcinki:
            raise ValidationError("Ten link jest już w bazie.")

    def validate_title(self, title):
        if title.data == -1:
            raise ValidationError("Nie wybrałeś anime.")


class EditAoForm(FlaskForm):
    source_link = URLField("URL", validators=[DataRequired(), URL()])
    anime_id = IntegerField("Id")
    submit = SubmitField("Zatwierdź")

    def validate_source_link(self, new_source_link):
        anime_odcinki = Anime_odcinki.query.filter_by(source_link=new_source_link.data).first()
        if anime_odcinki:
            if anime_odcinki.anime_id != self.anime_id.data:
                raise ValidationError("Ten link jest już w bazie.")


class AddOkamiSubsForm(FlaskForm):
    title = SelectField("Tytuł", choices=[], coerce=int, default=-1)
    title_in_site = StringField("Tytuł na stronie", validators=[DataRequired()])
    season_page_link = URLField("Podstrona z sezonem", validators=[DataRequired(), URL()])
    submit = SubmitField("Dodaj")

    def validate_title_in_site(self, title_in_site):
        okami_subs = Okami_subs.query.filter_by(title_in_site=title_in_site.data).first()
        if okami_subs:
            raise ValidationError("Ten tytuł jest już w bazie.")
 
    def validate_title(self, title):
        if title.data == -1:
            raise ValidationError("Nie wybrałeś anime.")


class EditOkamiSubsForm(FlaskForm):
    title_in_site = StringField("Tytuł na stronie", validators=[DataRequired()])
    season_page_link = URLField("URL", validators=[DataRequired(), URL()])
    anime_id = IntegerField("Id")
    submit = SubmitField("Zatwierdź")

    def validate_title_in_site(self, new_title_in_site):
        okami_subs = Okami_subs.query.filter_by(title_in_site=new_title_in_site.data).first()
        if okami_subs:
            if okami_subs.anime_id != self.anime_id.data:
                raise ValidationError("Ten tytuł jest już w bazie.")


class AddAnimesubForm(FlaskForm):
    title = SelectField("Tytuł", choices=[], coerce=int, default=-1)
    ansi_title = StringField("Tytuł na stronie", validators=[DataRequired()])
    author = StringField("Autor", validators=[DataRequired()])
    cr_numbering_diff = IntegerField("Różnica w numerowaniu CR", default=0, validators=[InputRequired()])
    cr_diff_title = StringField("Tytuł bez podziału (opcjonalne)")
    submit = SubmitField("Dodaj")

    def validate_title(self, title):
        if title.data == -1:
            raise ValidationError("Nie wybrałeś anime.")

    def validate_cr_diff_title(self, cr_diff_title):
        if cr_diff_title.data and self.cr_numbering_diff.data == 0:
            raise ValidationError('Wypełnij tylko w wypadku różnicy w numeracji.')
        if not cr_diff_title.data and self.cr_numbering_diff.data != 0:
            raise ValidationError('Należy wypełnić jeśli wybrałeś inna numerację.')          


class EditAnimesubForm(FlaskForm):
    animesub_id = IntegerField("Id")
    ansi_title = StringField("Tytuł na stronie", validators=[DataRequired()])
    author = StringField("Autor", validators=[DataRequired()])
    cr_numbering_diff = IntegerField("Cr diff", default=0, validators=[InputRequired()])
    cr_diff_title = StringField("Tytuł bez podziału (opcjonalne)")
    submit = SubmitField("Zatwierdź")

    def validate_cr_diff_title(self, cr_diff_title):
        if cr_diff_title.data and self.cr_numbering_diff.data == 0:
            raise ValidationError('Wypełnij tylko w wypadku różnicy w numeracji.')
        if not cr_diff_title.data and self.cr_numbering_diff.data != 0:
            raise ValidationError('Należy wypełnić jeśli wybrałeś inna numerację.')   


class AddAnimesubForumForm(FlaskForm):
    title = SelectField("Tytuł", choices=[], coerce=int, default=-1)
    author = StringField("Autor", validators=[DataRequired()])
    source_link = URLField("URL", validators=[DataRequired(), URL()])
    cr_numbering_diff = IntegerField("Różnica w numerowaniu CR", default=0, validators=[InputRequired()])
    cr_diff_title = StringField("Tytuł bez podziału (opcjonalne)")
    submit = SubmitField("Dodaj")

    def validate_source_link(self, source_link):
        animesub_forum = Animesub_forum.query.filter_by(source_link=source_link.data).first()
        if animesub_forum:
            raise ValidationError("Ten link jest już w bazie.")

    def validate_title(self, title):
        if title.data == -1:
            raise ValidationError("Nie wybrałeś anime.")

    def validate_cr_diff_title(self, cr_diff_title):
        if cr_diff_title.data and self.cr_numbering_diff.data == 0:
            raise ValidationError('Wypełnij tylko w wypadku różnicy w numeracji.')
        if not cr_diff_title.data and self.cr_numbering_diff.data != 0:
            raise ValidationError('Należy wypełnić jeśli wybrałeś inna numerację.')


class EditAnimesubForumForm(FlaskForm):
    animesub_forum_id = IntegerField("Id")
    author = StringField("Autor", validators=[DataRequired()])
    source_link = URLField("URL", validators=[DataRequired(), URL()])
    cr_numbering_diff = IntegerField("Cr diff", default=0, validators=[InputRequired()])
    cr_diff_title = StringField("Tytuł bez podziału (opcjonalne)")
    submit = SubmitField("Zatwierdź")

    def validate_source_link(self, new_source_link):
        animesub_forum = Animesub_forum.query.filter_by(source_link=new_source_link.data).first()
        if animesub_forum:
            if animesub_forum.animesub_forum_id != self.animesub_forum_id.data:
                raise ValidationError("Ten tytuł jest już w bazie.")

    def validate_cr_diff_title(self, cr_diff_title):
        if cr_diff_title.data and self.cr_numbering_diff.data == 0:
            raise ValidationError('Wypełnij tylko w wypadku różnicy w numeracji.')
        if not cr_diff_title.data and self.cr_numbering_diff.data != 0:
            raise ValidationError('Należy wypełnić jeśli wybrałeś inna numerację.')
