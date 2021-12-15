from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SubmitField


class EditSubscriptions(FlaskForm):
    anime_id = IntegerField()
    wbijam_sub = BooleanField()
    anime_odcinki_sub = BooleanField()
    okami_subs_sub = BooleanField()
    submit = SubmitField("Zatwierdź")